"""
Execute a circuit on a statevector.
"""

from __future__ import annotations
from .statevector import Statevector
from .circuit import Circuit, Instruction
from .gates import Gate


class Executor:
    def run(self, circuit: Circuit):
        """Execute a quantum circuit and return the final statevector."""
        sv = Statevector(circuit.num_qubits)
        
        for inst in circuit.instructions:
            self._apply_instruction(sv, inst)
            
        return sv

    def _apply_instruction(self, sv: Statevector, inst: Instruction):
        """Apply a single gate instruction to the statevector."""
        gate = inst.gate
        
        if gate.is_parametric:
            U = gate.unitary(inst.param)
        else:
            U = gate.unitary()
            
        sv.apply_unitary(U, inst.targets)


__all__ = ['Executor']