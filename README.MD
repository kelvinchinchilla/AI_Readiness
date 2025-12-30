# INGEK AI-Readiness Assessment Engine

![Stress Test Report](INGEK_StressTest_Report.png)
*(Example output: Dual-axis analysis showing the exact breaking point of a Tier III electrical branch under AI load)*

## 🚀 Overview
The **INGEK AI-Readiness Assessment Engine** is a specialized Python-based simulation tool designed to validate legacy Data Center infrastructure against the extreme power and thermal demands of modern High-Performance Computing (HPC) workloads, specifically **NVIDIA H100/Blackwell GPU clusters**.

Unlike static Excel calculations, this engine utilizes a **Newton-Raphson Power Flow Analysis** (via `pandapower`) to create a Digital Twin of the electrical topology. It performs iterative stress testing to identify the precise "Safe Operating Area" (SOA) before physical deployment.

## ⚙️ Key Capabilities
* **Digital Twin Modeling:** Simulates Grid $\to$ Transformer $\to$ PDU topology.
* **Iterative Stress Testing:** Injects synthetic AI loads in 20kW increments to find failure points.
* **Failure Detection:** Monitors critical constraints dynamically:
    * **Thermal Saturation:** Transformer & Cable loading > 98%.
    * **Voltage Instability:** Bus voltage drops below ANSI C84.1 limits (< 0.95 p.u.).
* **Visual Reporting:** Generates executive-grade dual-axis charts for decision-making.

## 🛠️ Technology Stack
* **Python 3.10+**
* **Pandapower:** For electric power system analysis.
* **Matplotlib:** For data visualization and reporting.
* **Pandas:** For telemetry logging and data manipulation.

## 📋 Methodology
The engine follows a strict validation logic:
1.  **Ingestion:** Defines network parameters (Voltage levels, impedance, cable lengths).
2.  **Simulation:** Loops through load scenarios (0% to 120% of design capacity).
3.  **Analysis:** Calculates power flow convergence and checks physical limits at each step.
4.  **Output:** Returns a Pass/Fail verdict and a visual capacity map.

## ⚠️ Disclaimer
**For Feasibility Studies Only.** This software is a simulation tool intended to guide capacity planning and risk assessment. Final electrical design and implementation must be verified by a certified Professional Engineer (PE) in accordance with local codes (NEC/IEC) and safety standards.

---
**Developed by [Your Name]** *Manager & Lead Consultant @ INGEK* *Power Engineering 4.0 Division*