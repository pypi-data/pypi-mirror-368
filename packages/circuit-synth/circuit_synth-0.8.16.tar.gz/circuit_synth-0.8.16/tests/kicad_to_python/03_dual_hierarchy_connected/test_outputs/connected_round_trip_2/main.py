#!/usr/bin/env python3
"""
Main circuit generated from KiCad
"""

from circuit_synth import *

@circuit(name='main')
def main():
    """
    Main circuit with hierarchical subcircuits
    """
    # Main circuit nets
    vin = Net('VIN')
    gnd = Net('GND')

    # Main circuit components
    r3 = Component(symbol="Device:R", ref="R3", value="10k", footprint="Resistor_SMD:R_0603_1608Metric")
    r2 = Component(symbol="Device:R", ref="R2", value="10k", footprint="Resistor_SMD:R_0603_1608Metric")
    r2 = Component(symbol="Device:R", ref="R2", value="10k", footprint="Resistor_SMD:R_0603_1608Metric")
    r2 = Component(symbol="Device:R", ref="R2", value="10k", footprint="Resistor_SMD:R_0603_1608Metric")
    r2 = Component(symbol="Device:R", ref="R2", value="10k", footprint="Resistor_SMD:R_0603_1608Metric")
    r2 = Component(symbol="Device:R", ref="R2", value="10k", footprint="Resistor_SMD:R_0603_1608Metric")
    r2 = Component(symbol="Device:R", ref="R2", value="10k", footprint="Resistor_SMD:R_0603_1608Metric")
    r2 = Component(symbol="Device:R", ref="R2", value="10k", footprint="Resistor_SMD:R_0603_1608Metric")



# Generate the circuit
if __name__ == '__main__':
    circuit = main()
    # Generate KiCad project (creates directory)
    circuit.generate_kicad_project(project_name="03_dual_hierarchy_connected_generated_generated")
    # Generate KiCad netlist (required for ratsnest display)
    circuit.generate_kicad_netlist("03_dual_hierarchy_connected_generated_generated/03_dual_hierarchy_connected_generated_generated.net")