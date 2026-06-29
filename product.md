# Product Context: KiCad Keyboard Automation Engine

## Target Audience & Intent
* **User Profile:** Hardware engineers and custom keyboard designers requiring low-latency layout generation without repetitive trace routing manual overhead.
* **Core Value Proposition:** Translates standard alphanumeric matrix layouts directly into perfectly placed, DRC-compliant, routed KiCad footprints, bypassing the manual switch-and-diode matrix layout lifecycle.

## High-Level Capabilities
1. **Algorithmic Grid Placement:** Auto-compute X/Y coordinates for switches, diodes, and bypass capacitors using parametric layout metadata.
2. **Component Abstraction Layer:** Handle mixed-type footprints natively (e.g., PTH vs. SMD 1N4148 diodes, MX-style hot-swap sockets vs. soldered pins).
3. **Automated Trace Routing Pipeline:** Programmatic interface to offload trace generation directly to high-throughput external routers (Rust $A^*$ or Quilter).
