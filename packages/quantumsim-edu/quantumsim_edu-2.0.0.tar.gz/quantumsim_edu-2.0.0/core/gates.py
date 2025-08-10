"""
Gate definitions for the educational quantum simulator.

Defines a minimal set of single- and two-qubit gates plus utilities 
to build unitary matrices. Focus is clarity rather than extreme performance.
"""

from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from typing import Callable, Dict


@dataclass(frozen=True)
class Gate:
    name: str
    matrix: Callable[[float], np.ndarray] | np.ndarray  # parameterized or static
    num_qubits: int = 1
    is_parametric: bool = False
    
    def unitary(self, theta: float | None = None) -> np.ndarray:
        if callable(self.matrix):
            if not self.is_parametric:
                return self.matrix(0.0)
            if theta is None:
                raise ValueError(f"Gate {self.name} requires a parameter theta")
            return self.matrix(theta)
        return self.matrix


# Basic constants
I = np.array([[1, 0], [0, 1]], dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
H = (1/np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)
S = np.array([[1, 0], [0, 1j]], dtype=complex)
T = np.array([[1, 0], [0, np.exp(1j*np.pi/4)]], dtype=complex)


# Parametric rotations
def RZ(theta: float) -> np.ndarray:
    return np.array([[np.exp(-1j*theta/2), 0], [0, np.exp(1j*theta/2)]], dtype=complex)

def RX(theta: float) -> np.ndarray:
    return np.array([[np.cos(theta/2), -1j*np.sin(theta/2)], 
                     [-1j*np.sin(theta/2), np.cos(theta/2)]], dtype=complex)

def RY(theta: float) -> np.ndarray:
    return np.array([[np.cos(theta/2), -np.sin(theta/2)], 
                     [np.sin(theta/2), np.cos(theta/2)]], dtype=complex)


# Two-qubit gates
CX = np.array([[1,0,0,0], [0,1,0,0], [0,0,0,1], [0,0,1,0]], dtype=complex)
CZ = np.array([[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,-1]], dtype=complex)
SWAP = np.array([[1,0,0,0], [0,0,1,0], [0,1,0,0], [0,0,0,1]], dtype=complex)


GATES: Dict[str, Gate] = {
    'I': Gate('I', I),
    'X': Gate('X', X),
    'Y': Gate('Y', Y),
    'Z': Gate('Z', Z),
    'H': Gate('H', H),
    'S': Gate('S', S),
    'T': Gate('T', T),
    'RZ': Gate('RZ', RZ, is_parametric=True),
    'RX': Gate('RX', RX, is_parametric=True),
    'RY': Gate('RY', RY, is_parametric=True),
    'CX': Gate('CX', CX, num_qubits=2),
    'CZ': Gate('CZ', CZ, num_qubits=2),
    'SWAP': Gate('SWAP', SWAP, num_qubits=2),
}

__all__ = ['Gate', 'GATES']