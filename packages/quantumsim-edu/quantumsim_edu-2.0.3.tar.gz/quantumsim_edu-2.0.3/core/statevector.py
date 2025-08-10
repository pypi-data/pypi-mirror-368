"""
Statevector representation and basic operations.

Little-endian convention: qubit 0 is least-significant bit in basis index.
"""

from __future__ import annotations
import numpy as np
from typing import Sequence, Dict


class Statevector:
    def __init__(self, num_qubits: int, data: np.ndarray | None = None):
        self.num_qubits = num_qubits
        dim = 2 ** num_qubits
        
        if data is None:
            self.data = np.zeros(dim, dtype=complex)
            self.data[0] = 1.0  # Start in |0...0⟩ state
        else:
            if data.shape != (dim,):
                raise ValueError("Statevector length mismatch")
            self.data = data.astype(complex, copy=False)

    def copy(self) -> 'Statevector':
        return Statevector(self.num_qubits, self.data.copy())

    def apply_unitary(self, U: np.ndarray, targets: Sequence[int]):
        """Apply unitary operation to specified target qubits."""
        k = len(targets)
        targets = list(targets)
        
        if U.shape != (2**k, 2**k):
            raise ValueError("Unitary dimension mismatch")
        
        # Sort targets to make tensor operations cleaner
        perm = np.argsort(targets)
        sorted_targets = [targets[i] for i in perm]
        
        num_qubits = self.num_qubits
        other_axes = [q for q in range(num_qubits) if q not in sorted_targets]
        full_order = sorted_targets + other_axes
        
        # Reshape and transpose to group target qubits at the front
        tensor = self.data.reshape([2]*num_qubits).transpose(full_order)
        
        front_dim = 2**k
        back_dim = 2**(num_qubits-k)
        
        tensor = tensor.reshape(front_dim, back_dim)
        tensor = U @ tensor
        
        # Reshape back and undo the transpose
        tensor = tensor.reshape([2]*num_qubits).transpose(np.argsort(full_order))
        self.data = tensor.reshape(2**num_qubits)

    def measure_probabilities(self) -> np.ndarray:
        """Get measurement probabilities for all computational basis states."""
        return np.abs(self.data)**2

    def sample(self, shots: int, rng: np.random.Generator | None = None):
        """Sample measurement outcomes according to quantum probabilities."""
        if rng is None:
            rng = np.random.default_rng()
        probs = self.measure_probabilities()
        outcomes = rng.choice(len(probs), size=shots, p=probs)
        return outcomes

    def measure_all(self, shots: int = 1, rng: np.random.Generator | None = None) -> Dict[str, int]:
        """Measure all qubits and return counts for each bitstring."""
        outcomes = self.sample(shots, rng)
        counts: Dict[str, int] = {}
        n = self.num_qubits
        
        for o in outcomes:
            bitstring = format(o, f'0{n}b')
            counts[bitstring] = counts.get(bitstring, 0) + 1
        
        return counts

    def __repr__(self):
        return f"Statevector(num_qubits={self.num_qubits}, data={self.data})"


__all__ = ['Statevector']