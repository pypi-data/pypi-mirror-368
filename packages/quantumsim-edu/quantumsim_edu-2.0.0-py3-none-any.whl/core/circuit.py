"""
Circuit data structure for representing quantum circuits.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Sequence, Optional
from .gates import GATES, Gate


@dataclass
class Instruction:
    gate: Gate
    targets: Sequence[int]
    param: Optional[float] = None


class Circuit:
    def __init__(self, num_qubits: int):
        self.num_qubits = num_qubits
        self.instructions: List[Instruction] = []

    def add(self, name: str, *targets: int, theta: float | None = None):
        gate = GATES[name]
        if len(targets) != gate.num_qubits:
            raise ValueError("Target count mismatch for gate")
        self.instructions.append(Instruction(gate, targets, theta))
        return self

    # Convenience methods for common gates
    def h(self, q: int):
        return self.add('H', q)
    
    def x(self, q: int):
        return self.add('X', q)
    
    def y(self, q: int):
        return self.add('Y', q)
    
    def z(self, q: int):
        return self.add('Z', q)
    
    def s(self, q: int):
        return self.add('S', q)
    
    def t(self, q: int):
        return self.add('T', q)
    
    def cx(self, c: int, t: int):
        return self.add('CX', c, t)
    
    def cz(self, c: int, t: int):
        return self.add('CZ', c, t)
    
    def swap(self, a: int, b: int):
        return self.add('SWAP', a, b)
    
    def rz(self, q: int, theta: float):
        return self.add('RZ', q, theta=theta)
    
    def rx(self, q: int, theta: float):
        return self.add('RX', q, theta=theta)
    
    def ry(self, q: int, theta: float):
        return self.add('RY', q, theta=theta)


__all__ = ['Circuit', 'Instruction']