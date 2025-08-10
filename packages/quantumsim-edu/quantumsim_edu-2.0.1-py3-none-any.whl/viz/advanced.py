"""Enhanced quantum visualization tools."""

from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
from ..core.statevector import Statevector
from ..core.circuit import Circuit


def plot_bloch_sphere(states: List[Tuple[np.ndarray, str]], title: str = "Bloch Sphere") -> None:
    """Plot quantum states on Bloch sphere (simplified educational version)."""
    print(f"Bloch Sphere Visualization: {title}")
    print("=" * 40)
    
    for state, label in states:
        if len(state) != 2:
            print(f"Skipping {label}: only single-qubit states supported")
            continue
            
        alpha, beta = state
        
        # Calculate Bloch coordinates
        x = 2 * np.real(alpha * np.conj(beta))
        y = 2 * np.imag(alpha * np.conj(beta))  
        z = np.abs(alpha)**2 - np.abs(beta)**2
        
        print(f"{label}: Bloch coordinates = ({x:.3f}, {y:.3f}, {z:.3f})")
    
    print("Note: Use matplotlib for full 3D visualization")


def animate_evolution(circuit: Circuit, steps: int = 10) -> Dict:
    """Animate quantum state evolution through circuit."""
    print("Quantum State Evolution Animation")
    print("=" * 35)
    
    from ..core.executor import Executor
    executor = Executor()
    
    # For educational purposes, show state at different points
    print("State evolution through circuit:")
    
    # Initial state
    initial_circuit = Circuit(circuit.num_qubits)
    state = executor.run(initial_circuit)
    print(f"Initial state: {state.data}")
    
    # Add gates one by one
    evolving_circuit = Circuit(circuit.num_qubits)
    
    for i, instruction in enumerate(circuit.instructions):
        # Add this instruction
        gate_name = instruction.gate.name
        targets = instruction.targets
        
        if gate_name == 'H':
            evolving_circuit.h(targets[0])
        elif gate_name == 'X':
            evolving_circuit.x(targets[0])
        elif gate_name == 'CX' and len(targets) == 2:
            evolving_circuit.cx(targets[0], targets[1])
        # Add other gates as needed
        
        # Execute and show state
        state = executor.run(evolving_circuit)
        print(f"After gate {i+1} ({gate_name}): {state.data}")
    
    return {"final_state": state.data}


def visualize_measurement_statistics(measurements: Dict[str, int], title: str = "Measurement Results") -> None:
    """Visualize measurement statistics."""
    print(f"\n{title}")
    print("=" * len(title))
    
    total_shots = sum(measurements.values())
    
    print("Measurement outcomes:")
    for state, count in sorted(measurements.items()):
        probability = count / total_shots
        bar = "█" * int(probability * 20)  # Simple ASCII bar chart
        print(f"|{state}⟩: {count:4d} ({probability:.3f}) {bar}")
    
    print(f"\nTotal shots: {total_shots}")


def plot_quantum_fidelity(states: List[Statevector], labels: List[str]) -> None:
    """Calculate and display quantum fidelities between states."""
    print("Quantum State Fidelity Matrix")
    print("=" * 30)
    
    n = len(states)
    print(f"Computing fidelities for {n} states")
    
    # Print header
    print("     ", end="")
    for label in labels:
        print(f"{label:>8}", end="")
    print()
    
    # Compute fidelity matrix
    for i, (state_i, label_i) in enumerate(zip(states, labels)):
        print(f"{label_i:>4} ", end="")
        for j, state_j in enumerate(states):
            # Fidelity = |⟨ψ_i|ψ_j⟩|²
            overlap = np.abs(np.vdot(state_i.data, state_j.data))**2
            print(f"{overlap:>8.3f}", end="")
        print()


__all__ = [
    'plot_bloch_sphere',
    'animate_evolution', 
    'visualize_measurement_statistics',
    'plot_quantum_fidelity'
]