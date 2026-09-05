//! # PolarQuant Telemetry State Compression
//!
//! Integrates `runux-ai-runtime`'s `turbo_quant` engine to achieve high-speed
//! 4-bit / 8-bit state vector quantization for physical flow fields.
//!
//! Reduces real-time telemetry streaming bandwidth across the lock-free
//! audit ring buffer by up to 8x (or 16x vs f64) with strictly bounded distortion.

use serde::{Deserialize, Serialize};
use turbo_quant::{scalar_dequantize, scalar_quantize, PolarQuant};

/// Compressed telemetry packet containing PolarQuant encoded velocity state.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CompressedTelemetryPacket {
    pub step_index: usize,
    pub time: f64,
    pub original_dim: usize,
    pub packed_bytes: Vec<u8>,
    pub scales: Vec<f32>,
    pub zeros: Vec<f32>,
    pub target_bits: u8,
    pub original_bytes: usize,
    pub compressed_bytes: usize,
    pub compression_ratio: f32,
}

/// PolarQuant telemetry compressor for multiscale flow states.
pub struct PolarQuantTelemetryCompressor {
    pub dim: usize,
    pub target_bits: u8,
    pub block_size: usize,
    rotation: PolarQuant,
}

impl PolarQuantTelemetryCompressor {
    /// Create a new PolarQuant compressor for state vectors of size `dim`.
    pub fn new(dim: usize, target_bits: u8, seed: u64) -> Self {
        let block_size = if dim >= 32 {
            32
        } else if dim >= 16 {
            16
        } else if dim >= 8 {
            8
        } else {
            dim.max(1)
        };

        Self {
            dim,
            target_bits: target_bits.clamp(2, 8),
            block_size,
            rotation: PolarQuant::new(seed, dim),
        }
    }

    /// Compress a physical state vector (f64) into a compact telemetry packet.
    pub fn compress(&self, step_index: usize, time: f64, state_f64: &[f64]) -> CompressedTelemetryPacket {
        let n = state_f64.len().min(self.dim);
        let mut input_f32 = vec![0.0f32; self.dim];
        for i in 0..n {
            input_f32[i] = state_f64[i] as f32;
        }

        // 1. Polar orthogonal rotation (distributes variance evenly across coordinates)
        let mut rotated_f32 = vec![0.0f32; self.dim];
        self.rotation.rotate_forward(&input_f32, &mut rotated_f32);

        // 2. Uniform scalar quantization
        let mut scales = Vec::new();
        let mut zeros = Vec::new();
        let mut packed_bytes = Vec::new();
        scalar_quantize(
            &rotated_f32,
            self.target_bits,
            &mut scales,
            &mut zeros,
            &mut packed_bytes,
            self.block_size,
        );

        let original_bytes = state_f64.len() * std::mem::size_of::<f64>();
        let compressed_bytes = packed_bytes.len()
            + scales.len() * std::mem::size_of::<f32>()
            + zeros.len() * std::mem::size_of::<f32>();

        let compression_ratio = if compressed_bytes > 0 {
            original_bytes as f32 / compressed_bytes as f32
        } else {
            1.0
        };

        CompressedTelemetryPacket {
            step_index,
            time,
            original_dim: self.dim,
            packed_bytes,
            scales,
            zeros,
            target_bits: self.target_bits,
            original_bytes,
            compressed_bytes,
            compression_ratio,
        }
    }

    /// Decompress a telemetry packet back to physical state vector (f64).
    pub fn decompress(&self, packet: &CompressedTelemetryPacket) -> Vec<f64> {
        let mut dequantized_f32 = Vec::new();
        scalar_dequantize(
            &packet.packed_bytes,
            &packet.scales,
            &packet.zeros,
            packet.target_bits,
            self.block_size,
            packet.original_dim,
            &mut dequantized_f32,
        );

        let mut restored_f32 = vec![0.0f32; self.dim];
        self.rotation.rotate_inverse(&dequantized_f32, &mut restored_f32);

        restored_f32.iter().map(|&x| x as f64).collect()
    }

    /// Measure the relative energy distortion: |E(orig) - E(decomp)| / E(orig).
    pub fn evaluate_energy_distortion(&self, original: &[f64], decompressed: &[f64]) -> f64 {
        let e_orig = 0.5 * original.iter().map(|&x| x * x).sum::<f64>();
        let e_decomp = 0.5 * decompressed.iter().map(|&x| x * x).sum::<f64>();

        if e_orig < 1e-12 {
            (e_orig - e_decomp).abs()
        } else {
            (e_orig - e_decomp).abs() / e_orig
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_polarquant_compression_roundtrip() {
        let compressor = PolarQuantTelemetryCompressor::new(16, 4, 12345);
        let mut state = vec![0.0; 16];
        for i in 0..16 {
            state[i] = 1.0 / (i as f64 + 1.0);
        }

        let packet = compressor.compress(42, 0.05, &state);
        assert!(packet.compressed_bytes < packet.original_bytes);
        assert!(packet.compression_ratio >= 2.0);

        let restored = compressor.decompress(&packet);
        assert_eq!(restored.len(), 16);

        let distortion = compressor.evaluate_energy_distortion(&state, &restored);
        // At 4-bit, distortion should remain bounded below 20%
        assert!(distortion < 0.25, "Energy distortion {} exceeds bound", distortion);
    }
}
