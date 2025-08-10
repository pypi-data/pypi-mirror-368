"""
ASCII circuit visualization for educational purposes.
"""

from __future__ import annotations
from typing import List, Dict, Tuple
from ..core.circuit import Circuit, Instruction


class ASCIIDrawer:
    """Draw quantum circuits as ASCII art for terminal/notebook display."""
    
    def __init__(self, circuit: Circuit):
        self.circuit = circuit
        self.num_qubits = circuit.num_qubits

    def draw(self, show_qubits: bool = True) -> str:
        """Generate ASCII representation of the circuit."""
        lines = []
        
        # Calculate gate positions and wire lengths
        gate_positions = self._calculate_positions()
        max_width = max(pos[1] for pos in gate_positions.values()) if gate_positions else 0
        
        # Draw each qubit line
        for q in range(self.num_qubits):
            line = self._draw_qubit_line(q, gate_positions, max_width, show_qubits)
            lines.append(line)
            
        return '\n'.join(lines)

    def _calculate_positions(self) -> Dict[int, Tuple[int, int]]:
        """Calculate (row, column) positions for each instruction."""
        positions = {}
        column_positions = [0] * self.num_qubits  # Last occupied column per qubit
        
        for i, inst in enumerate(self.circuit.instructions):
            # Find the earliest column where this gate can be placed
            min_col = max(column_positions[q] for q in inst.targets) + 1
            
            # Update positions for all target qubits
            for q in inst.targets:
                column_positions[q] = min_col
                
            positions[i] = (min(inst.targets), min_col)
        
        return positions

    def _draw_qubit_line(self, qubit: int, positions: Dict[int, Tuple[int, int]], 
                        max_width: int, show_qubits: bool) -> str:
        """Draw a single qubit's wire and gates."""
        # Start with qubit label
        if show_qubits:
            line = f"q{qubit}: "
        else:
            line = ""
        
        # Build the wire with gates
        wire_chars = ['-'] * (max_width + 2)  # Extra space for final wire
        
        for i, inst in enumerate(self.circuit.instructions):
            if qubit in inst.targets:
                row, col = positions[i]
                gate_char = self._get_gate_char(inst, qubit)
                
                # Handle multi-qubit gates
                if inst.gate.num_qubits > 1:
                    if qubit == min(inst.targets):
                        wire_chars[col] = gate_char
                    else:
                        wire_chars[col] = self._get_connection_char(inst, qubit)
                else:
                    wire_chars[col] = gate_char
        
        line += ''.join(wire_chars)
        return line

    def _get_gate_char(self, inst: Instruction, qubit: int) -> str:
        """Get the character representation for a gate."""
        gate_chars = {
            'H': 'H',
            'X': 'X', 
            'Y': 'Y',
            'Z': 'Z',
            'S': 'S',
            'T': 'T',
            'I': 'I',
            'RX': 'Rx',
            'RY': 'Ry', 
            'RZ': 'Rz',
            'CX': '+' if qubit == max(inst.targets) else 'C',
            'CZ': 'Z' if qubit == max(inst.targets) else 'C',
            'SWAP': 'X'
        }
        return gate_chars.get(inst.gate.name, '?')

    def _get_connection_char(self, inst: Instruction, qubit: int) -> str:
        """Get connection character for multi-qubit gates."""
        if inst.gate.name == 'CX':
            return '+' if qubit == max(inst.targets) else 'C'
        elif inst.gate.name == 'CZ':
            return 'Z' if qubit == max(inst.targets) else 'C'
        elif inst.gate.name == 'SWAP':
            return 'X'
        return '|'


def print_circuit(circuit: Circuit, show_qubits: bool = True) -> None:
    """Convenience function to print circuit diagram."""
    drawer = ASCIIDrawer(circuit)
    print(drawer.draw(show_qubits))


__all__ = ['ASCIIDrawer', 'print_circuit']