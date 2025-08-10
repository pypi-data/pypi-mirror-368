from riscv_emulator.debugger import debugger
from riscv_emulator.assembler import assemble

class emulator:
    def __init__(self, memory = 4096, abi = False):
        self.memory = bytearray(memory)
        self.rg = [0] * 32
        self.pc = 0
        self.abi = abi

    def sign_extend(self, value, bits):
        sign_bit = 1 << (bits - 1)
        return (value & (sign_bit - 1)) - (value & sign_bit)

    def load_program(self, path):
        with open(path, "rb") as f:
            program = f.read()
            required_size = len(program) + 4096
            if len(self.memory) < required_size:
                print(f"Expandng memory from {len(self.memory)} to {required_size} bytes.")
                self.memory = bytearray(required_size)
            self.memory[0:len(program)] = program

    def assemble(self, input_path):
        print(assemble(input_path))

    def run(self):
        while self.pc < len(self.memory):
            instr = int.from_bytes(self.memory[self.pc:self.pc+4], byteorder='little')
            if (instr == 0):
                break
            self.execute(instr)
    
    def debug(self):
        debugger(self)

    def execute(self, instr):
        old_pc = self.pc
        opcode = instr & 0x7f

        if opcode == 0x33:
            rd = (instr >> 7) & 0x1f
            funct3 = (instr >> 12) & 0x7
            rs1 = (instr >> 15) & 0x1f
            rs2 = (instr >> 20) & 0x1f
            funct7 = (instr >> 25) & 0x7f
            if funct3 == 0x0:
                if funct7 == 0x00:
                    self.rg[rd] = (self.rg[rs1] + self.rg[rs2]) & 0xffffffff
                elif funct7 == 0x20:
                    self.rg[rd] = (self.rg[rs1] - self.rg[rs2]) & 0xffffffff
            elif funct3 == 0x4:
                self.rg[rd] = (self.rg[rs1] ^ self.rg[rs2]) & 0xffffffff
            elif funct3 == 0x6:
                self.rg[rd] = (self.rg[rs1] | self.rg[rs2]) & 0xffffffff
            elif funct3 == 0x7:
                self.rg[rd] = (self.rg[rs1] & self.rg[rs2]) & 0xffffffff
            elif funct3 == 0x1:
                self.rg[rd] = (self.rg[rs1] << (self.rg[rs2] & 0x1f)) & 0xffffffff
            elif funct3 == 0x5:
                if funct7 == 0x00:
                    self.rg[rd] = (self.rg[rs1] >> (self.rg[rs2] & 0x1f)) & 0xffffffff
                elif funct7 == 0x20:
                    val = self.rg[rs1] & 0xffffffff
                    if val & 0x80000000:
                        self.rg[rd] = (val >> (self.rg[rs2] & 0x1f)) | (0xffffffff << (32 - (self.rg[rs2] & 0x1f))) & 0xffffffff
                    else:
                        self.rg[rd] = val >> (self.rg[rs2] & 0x1f)
            elif funct3 == 0x2:
                self.rg[rd] = 1 if self.sign_extend(self.rg[rs1], 32) < self.sign_extend(self.rg[rs2], 32) else 0
            elif funct3 == 0x3:
                self.rg[rd] = 1 if (self.rg[rs1] & 0xffffffff) < (self.rg[rs2] & 0xffffffff) else 0

        elif opcode == 0x13:
            rd = (instr >> 7) & 0x1f
            funct3 = (instr >> 12) & 0x7
            rs1 = (instr >> 15) & 0x1f
            imm = (instr >> 20) & 0xfff
            imm = self.sign_extend(imm, 12)
            if funct3 == 0x0:
                self.rg[rd] = (self.rg[rs1] + imm) & 0xffffffff
            elif funct3 == 0x4:
                self.rg[rd] = (self.rg[rs1] ^ imm)
            elif funct3 == 0x6:
                self.rg[rd] = (self.rg[rs1] | imm)
            elif funct3 == 0x7:
                self.rg[rd] = self.rg[rs1] & imm
            elif funct3 == 0x1:
                self.rg[rd] = (self.rg[rs1] << (imm & 0x1f)) & 0xffffffff
            elif funct3 == 0x5:
                if (imm >> 5) == 0x00:
                    self.rg[rd] = (self.rg[rs1] >> (imm & 0x1f)) & 0xffffffff
                elif (imm >> 5) == 0x20:
                    val = self.rg[rs1] & 0xffffffff
                    if val & 0x80000000:
                        self.rg[rd] = (val >> (imm & 0x1f)) | (0xffffffff << (32 - (imm & 0x1f))) & 0xffffffff
                    else:
                        self.rg[rd] = val >> (imm & 0x1f)
            elif funct3 == 0x2:
                self.rg[rd] = 1 if self.sign_extend(self.rg[rs1], 32) < imm else 0
            elif funct3 == 0x3:
                self.rg[rd] = 1 if (self.rg[rs1] & 0xffffffff) < (imm & 0xffffffff) else 0

        elif opcode == 0x3:
            rd = (instr >> 7) & 0x1f
            funct3 = (instr >> 12) & 0x7
            rs1 = (instr >> 15) & 0x1f
            imm = (instr >> 20) & 0xfff
            imm = self.sign_extend(imm, 12)
            address = self.rg[rs1] + imm
            if funct3 == 0x0:
                self.rg[rd] = self.sign_extend(self.memory[address], 8)
            elif funct3 == 0x1:
                val = int.from_bytes(self.memory[address:address + 2], "little")
                self.rg[rd] = self.sign_extend(val, 16)
            elif funct3 == 0x2:
                val = int.from_bytes(self.memory[address:address + 4], "little")
                self.rg[rd] = self.sign_extend(val, 32)
            elif funct3 == 0x4:
                self.rg[rd] = self.memory[address] & 0xff
            elif funct3 == 0x5:
                val = int.from_bytes(self.memory[address:address + 2], "little")
                self.rg[rd] = val & 0xffff

        elif opcode == 0x23:
            imm_bot = (instr >> 7) & 0x1f
            funct3 = (instr >> 12) & 0x7
            rs1 = (instr >> 15) & 0x1f
            rs2 = (instr >> 20) & 0x1f
            imm_top = (instr >> 25) & 0x7f
            imm = (imm_top << 5) | imm_bot
            imm = self.sign_extend(imm, 12)
            address = self.rg[rs1] + imm
            if funct3 == 0x0:
                self.memory[address] = self.rg[rs2] & 0xff
            elif funct3 == 0x1:
                self.memory[address:address + 2] = int.to_bytes(self.rg[rs2] & 0xffff, 2, "little")
            elif funct3 == 0x2:
                self.memory[address:address + 4] = int.to_bytes(self.rg[rs2] & 0xffffffff, 4, "little")

        elif opcode == 0x63:
            funct3 = (instr >> 12) & 0x7
            rs1 = (instr >> 15) & 0x1f
            rs2 = (instr >> 20) & 0x1f
            imm = ((instr >> 8) & 0xf) << 1
            imm |= ((instr >> 25) & 0x3f) << 5
            imm |= ((instr >> 7) & 0x1) << 11
            imm |= ((instr >> 31) & 0x1) << 12
            imm = self.sign_extend(imm, 13)
            if funct3 == 0x0:
                self.pc = self.pc + imm if self.rg[rs1] == self.rg[rs2] else self.pc
            elif funct3 == 0x1:
                self.pc = self.pc + imm if self.rg[rs1] != self.rg[rs2] else self.pc
            elif funct3 == 0x4:
                self.pc = self.pc + imm if self.sign_extend(self.rg[rs1], 32) < self.sign_extend(self.rg[rs2], 32) else self.pc
            elif funct3 == 0x5:
                self.pc = self.pc + imm if self.sign_extend(self.rg[rs1], 32) >= self.sign_extend(self.rg[rs2], 32) else self.pc
            elif funct3 == 0x6:
                self.pc = self.pc + imm if self.rg[rs1] & 0xffffffff < self.rg[rs2] & 0xffffffff else self.pc
            elif funct3 == 0x7:
                self.pc = self.pc + imm if self.rg[rs1] & 0xffffffff >= self.rg[rs2] & 0xffffffff else self.pc

        elif opcode == 0x6f:
            rd = (instr >> 7) & 0x1f
            imm = ((instr >> 21) & 0x3ff) << 1
            imm |= ((instr >> 20) & 0x1) << 11
            imm |= ((instr >> 12) & 0xff) << 12
            imm |= ((instr >> 31) & 0x1) << 20
            imm = self.sign_extend(imm, 21)
            self.rg[rd] = self.pc + 4
            self.pc += imm

        elif opcode == 0x67:
            rd = (instr >> 7) & 0x1f
            funct3 = (instr >> 12) & 0x7
            rs1 = (instr >> 15) & 0x1f
            imm = (instr >> 20) & 0xfff
            imm = self.sign_extend(imm, 12)
            if funct3 == 0x0:
                self.rg[rd] = self.pc + 4
                self.pc = (self.rg[rs1] + imm) & 0xfffffffe

        elif opcode == 0x37:
            rd = (instr >> 7) & 0x1f
            imm = (instr >> 12) & 0xfffff
            self.rg[rd] = imm << 12

        elif opcode == 0x17:
            rd = (instr >> 7) & 0x1f
            imm = (instr >> 12) & 0xfffff
            self.rg[rd] = self.pc + (imm << 12)

        elif opcode == 0x73:
            imm = (instr >> 20) & 0xfff
            if imm == 0x0:
                print("ECALL, ending execution")
                self.pc = len(self.memory)
            elif imm == 0x1:
                print("EBREAK")
                self.pc += 4
                debugger(self)
        if self.pc == old_pc:
            self.pc += 4
        self.rg[0] = 0