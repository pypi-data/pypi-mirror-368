"""Quantum Machine Learning algorithms and tools."""

from __future__ import annotations
import numpy as np
from typing import List, Dict, Tuple, Optional
from ..core.circuit import Circuit
from ..core.executor import Executor


class QuantumNeuralNetwork:
    """Educational quantum neural network implementation."""
    
    def __init__(self, num_qubits: int, num_layers: int = 2):
        self.num_qubits = num_qubits
        self.num_layers = num_layers
        self.executor = Executor()
        self.parameters = self._initialize_parameters()
    
    def _initialize_parameters(self) -> List[float]:
        """Initialize random parameters for the QNN."""
        # Each layer has rotation parameters for each qubit
        num_params = self.num_qubits * self.num_layers * 3  # RX, RY, RZ for each qubit
        return np.random.uniform(0, 2*np.pi, num_params)
    
    def create_ansatz(self, parameters: List[float]) -> Circuit:
        """Create parameterized quantum circuit ansatz."""
        circuit = Circuit(self.num_qubits)
        param_idx = 0
        
        for layer in range(self.num_layers):
            # Rotation gates for each qubit
            for qubit in range(self.num_qubits):
                circuit.rx(qubit, parameters[param_idx])
                param_idx += 1
                circuit.ry(qubit, parameters[param_idx])
                param_idx += 1
                circuit.rz(qubit, parameters[param_idx])
                param_idx += 1
            
            # Entangling layer (except last layer)
            if layer < self.num_layers - 1:
                for qubit in range(self.num_qubits - 1):
                    circuit.cx(qubit, qubit + 1)
        
        return circuit
    
    def forward(self, input_data: np.ndarray) -> float:
        """Forward pass of the QNN."""
        # Create circuit with input encoding
        circuit = Circuit(self.num_qubits)
        
        # Data encoding (simplified)
        for i, value in enumerate(input_data[:self.num_qubits]):
            if value > 0.5:
                circuit.x(i)
        
        # Add ansatz parameters
        ansatz = self.create_ansatz(self.parameters)
        for instruction in ansatz.instructions:
            gate_name = instruction.gate.name
            targets = instruction.targets
            if gate_name in ['RX', 'RY', 'RZ']:
                getattr(circuit, gate_name.lower())(targets[0], instruction.param)
            elif gate_name == 'CX':
                circuit.cx(targets[0], targets[1])
        
        # Execute and measure
        final_state = self.executor.run(circuit)
        
        # Expectation value of Z on first qubit as output
        measurements = final_state.measure_all(shots=1000)
        prob_0 = sum(count for state, count in measurements.items() 
                    if state[-1] == '0') / 1000
        prob_1 = 1 - prob_0
        expectation = prob_0 - prob_1
        
        return expectation


class QuantumKernelMethods:
    """Quantum kernel methods for machine learning."""
    
    def __init__(self, num_qubits: int, num_features: int):
        self.num_qubits = num_qubits
        self.num_features = num_features
        self.executor = Executor()
    
    def feature_map(self, x: np.ndarray) -> Circuit:
        """Create quantum feature map circuit."""
        circuit = Circuit(self.num_qubits)
        
        # ZZ-feature map
        for i, feature in enumerate(x[:self.num_qubits]):
            # First order terms
            circuit.h(i)
            circuit.rz(i, 2 * feature)
        
        # Second order terms (entangling)
        for i in range(self.num_qubits):
            for j in range(i + 1, self.num_qubits):
                circuit.cx(i, j)
                circuit.rz(j, 2 * x[i % len(x)] * x[j % len(x)])
                circuit.cx(i, j)
        
        return circuit
    
    def quantum_kernel(self, x1: np.ndarray, x2: np.ndarray) -> float:
        """Compute quantum kernel between two data points."""
        # Create feature map for x1
        circuit1 = self.feature_map(x1)
        state1 = self.executor.run(circuit1)
        
        # Create feature map for x2
        circuit2 = self.feature_map(x2)
        state2 = self.executor.run(circuit2)
        
        # Compute inner product (fidelity)
        kernel_value = abs(np.vdot(state1.data, state2.data))**2
        return kernel_value


def demonstrate_quantum_ml():
    """Demonstrate quantum machine learning capabilities."""
    print("   QUANTUM MACHINE LEARNING")
    print("=" * 50)
    
    # 1. Quantum Neural Network
    print("1. Quantum Neural Network")
    qnn = QuantumNeuralNetwork(num_qubits=2, num_layers=2)
    
    # Simple test data
    test_input = np.array([0.5, 0.3])
    output = qnn.forward(test_input)
    print(f"   QNN output for {test_input}: {output:.4f}")
    
    # 2. Quantum Kernel Methods
    print("\n2. Quantum Kernel Methods")
    qkm = QuantumKernelMethods(num_qubits=2, num_features=2)
    
    # Test kernel computation
    x1 = np.array([0.1, 0.2])
    x2 = np.array([0.3, 0.4])
    kernel_val = qkm.quantum_kernel(x1, x2)
    print(f"   Kernel value between {x1} and {x2}: {kernel_val:.4f}")
    
    return {
        'qnn_output': output,
        'kernel_value': kernel_val
    }


__all__ = [
    'QuantumNeuralNetwork',
    'QuantumKernelMethods', 
    'demonstrate_quantum_ml'
]