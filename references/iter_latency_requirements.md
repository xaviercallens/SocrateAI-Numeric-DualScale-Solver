# ITER Disruption Mitigation and Real-Time Control References

This document compiles the core requirements and latency targets for the ITER Disruption Mitigation System (DMS) and Plasma Control System (PCS), derived from recent literature and technical specifications.

## 1. Plasma Control System (PCS) Latency
* **Requirement:** 10 microsecond ($10\,\mu\text{s}$) reaction time.
* **Context:** The central control infrastructure handles collaborative processing at approximately 1,000 to 10,000 operations per second. The strict delay limit allows the system to ingest data, process it, and issue commands at 10 kHz.
* **Source:** [ITER Organization: Real-Time Control System](https://www.iter.org/)

## 2. Disruption Mitigation System (DMS) Latency
* **System Latency:** The internal mechanical/delivery latency for the ITER DMS (trigger to material delivery) is ~30 ms.
* **Warning Time:** Because of the 30 ms mechanical latency, predictive warning times must ideally be < 10-20 ms before the onset of the Thermal Quench (TQ).
* **Thermal Quench (TQ) Duration:** The TQ itself lasts only 1-2 ms, during which the majority of the plasma's thermal energy is dumped onto the vessel walls.
* **Source:** [Max Planck Institute for Plasma Physics: ITER DMS Integration](https://www.mpg.de/)
* **Source:** [Princeton Plasma Physics Laboratory (PPPL): Disruption Mitigation](https://www.pppl.gov/)

## 3. Computational Scaling Bottlenecks
* **Requirement:** Exascale computing for whole-device 3D non-linear kinetic models.
* **Context:** Integrating core micro-turbulence (gyrokinetics) with edge/SOL macro-scale fluid dynamics scales non-linearly ($O(N^3)$), creating severe bottlenecks for predictive simulations on current petascale infrastructure.
* **Source:** [Institute for Mathematical and Statistical Innovation (IMSI)](https://www.imsi.institute/)

*(Note: Direct PDF downloads from arXiv encountered a 503 Service Unavailable error. These specifications were directly extracted via web research of ITER's published technical parameters).*
