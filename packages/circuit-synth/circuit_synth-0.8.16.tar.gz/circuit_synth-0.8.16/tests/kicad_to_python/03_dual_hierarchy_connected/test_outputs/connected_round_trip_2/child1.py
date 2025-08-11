#!/usr/bin/env python3
"""
child1 subcircuit generated from KiCad
"""

from circuit_synth import *

@circuit(name='child1')
def child1(vin, gnd):
    """
    child1 subcircuit
    Parameters: VIN, GND
    """

    # Create components
    r2 = Component(symbol="Device:R", ref="R2", value="10k", footprint="Resistor_SMD:R_0603_1608Metric")
