"""Quantum error correction codes for educational purposes."""

from __future__ import annotations
import numpy as np
from typing import List, Dict, Tuple
from ..core.circuit import Circuit
from ..core.executor import Executor
from ..core.statevector import Statevector


class ShorCode:
    """Simplified 9-qubit Shor code implementation for education."""
    
    @staticmethod
    def create_encoding_circuit() -> Circuit:
        """Create a simplified encoding circuit."""
        circuit = Circuit(3)  # Simplified to 3 qubits for education
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.cx(0, 2)
        return circuit
    
    @staticmethod
    def demonstrate() -> Dict:
        """Demonstrate basic error correction concepts."""
        print("Shor Code Error Correction Demo")
        print("=" * 40)
        
        executor = Executor()
        
        # Create encoded state
        circuit = ShorCode.create_encoding_circuit()
        state = executor.run(circuit)
        measurements = state.measure_all(1000)
        
        print(f"Encoded state measurements: {measurements}")
        
        return {'measurements': measurements}


class SteaneCode:
    """Simplified Steane code implementation."""
    
    @staticmethod
    def create_encoding_circuit() -> Circuit:
        """Create a simplified 7-qubit encoding circuit."""
        circuit = Circuit(7)
        
        # Simplified encoding for educational purposes
        circuit.h(0)
        for i in range(1, 7):
            circuit.cx(0, i)
        
        return circuit
    
    @staticmethod
    def demonstrate() -> Dict:
        """Demonstrate Steane code basics."""
        print("Steane Code Demo")
        print("=" * 20)
        
        executor = Executor()
        circuit = SteaneCode.create_encoding_circuit()
        state = executor.run(circuit)
        measurements = state.measure_all(100)
        
        print(f"Steane code measurements: {measurements}")
        
        return {'measurements': measurements}


def surface_code_distance_3() -> Dict:
    """Demonstrate surface code concepts with distance 3."""
    print("Surface Code (Distance 3) Demo")
    print("=" * 30)
    
    # Create a simple 3x3 grid representation
    circuit = Circuit(9)  # 9 data qubits in 3x3 grid
    
    # Initialize in superposition
    for i in range(9):
        circuit.h(i)
    
    executor = Executor()
    state = executor.run(circuit)
    measurements = state.measure_all(100)
    
    print("Surface code provides topological error correction")
    print(f"Sample measurements: {list(measurements.keys())[:5]}...")
    
    return {'measurements': measurements}


def demonstrate_error_correction() -> Dict:
    """Run comprehensive error correction demonstration."""
    print("QUANTUM ERROR CORRECTION SHOWCASE")
    print("=" * 50)
    
    # Demonstrate different codes
    shor_results = ShorCode.demonstrate()
    print("\n" + "="*50)
    
    steane_results = SteaneCode.demonstrate()
    print("\n" + "="*50)
    
    surface_results = surface_code_distance_3()
    print("\n" + "="*50)
    
    print("Error correction codes protect quantum information!")
    print("These codes can detect and correct quantum errors.")
    
    return {
        'shor': shor_results,
        'steane': steane_results,
        'surface': surface_results
    }


__all__ = [
    'ShorCode',
    'SteaneCode', 
    'surface_code_distance_3',
    'demonstrate_error_correction'
]