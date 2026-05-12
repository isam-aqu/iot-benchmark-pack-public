## R106 – Wi-Fi Baseline with Ethernet Logger (W1_wifi_near_quiet_v6)

### Motivation
Previous Wi-Fi baseline runs (R102–R105) showed heavy-tail latency and significant outliers.  
Hypothesis: The measurement system (laptop connected via Wi-Fi) introduced RF contention.

### Change Introduced
- Laptop connected via **Ethernet**
- Laptop **Wi-Fi disabled**

### Result
- Median RTT reduced to ~10.4 ms
- P95 reduced to ~15.9 ms
- Maximum RTT ~18 ms
- **No outliers observed**
- Fully stable distribution

### Key Insight
The previously observed Wi-Fi latency spikes were caused by **measurement-induced wireless contention**, not intrinsic Wi-Fi behavior.

### Impact
- Establishes **true Wi-Fi baseline performance**
- Invalidates earlier assumption of system-level instability
- Demonstrates importance of measurement setup in IoT latency experiments
