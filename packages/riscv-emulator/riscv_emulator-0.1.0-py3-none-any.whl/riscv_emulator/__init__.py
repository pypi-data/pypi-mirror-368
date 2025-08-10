"""
RISC-V Emulator Package
=======================
This package provides:
- An assembler for RISC-V assembly code
- An emulator to run RISC-V binaries
- A disassembler to convert binaries back into assembly

You can use it as a Python library or through the CLI (`riscv`).
"""

from .assembler import assemble
from .emulator import emulator
from .disassembler import disassemble

__all__ = [
    "assemble",
    "emulator",
    "disassemble",
]
