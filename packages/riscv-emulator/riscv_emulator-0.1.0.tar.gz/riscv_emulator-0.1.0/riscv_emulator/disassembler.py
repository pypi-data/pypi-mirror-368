def sign_extend(value, bits):
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)

INSTRUCTION_SET = {
    0x33: {
        (0x0, 0x00): "add",
        (0x0, 0x20): "sub",
        (0x1, 0x00): "sll",
        (0x2, 0x00): "slt",
        (0x3, 0x00): "sltu",
        (0x4, 0x00): "xor",
        (0x5, 0x00): "srl",
        (0x5, 0x20): "sra",
        (0x6, 0x00): "or",
        (0x7, 0x00): "and",
    },
    0x13: {
        0x0: "addi",
        0x2: "slti",
        0x3: "sltiu",
        0x4: "xori",
        0x6: "ori",
        0x7: "andi",
        0x1: "slli",
        0x5: {0x00: "srli", 0x20: "srai"},
    },
    0x03: {
        0x0: "lb",
        0x1: "lh",
        0x2: "lw",
        0x4: "lbu",
        0x5: "lhu",
    },
    0x67: {
        0x0: "jalr",
    },
    0x23: {
        0x0: "sb",
        0x1: "sh",
        0x2: "sw",
    },
    0x63: {
        0x0: "beq",
        0x1: "bne",
        0x4: "blt",
        0x5: "bge",
        0x6: "bltu",
        0x7: "bgeu",
    },
    0x37: "lui",
    0x17: "auipc",
    0x6F: "jal",
    0x73: {
        0x0: {0: "ecall", 1: "ebreak"}
    }
}

def get_bits(val, start, end):
    mask = (1 << (end - start + 1)) - 1
    return (val >> start) & mask

def disassemble(hexcode):
    
    instr = int(hexcode, 16)
    opcode = get_bits(instr, 0, 6)
    if opcode == 0x33:
        rd = get_bits(instr, 7, 11)
        funct3 = get_bits(instr, 12, 14)
        rs1 = get_bits(instr, 15, 19)
        rs2 = get_bits(instr, 20, 24)
        funct7 = get_bits(instr, 25, 31)
        mnemonic = INSTRUCTION_SET[opcode].get((funct3, funct7))
        if mnemonic:
            return f"{mnemonic} x{rd}, x{rs1}, x{rs2}"
    elif opcode in (0x13, 0x03, 0x67):
        rd = get_bits(instr, 7, 11)
        funct3 = get_bits(instr, 12, 14)
        rs1 = get_bits(instr, 15, 19)
        imm = sign_extend(get_bits(instr, 20, 31), 12)
        if opcode == 0x13 and funct3 in (0x1, 0x5):
            shamt = get_bits(instr, 20, 24)
            funct7 = get_bits(instr, 25, 31)
            if funct3 == 0x1:
                mnemonic = INSTRUCTION_SET[opcode][funct3]
                return f"{mnemonic} x{rd}, x{rs1}, {shamt}"
            elif funct3 == 0x5:
                mnemonic = INSTRUCTION_SET[opcode][funct3].get(funct7)
                if mnemonic:
                    return f"{mnemonic} x{rd}, x{rs1}, {shamt}"
        else:
            if opcode == 0x13:
                mnemonic = INSTRUCTION_SET[opcode].get(funct3)
            else:
                mnemonic = INSTRUCTION_SET[opcode].get(funct3)
            if mnemonic:
                if opcode == 0x03:
                    return f"{mnemonic} x{rd}, {imm}(x{rs1})"
                elif opcode == 0x67:
                    return f"{mnemonic} x{rd}, {imm}(x{rs1})"
                else:
                    return f"{mnemonic} x{rd}, x{rs1}, {imm}"
    elif opcode == 0x23:
        funct3 = get_bits(instr, 12, 14)
        rs1 = get_bits(instr, 15, 19)
        rs2 = get_bits(instr, 20, 24)
        imm = (get_bits(instr, 25, 31) << 5) | get_bits(instr, 7, 11)
        imm = sign_extend(imm, 12)
        mnemonic = INSTRUCTION_SET[opcode].get(funct3)
        if mnemonic:
            return f"{mnemonic} x{rs2}, {imm}(x{rs1})"
    elif opcode == 0x63:
        funct3 = get_bits(instr, 12, 14)
        rs1 = get_bits(instr, 15, 19)
        rs2 = get_bits(instr, 20, 24)
        imm = ((get_bits(instr, 31, 31) << 12) | (get_bits(instr, 7, 7) << 11) | (get_bits(instr, 25, 30) << 5) | (get_bits(instr, 8, 11) << 1))
        imm = sign_extend(imm, 13)
        mnemonic = INSTRUCTION_SET[opcode].get(funct3)
        if mnemonic:
            return f"{mnemonic} x{rs1}, x{rs2}, {imm}"
    elif opcode in (0x37, 0x17):
        rd = get_bits(instr, 7, 11)
        imm = get_bits(instr, 12, 31) << 12
        mnemonic = INSTRUCTION_SET[opcode]
        return f"{mnemonic} x{rd}, {imm}"
    elif opcode == 0x6F:
        rd = get_bits(instr, 7, 11)
        imm = ((get_bits(instr, 31, 31) << 20) | (get_bits(instr, 12, 19) << 12) | (get_bits(instr, 20, 20) << 11) | (get_bits(instr, 21, 30) << 1))
        imm = sign_extend(imm, 21)
        mnemonic = INSTRUCTION_SET[opcode]
        return f"{mnemonic} x{rd}, {imm}"
    elif opcode == 0x73:
        funct3 = get_bits(instr, 12, 14)
        imm = get_bits(instr, 20, 31)
        sys_map = INSTRUCTION_SET[opcode].get(funct3)
        if sys_map and imm in sys_map:
            return sys_map[imm]
    return "unknown"