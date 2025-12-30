"""
PROJECT: AI-Ready Infrastructure Capacity Engine
CLIENT: Internal / INGEK Proprietary Tool
DEVELOPER: Kelvin Chinchilla, Manager at INGEK
VERSION: 1.0.0 (Production)
DATE: 2025-12-28

DESCRIPTION:
This software creates a Digital Twin of a Data Center's electrical branch 
(Grid -> Transformer -> UPS -> PDU) to simulate high-density AI workload scenarios.
It performs iterative Power Flow Analysis (Newton-Raphson method) to determine 
the exact Breaking Point of the infrastructure based on thermal and voltage stability limits.

COPYRIGHT:
© 2025 INGEK. All rights reserved. 
Confidential and Proprietary.
"""

import pandapower as pp
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --- CONFIGURATION & CONSTANTS ---
GRID_VOLTAGE_KV = 13.8
MAIN_VOLTAGE_KV = 0.48
TRAFO_RATING_MVA = 2.5
CRITICAL_VOLTAGE_LIMIT_PU = 0.95  # ANSI Range A (-5%)
CRITICAL_LOADING_PERCENT = 98.0   # Safety Margin before overload
STEP_SIZE_KW = 20.0               # Incremental load step
MAX_SIMULATION_MW = 5.0           # Stop simulation if this load is reached

class AIInfrastuctureTwin:
    def __init__(self):
        self.net = pp.create_empty_network()
        self.results_log = []
        self._build_network()

    def _build_network(self):
        """Constructs the electrical topology of the Data Center branch."""
        # 1. Create Buses
        self.b_grid = pp.create_bus(self.net, vn_kv=GRID_VOLTAGE_KV, name="Utility Grid")
        self.b_main = pp.create_bus(self.net, vn_kv=MAIN_VOLTAGE_KV, name="Main Switchboard")
        self.b_pdu = pp.create_bus(self.net, vn_kv=MAIN_VOLTAGE_KV, name="AI High-Density Hall")

        # 2. External Grid Connection (Infinite Bus)
        pp.create_ext_grid(self.net, bus=self.b_grid, vm_pu=1.0, name="Grid Feed")

        # 3. Transformer (2.5 MVA | 13.8kV -> 480V | Z=6%)
        pp.create_transformer_from_parameters(
            self.net, hv_bus=self.b_grid, lv_bus=self.b_main,
            sn_mva=TRAFO_RATING_MVA, vn_hv_kv=GRID_VOLTAGE_KV, vn_lv_kv=MAIN_VOLTAGE_KV,
            vkr_percent=1.0, vk_percent=6.0, pfe_kw=5.0, i0_percent=0.1,
            name="Main Transformer T-1"
        )

        # 4. Cabling (Simulating 50m of heavy gauge feeder to the AI Hall)
        pp.create_line_from_parameters(
            self.net, from_bus=self.b_main, to_bus=self.b_pdu, length_km=0.05,
            r_ohm_per_km=0.06, x_ohm_per_km=0.03, c_nf_per_km=10, max_i_ka=3.5,
            name="Feeder Busway"
        )

        # 5. The AI Load (Initial State: 0 kW)
        self.load_id = pp.create_load(
            self.net, bus=self.b_pdu, p_mw=0.0, q_mvar=0.0, name="NVIDIA H100 Cluster"
        )

    def run_stress_test(self):
        """Executes the iterative load injection simulation."""
        print(f"\n--- INGEK AI-CAPACITY ENGINE INITIATED ---")
        print(f"Developer: [YOUR NAME], Manager at INGEK")
        print(f"Target: Determining maximum safe AI deployment capacity...\n")

        current_load_mw = 0.0
        step_mw = STEP_SIZE_KW / 1000.0
        is_safe = True

        while is_safe and current_load_mw <= MAX_SIMULATION_MW:
            # Update Load (Assuming PF = 0.95 lagging for modern PSUs)
            self.net.load.at[self.load_id, 'p_mw'] = current_load_mw
            self.net.load.at[self.load_id, 'q_mvar'] = current_load_mw * 0.329 

            try:
                pp.runpp(self.net)
            except pp.LoadflowNotConverged:
                print(f"CRITICAL: Grid Collapse (Divergence) at {current_load_mw*1000:.0f} kW")
                break

            # Capture Telemetry
            trafo_loading = self.net.res_trafo.loading_percent[0]
            voltage_pu = self.net.res_bus.vm_pu[self.b_pdu]
            
            # Log Data
            self.results_log.append({
                "Load_kW": current_load_mw * 1000,
                "Trafo_Load_Pct": trafo_loading,
                "Voltage_PU": voltage_pu
            })

            # Check Safety Constraints
            if trafo_loading >= CRITICAL_LOADING_PERCENT:
                print(f"(!) LIMIT REACHED: Transformer Overload ({trafo_loading:.1f}%) at {current_load_mw*1000:.0f} kW")
                is_safe = False
            elif voltage_pu <= CRITICAL_VOLTAGE_LIMIT_PU:
                print(f"(!) LIMIT REACHED: Voltage Drop Violation ({voltage_pu:.3f} pu) at {current_load_mw*1000:.0f} kW")
                is_safe = False
            else:
                current_load_mw += step_mw

        return pd.DataFrame(self.results_log)

    def generate_executive_report(self, df):
        """Generates a professional dual-axis plot for client presentation."""
        fig, ax1 = plt.subplots(figsize=(10, 6))
        
        # Plot 1: Transformer Loading (Left Axis)
        color = 'tab:blue'
        ax1.set_xlabel('AI Compute Load (kW)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Transformer Loading (%)', color=color, fontsize=12)
        ax1.plot(df['Load_kW'], df['Trafo_Load_Pct'], color=color, linewidth=2, label='Trafo Load')
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.axhline(y=100, color='red', linestyle='--', alpha=0.5, label='Max Capacity')

        # Plot 2: Voltage Stability (Right Axis)
        ax2 = ax1.twinx() 
        color = 'tab:green'
        ax2.set_ylabel('Voltage at Rack (p.u.)', color=color, fontsize=12)
        ax2.plot(df['Load_kW'], df['Voltage_PU'], color=color, linewidth=2, linestyle='-', label='Voltage')
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.axhline(y=0.95, color='orange', linestyle='--', alpha=0.5, label='Min Voltage (ANSI)')

        # Branding & Layout
        plt.title('INGEK AI-Readiness Assessment: Stress Test Results', fontsize=14, pad=20)
        fig.tight_layout()
        plt.grid(True, which='both', linestyle='--', alpha=0.7)
        
        # Save output
        filename = "INGEK_StressTest_Report.png"
        plt.savefig(filename, dpi=300)
        print(f"\n[SUCCESS] Executive Chart generated: {filename}")
        plt.show()

if __name__ == "__main__":
    engine = AIInfrastuctureTwin()
    results = engine.run_stress_test()
    engine.generate_executive_report(results)