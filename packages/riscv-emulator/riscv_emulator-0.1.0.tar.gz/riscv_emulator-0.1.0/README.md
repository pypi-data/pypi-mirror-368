# 🖥️ RISC-V Emulator

A simple RISC-V **assembler**, **emulator**, and **disassembler** written in Python.  
It can be used both as a **command-line tool** and as a **Python library**.

---

## ✨ Features
- Assemble `.s` RISC-V assembly files into binary machine code
- Run binary files on a simple RISC-V CPU emulator
- Disassemble binary files back into readable assembly
- One-step assemble-and-run mode
- Works as both CLI tool and importable Python package

---

## 📦 Installation

From PyPI:
```bash
pip install riscv-emulator
```

From source:
```bash
git clone https://github.com/yourusername/riscv_emulator.git
cd riscv_emulator
pip install .
```

---

## 🚀 Usage

### CLI Commands
```bash
# Assemble a file
riscv assemble program.s -o program.bin

# Run a binary
riscv run program.bin

# Assemble and run in one step
riscv full program.s

# Disassemble a binary
riscv disassemble program.bin
```

---

### Python API
```python
from riscv_emulator import assemble, emulator, disassemble

# Assemble
assemble("program.s", "program.bin")

# Run
emu = emulator()
emu.load_program("program.bin")
emu.run()

# Disassemble
disassemble("program.bin")
```

---

## 📂 Project Structure
```
riscv_emulator/
├── riscv_emulator/
│   ├── __init__.py
│   ├── assembler.py
│   ├── debugger.py
│   ├── disassembler.py
│   ├── emulator.py
│   ├── main.py
├── README.md
├── pyproject.toml
├── LICENSE
```

---

## 📝 License
This project is licensed under the terms of the **MIT License**.  
See the [LICENSE](LICENSE) file for details.

---

## 💡 Example
Example assembly file (`program.s`):
```asm
addi x1, zero, 3
addi x2, zero, 4
add  x3, x1, x2
```
Run it:
```bash
riscv full program.s
```

---

## 🤝 Contributing
Pull requests are welcome!  
If you find a bug or have a feature request, please open an issue on GitHub.

---

## 🛠 Requirements
- Python 3.8+
- No external dependencies
