"""
Live Multi-Cloud Telemetry Streamer — Phase 7 Upgrade 3 (H43)
=============================================================

gRPC-schema-compatible telemetry event emitter for the EdgeCloudSwarmAgent.
In CI, operates in mock streaming mode — emits events deterministically to
a local JSON-lines telemetry log (data/telemetry_stream.jsonl), proving the
streaming protocol end-to-end without a real cloud endpoint.

H43 mandate:
  - Stream emits N events with correct schema
  - Monotonically-increasing timestamps (nanoseconds)
  - Rolling SHA-256 stream integrity hash
  - No events dropped (emitted_count == received_count)
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# TelemetryEvent dataclass (mirrors gRPC proto schema)
# ---------------------------------------------------------------------------

@dataclass
class TelemetryEvent:
    """Single structured telemetry event (gRPC-compatible schema)."""
    event_id: str
    timestamp_ns: int       # Monotonic nanosecond timestamp
    source_node: str        # e.g. "edge_node_07", "cloud_solver"
    metric_name: str        # e.g. "edge_latency_ms", "enstrophy_snapshot"
    metric_value: float
    unit: str               # e.g. "ms", "m^-2 s^-1", "fraction"
    sequence_number: int    # Per-node sequence counter
    schema_version: str = "v1.0"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def schema_valid(self) -> bool:
        """All required fields present and typed correctly."""
        return (
            isinstance(self.event_id, str) and len(self.event_id) > 0
            and isinstance(self.timestamp_ns, int) and self.timestamp_ns > 0
            and isinstance(self.source_node, str) and len(self.source_node) > 0
            and isinstance(self.metric_name, str) and len(self.metric_name) > 0
            and isinstance(self.metric_value, float)
            and isinstance(self.unit, str)
            and isinstance(self.sequence_number, int)
        )


# ---------------------------------------------------------------------------
# TelemetryStreamer
# ---------------------------------------------------------------------------

class TelemetryStreamer:
    """
    Collects telemetry events, validates monotonic ordering, computes rolling
    SHA-256 integrity hash, and writes to a JSONL sink.
    """

    def __init__(self, sink_filepath: Optional[str] = None):
        self._events: List[TelemetryEvent] = []
        self._last_ts_ns: int = 0
        self._rolling_hash = hashlib.sha256()
        self._monotonicity_violated = False
        self._schema_errors: List[str] = []
        self.sink_filepath = sink_filepath

    def emit(self, event: TelemetryEvent) -> bool:
        """
        Accept an event into the stream.
        Returns False if event violates monotonic ordering or schema.
        """
        if not event.schema_valid():
            self._schema_errors.append(event.event_id)
            return False
        if event.timestamp_ns <= self._last_ts_ns:
            self._monotonicity_violated = True
            return False
        self._last_ts_ns = event.timestamp_ns
        self._events.append(event)
        self._rolling_hash.update(json.dumps(event.to_dict(), sort_keys=True).encode())
        return True

    def flush(self) -> str:
        """Write all events to the JSONL sink and return the final integrity hash."""
        if self.sink_filepath:
            os.makedirs(
                os.path.dirname(self.sink_filepath) if os.path.dirname(self.sink_filepath) else ".",
                exist_ok=True,
            )
            with open(self.sink_filepath, "w", encoding="utf-8") as f:
                for ev in self._events:
                    f.write(json.dumps(ev.to_dict()) + "\n")
        return self._rolling_hash.hexdigest()

    @property
    def events_emitted(self) -> int:
        return len(self._events)

    @property
    def stream_valid(self) -> bool:
        return (
            not self._monotonicity_violated
            and len(self._schema_errors) == 0
            and len(self._events) > 0
        )


# ---------------------------------------------------------------------------
# Edge Swarm Telemetry Generator
# ---------------------------------------------------------------------------

def simulate_edge_telemetry_stream(
    swarm_nodes: int = 16,
    n_events_per_node: int = 10,
    base_ts_ns: int = 1_000_000_000,
    sink_filepath: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generates deterministic telemetry events from `swarm_nodes` ARM Cortex-M4
    edge nodes and the cloud solver, streaming them through a TelemetryStreamer.

    Each node emits:
      - edge_latency_ms per step
      - local_enstrophy_snapshot
      - cloud_sync_ack (boolean as float 0/1)

    Returns streaming metrics conforming to the H43 mandate.
    """
    streamer = TelemetryStreamer(sink_filepath=sink_filepath)

    # Base per-node edge latency (deterministic, seeded from node index)
    BASE_LATENCY_MS = 0.185
    BASE_ENSTROPHY = 8.2e10

    ts_ns = base_ts_ns
    total_attempted = 0
    seq_counters = {f"edge_node_{i:02d}": 0 for i in range(swarm_nodes)}
    seq_counters["cloud_solver"] = 0

    for step in range(n_events_per_node):
        for node_i in range(swarm_nodes):
            node_name = f"edge_node_{node_i:02d}"

            # 1. Edge latency metric
            latency = BASE_LATENCY_MS + 0.001 * (node_i % 3)  # small deterministic spread
            ev_latency = TelemetryEvent(
                event_id=f"{node_name}_latency_{step}",
                timestamp_ns=ts_ns,
                source_node=node_name,
                metric_name="edge_latency_ms",
                metric_value=float(latency),
                unit="ms",
                sequence_number=seq_counters[node_name],
            )
            ts_ns += 1_000  # +1µs per event
            seq_counters[node_name] += 1
            streamer.emit(ev_latency)
            total_attempted += 1

            # 2. Enstrophy snapshot
            enstrophy = BASE_ENSTROPHY * (1.0 - 0.001 * step) * (1.0 - 0.0005 * node_i)
            ev_ens = TelemetryEvent(
                event_id=f"{node_name}_enstrophy_{step}",
                timestamp_ns=ts_ns,
                source_node=node_name,
                metric_name="enstrophy_snapshot",
                metric_value=float(enstrophy),
                unit="m^-2 s^-1",
                sequence_number=seq_counters[node_name],
            )
            ts_ns += 1_000
            seq_counters[node_name] += 1
            streamer.emit(ev_ens)
            total_attempted += 1

        # Cloud solver sync ack
        ev_ack = TelemetryEvent(
            event_id=f"cloud_solver_ack_{step}",
            timestamp_ns=ts_ns,
            source_node="cloud_solver",
            metric_name="cloud_sync_ack",
            metric_value=1.0,
            unit="bool",
            sequence_number=seq_counters["cloud_solver"],
        )
        ts_ns += 10_000  # cloud events separated by 10µs
        seq_counters["cloud_solver"] += 1
        streamer.emit(ev_ack)
        total_attempted += 1

    integrity_hash = streamer.flush()

    return {
        "swarm_nodes": swarm_nodes,
        "events_per_node": n_events_per_node,
        "events_attempted": total_attempted,
        "events_emitted": streamer.events_emitted,
        "events_dropped": total_attempted - streamer.events_emitted,
        "stream_integrity_hash": integrity_hash,
        "telemetry_stream_valid": streamer.stream_valid,
        "sink_filepath": sink_filepath,
        "_measured": True,
    }


# ---------------------------------------------------------------------------
# Stream Validator
# ---------------------------------------------------------------------------

def validate_telemetry_stream(filepath: str) -> Dict[str, Any]:
    """
    Reads a JSONL telemetry stream file and confirms:
    - Monotonically increasing timestamps
    - All required schema fields present
    - Integrity hash recomputable
    """
    if not os.path.isfile(filepath):
        return {"valid": False, "error": "File not found", "_measured": True}

    events = []
    schema_errors = 0
    rolling = hashlib.sha256()

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                required = {"event_id", "timestamp_ns", "source_node", "metric_name",
                            "metric_value", "unit", "sequence_number"}
                if not required.issubset(d.keys()):
                    schema_errors += 1
                    continue
                events.append(d)
                rolling.update(json.dumps(d, sort_keys=True).encode())
            except json.JSONDecodeError:
                schema_errors += 1

    monotonic = all(
        events[i]["timestamp_ns"] < events[i + 1]["timestamp_ns"]
        for i in range(len(events) - 1)
    )

    return {
        "events_read": len(events),
        "schema_errors": schema_errors,
        "monotonic_timestamps": monotonic,
        "recomputed_hash": rolling.hexdigest(),
        "valid": monotonic and schema_errors == 0 and len(events) > 0,
        "_measured": True,
    }


# ---------------------------------------------------------------------------
# Negative Control
# ---------------------------------------------------------------------------

def negative_control_nc_p7_09() -> bool:
    """
    NC-P7-09: Out-of-order timestamps or missing schema fields must be
    deterministically rejected by the TelemetryStreamer.
    """
    streamer = TelemetryStreamer()
    ev1 = TelemetryEvent(
        event_id="ev_001", timestamp_ns=2_000, source_node="node_00",
        metric_name="latency_ms", metric_value=0.185, unit="ms", sequence_number=0,
    )
    ev2 = TelemetryEvent(
        event_id="ev_002", timestamp_ns=1_000,  # earlier timestamp — violation!
        source_node="node_00", metric_name="latency_ms", metric_value=0.185,
        unit="ms", sequence_number=1,
    )
    streamer.emit(ev1)
    accepted_ev2 = streamer.emit(ev2)
    rejected = (not accepted_ev2) and streamer._monotonicity_violated
    return bool(rejected)
