# quantumsim-edu: Educational Quantum Computing Simulator

A lightweight, educational quantum circuit simulator designed for learning```python
import quantumsim as qs

# Create a Bell state
circuit = qs.Circuit(2)
circuit.h(0)
circuit.cx(0, 1)

# Execute the circuit
executor = qs.Executor()
statevector = executor.run(circuit)
result = statevector.measure_all(shots=1000)
print(result)  # {'00': ~500, '11': ~500}
```uting concepts. Built with clarity and modularity in mind, quantumsim provides an intuitive interface for building and simulating quantum circuits.

## How quantumsim Works

quantumsim uses **statevector simulation** to model quantum systems:

### Quantum State Representation
- Quantum states are represented as complex-valued vectors in a 2^n dimensional Hilbert space
- For n qubits, the statevector contains 2^n complex amplitudes
- Each amplitude represents the probability amplitude for a specific computational basis state

### Gate Operations
- Quantum gates are implemented as unitary matrices
- Gate application involves matrix-vector multiplication with the statevector
- Multi-qubit gates use tensor product operations to construct full-dimensional matrices

### Circuit Execution
- Circuits are built using a fluent API that chains gate operations
- The executor applies gates sequentially to evolve the quantum state
- Intermediate states can be inspected for educational purposes

## Features

**Core Simulation Engine:**
- Statevector simulator supporting up to 20 qubits on typical hardware
- Complete quantum gate library: Pauli gates (X, Y, Z), Hadamard (H), Phase gates (S, T), Rotation gates (RX, RY, RZ), Controlled gates (CX, CZ), SWAP gate
- Fluent circuit building API with method chaining
- ASCII circuit visualization for educational clarity

**Educational Tools:**
- Interactive examples demonstrating key quantum algorithms
- Bell state preparation and measurement
- Grover's search algorithm implementation
- Quantum teleportation protocol
- Noise modeling for realistic quantum simulation

## Installation

```bash
pip install quantumsim-edu
```

## 🔧 How to Import and Use

### Basic Imports
```python
# For users who installed via pip install quantumsim-edu
from quantumsim import Circuit, Executor, print_circuit, GATES
from quantumsim.core import Statevector
from quantumsim.noise import DepolarizingChannel
```

## Quick Start

```python
from quantumsim import Circuit, Executor, print_circuit

# Create a 2-qubit circuit
circuit = Circuit(2)
circuit.h(0)        # Hadamard gate on qubit 0
circuit.cx(0, 1)    # CNOT gate: control=0, target=1

# Visualize the circuit
print_circuit(circuit)

# Execute the circuit
executor = Executor()
result = executor.run(circuit)

# Get measurement results
counts = result.measure_all(shots=1000)
print(f"Bell state measurements: {counts}")
# Expected output: {'00': ~500, '11': ~500}
```

## 💻 Advanced Examples

### Grover's Search Algorithm
```python
from quantumsim import Circuit, Executor

def grovers_algorithm(target_state="11"):
    """Grover's algorithm to find a marked state in a 2-qubit system"""
    circuit = Circuit(2)
    
    # Initialize superposition
    circuit.h(0).h(1)
    
    # Oracle - mark the target state |11⟩
    if target_state == "11":
        circuit.cz(0, 1)
    
    # Diffusion operator
    circuit.h(0).h(1)
    circuit.x(0).x(1)
    circuit.cz(0, 1)
    circuit.x(0).x(1)
    circuit.h(0).h(1)
    
    return circuit

# Execute Grover's algorithm
circuit = grovers_algorithm()
result = Executor().run(circuit)
counts = result.measure_all(1000)
print(f"Grover's results: {counts}")  # Should favor |11⟩
```

### Quantum Noise Simulation
```python
from quantumsim.noise import DepolarizingChannel

# Create a Bell state
circuit = Circuit(2)
circuit.h(0).cx(0, 1)

executor = Executor()
clean_state = executor.run(circuit)

# Apply noise
noise = DepolarizingChannel(p=0.1)  # 10% noise
noisy_state = noise.apply_stochastic(clean_state)

# Compare measurements
clean_counts = clean_state.measure_all(1000)
noisy_counts = noisy_state.measure_all(1000)

print("Clean measurements:", clean_counts)
print("Noisy measurements:", noisy_counts)
```

# Create a Bell state circuit
circuit = Circuit(2)
circuit.h(0)        # Apply Hadamard to qubit 0
circuit.cx(0, 1)    # Apply CNOT with control=0, target=1

# Execute the circuit
executor = Executor()
final_state = executor.run(circuit)

# Measure the result
measurement_counts = final_state.measure_all(shots=1000)
print("Measurement results:", measurement_counts)
# Expected: {'00': ~500, '11': ~500} (Bell state superposition)
```

## License

MIT License - Free for educational and research use.