"""Quantum noise models for educational simulation."""

from __future__ import annotations
import numpy as np
from typing import List
from ..core.statevector import Statevector


def bit_flip_channel(state: Statevector, p: float) -> Statevector:
    """Apply bit flip noise with probability p."""
    if np.random.random() < p:
        # Apply X gate to random qubit
        qubit = np.random.randint(0, state.num_qubits)
        new_data = state.data.copy()
        n = 2 ** state.num_qubits
        for i in range(n):
            if (i >> qubit) & 1:  # If qubit is |1⟩
                j = i ^ (1 << qubit)  # Flip to |0⟩
                new_data[j], new_data[i] = new_data[i], new_data[j]
        return Statevector(state.num_qubits, new_data)
    return state


def phase_flip_channel(state: Statevector, p: float) -> Statevector:
    """Apply phase flip noise with probability p."""
    if np.random.random() < p:
        # Apply Z gate to random qubit
        qubit = np.random.randint(0, state.num_qubits)
        new_data = state.data.copy()
        n = 2 ** state.num_qubits
        for i in range(n):
            if (i >> qubit) & 1:  # If qubit is |1⟩
                new_data[i] *= -1  # Apply phase flip
        return Statevector(state.num_qubits, new_data)
    return state


def depolarizing_channel(state: Statevector, p: float) -> Statevector:
    """Apply depolarizing noise with probability p."""
    if np.random.random() < p:
        # With probability p/3 each, apply X, Y, or Z
        noise_type = np.random.choice(['X', 'Y', 'Z'])
        qubit = np.random.randint(0, state.num_qubits)
        
        new_data = state.data.copy()
        n = 2 ** state.num_qubits
        
        if noise_type == 'X':
            # Bit flip
            for i in range(n):
                if (i >> qubit) & 1:
                    j = i ^ (1 << qubit)
                    new_data[j], new_data[i] = new_data[i], new_data[j]
        
        elif noise_type == 'Y':
            # Y = iXZ
            for i in range(n):
                if (i >> qubit) & 1:
                    j = i ^ (1 << qubit)
                    new_data[j], new_data[i] = -1j * new_data[i], 1j * new_data[j]
                else:
                    new_data[i] *= -1j
        
        elif noise_type == 'Z':
            # Phase flip
            for i in range(n):
                if (i >> qubit) & 1:
                    new_data[i] *= -1
        
        return Statevector(state.num_qubits, new_data)
    
    return state


def amplitude_damping_channel(state: Statevector, gamma: float) -> Statevector:
    """Apply amplitude damping with parameter gamma."""
    if np.random.random() < gamma:
        # Apply damping to a random qubit
        qubit = np.random.randint(0, state.num_qubits)
        new_data = state.data.copy()
        n = 2 ** state.num_qubits
        
        # Amplitude damping: |1⟩ → |0⟩ with some probability
        for i in range(n):
            if (i >> qubit) & 1:  # If qubit is |1⟩
                j = i ^ (1 << qubit)  # Corresponding |0⟩ state
                amplitude_1 = new_data[i]
                # Transfer amplitude with damping
                new_data[j] += np.sqrt(gamma) * amplitude_1
                new_data[i] *= np.sqrt(1 - gamma)
        
        return Statevector(state.num_qubits, new_data)
    
    return state


def phase_damping_channel(state: Statevector, gamma: float) -> Statevector:
    """Apply phase damping with parameter gamma."""
    if np.random.random() < gamma:
        # Apply random phase to superposition
        qubit = np.random.randint(0, state.num_qubits)
        new_data = state.data.copy()
        n = 2 ** state.num_qubits
        
        # Reduce coherence between |0⟩ and |1⟩ states
        for i in range(n):
            if (i >> qubit) & 1:  # If qubit is |1⟩
                new_data[i] *= np.sqrt(1 - gamma)
        
        return Statevector(state.num_qubits, new_data)
    
    return state


__all__ = [
    'bit_flip_channel',
    'phase_flip_channel', 
    'depolarizing_channel',
    'amplitude_damping_channel',
    'phase_damping_channel'
]