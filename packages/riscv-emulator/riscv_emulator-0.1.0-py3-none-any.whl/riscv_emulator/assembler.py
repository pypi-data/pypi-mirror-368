import os, re

REGISTER_MAP = {f'x{i}': i for i in range(32)}
REGISTER_MAP.update({
    'zero': 0, 'ra': 1, 'sp': 2, 'gp': 3, 'tp': 4,
    't0': 5, 't1': 6, 't2': 7,
    's0': 8, 'fp': 8, 's1': 9,
    'a0': 10, 'a1': 11, 'a2': 12, 'a3': 13, 'a4': 14, 'a5': 15, 'a6': 16, 'a7': 17,
    's2': 18, 's3': 19, 's4': 20, 's5': 21, 's6': 22, 's7': 23, 's8': 24, 's9': 25, 's10': 26, 's11': 27,
    't3': 28, 't4': 29, 't5': 30, 't6': 31
})

INSTRUCTION_SET = {
    'add':  {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b000, 'funct7': 0b0000000},
    'sub':  {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b000, 'funct7': 0b0100000},
    'sll':  {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b001, 'funct7': 0b0000000},
    'slt':  {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b010, 'funct7': 0b0000000},
    'sltu': {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b011, 'funct7': 0b0000000},
    'xor':  {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b100, 'funct7': 0b0000000},
    'srl':  {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b101, 'funct7': 0b0000000},
    'sra':  {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b101, 'funct7': 0b0100000},
    'or':   {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b110, 'funct7': 0b0000000},
    'and':  {'type': 'R', 'opcode': 0b0110011, 'funct3': 0b111, 'funct7': 0b0000000},
    'addi': {'type': 'I', 'opcode': 0b0010011, 'funct3': 0b000},
    'slti': {'type': 'I', 'opcode': 0b0010011, 'funct3': 0b010},
    'sltiu':{'type': 'I', 'opcode': 0b0010011, 'funct3': 0b011},
    'xori': {'type': 'I', 'opcode': 0b0010011, 'funct3': 0b100},
    'ori':  {'type': 'I', 'opcode': 0b0010011, 'funct3': 0b110},
    'andi': {'type': 'I', 'opcode': 0b0010011, 'funct3': 0b111},
    'slli': {'type': 'I', 'opcode': 0b0010011, 'funct3': 0b001, 'funct7': 0b0000000},
    'srli': {'type': 'I', 'opcode': 0b0010011, 'funct3': 0b101, 'funct7': 0b0000000},
    'srai': {'type': 'I', 'opcode': 0b0010011, 'funct3': 0b101, 'funct7': 0b0100000},
    'jalr': {'type': 'I', 'opcode': 0b1100111, 'funct3': 0b000},
    'lb':   {'type': 'I', 'opcode': 0b0000011, 'funct3': 0b000},
    'lh':   {'type': 'I', 'opcode': 0b0000011, 'funct3': 0b001},
    'lw':   {'type': 'I', 'opcode': 0b0000011, 'funct3': 0b010},
    'lbu':  {'type': 'I', 'opcode': 0b0000011, 'funct3': 0b100},
    'lhu':  {'type': 'I', 'opcode': 0b0000011, 'funct3': 0b101},
    'sb':   {'type': 'S', 'opcode': 0b0100011, 'funct3': 0b000},
    'sh':   {'type': 'S', 'opcode': 0b0100011, 'funct3': 0b001},
    'sw':   {'type': 'S', 'opcode': 0b0100011, 'funct3': 0b010},
    'beq':  {'type': 'B', 'opcode': 0b1100011, 'funct3': 0b000},
    'bne':  {'type': 'B', 'opcode': 0b1100011, 'funct3': 0b001},
    'blt':  {'type': 'B', 'opcode': 0b1100011, 'funct3': 0b100},
    'bge':  {'type': 'B', 'opcode': 0b1100011, 'funct3': 0b101},
    'bltu': {'type': 'B', 'opcode': 0b1100011, 'funct3': 0b110},
    'bgeu': {'type': 'B', 'opcode': 0b1100011, 'funct3': 0b111},
    'lui':  {'type': 'U', 'opcode': 0b0110111},
    'auipc':{'type': 'U', 'opcode': 0b0010111},
    'jal':  {'type': 'J', 'opcode': 0b1101111},
    'ecall':{'type': 'SYS', 'opcode': 0b1110011},
    'ebreak':{'type': 'SYS', 'opcode': 0b1110011},
}

class Section:
    def __init__(self, name, start_addr=0):
        self.name = name
        self.start_addr = start_addr
        self.data = bytearray()
        self.labels = {}
        self.current_addr = start_addr
        
    def add_data(self, data):
        self.data.extend(data)
        self.current_addr += len(data)
        
    def add_label(self, label, offset=None):
        if offset is None:
            offset = len(self.data)
        self.labels[label] = self.start_addr + offset
        
    def align(self, alignment):
        current_len = len(self.data)
        padding = (alignment - (current_len % alignment)) % alignment
        if padding > 0:
            self.add_data(bytes(padding))

class Assembler:
    def __init__(self):
        self.sections = {}
        self.current_section = None
        self.symbols = {}
        self.global_symbols = set()
        self.text_start_addr = 0x00000000
        self.data_start_addr = 0x00001000
        
    def get_or_create_section(self, name):
        if name not in self.sections:
            if name == 'text':
                start_addr = self.text_start_addr
            elif name == 'data':
                start_addr = self.data_start_addr
            else:
                start_addr = 0
            self.sections[name] = Section(name, start_addr)
        return self.sections[name]
        
    def parse_string_literal(self, s):
        if not (s.startswith("'") and s.endswith("'")) and not (s.startswith('"') and s.endswith('"')):
            raise ValueError(f"String literal must be quoted: {s}")
        
        s = s[1:-1]
        s = s.replace('\\n', '\n')
        s = s.replace('\\t', '\t')
        s = s.replace('\\r', '\r')
        s = s.replace('\\\\', '\\')
        s = s.replace("\\'", "'")
        s = s.replace('\\"', '"')
        return s
        
    def process_pseudo_op(self, parts, line_num):
        directive = parts[0]
        
        if directive == '.text':
            self.current_section = self.get_or_create_section('text')
        elif directive == '.data':
            self.current_section = self.get_or_create_section('data')
        elif directive.startswith('.section'):
            if len(parts) < 2:
                raise ValueError(f"Line {line_num}: .section requires section name")
            section_name = parts[1].lstrip('.')
            self.current_section = self.get_or_create_section(section_name)
        elif directive == '.space':
            if not self.current_section:
                self.current_section = self.get_or_create_section('data')
            if len(parts) < 2:
                raise ValueError(f"Line {line_num}: .space requires length argument")
            length = int(parts[1], 0)
            self.current_section.add_data(bytes(length))
        elif directive == '.ascii':
            if not self.current_section:
                self.current_section = self.get_or_create_section('data')
            if len(parts) < 2:
                raise ValueError(f"Line {line_num}: .ascii requires string argument")
            string_part = ' '.join(parts[1:])
            text = self.parse_string_literal(string_part)
            self.current_section.add_data(text.encode('utf-8'))
        elif directive == '.asciiz':
            if not self.current_section:
                self.current_section = self.get_or_create_section('data')
            if len(parts) < 2:
                raise ValueError(f"Line {line_num}: .asciiz requires string argument")
            string_part = ' '.join(parts[1:])
            text = self.parse_string_literal(string_part)
            self.current_section.add_data(text.encode('utf-8') + b'\0')
        elif directive == '.set':
            if len(parts) < 3:
                raise ValueError(f"Line {line_num}: .set requires name and value")
            name = parts[1].rstrip(',')
            value = int(parts[2], 0)
            self.symbols[name] = value
        elif directive == '.global':
            if len(parts) < 2:
                raise ValueError(f"Line {line_num}: .global requires symbol name")
            symbol = parts[1]
            self.global_symbols.add(symbol)
        elif directive == '.align':
            if not self.current_section:
                self.current_section = self.get_or_create_section('text')
            if len(parts) >= 2:
                alignment = int(parts[1], 0)
                self.current_section.align(alignment)
        else:
            raise ValueError(f"Line {line_num}: Unknown directive: {directive}")

def sign_extend(value, bits):
    if value & (1 << (bits - 1)):
        value -= 1 << bits
    return value

def parse_mem_operand(operand):
    match = re.match(r'(-?\d+)\((\w+)\)', operand)
    if not match:
        raise ValueError(f"Invalid memory operation format {operand}")
    else:
        imm = int(match.group(1), 0)
        rs1 = match.group(2)
        return imm, rs1

def encode_r_type(opcode, rd, funct3, rs1, rs2, funct7=0):
    return (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode

def encode_i_type(opcode, rd, funct3, rs1, imm):
    return ((imm & 0xfff) << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode

def encode_s_type(opcode, rs1, rs2, imm, funct3):
    imm11to5 = (imm >> 5) & 0x7f
    imm4to0 = imm & 0x1f
    return (imm11to5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm4to0 << 7) | opcode

def encode_b_type(opcode, rs1, rs2, imm, funct3):
    imm12 = (imm >> 12) & 0x1
    imm10to5 = (imm >> 5) & 0x3f
    imm4to1 = (imm >> 1) & 0xf
    imm11 = (imm >> 11) & 0x1
    return (imm12 << 31) | (imm10to5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm4to1 << 8) | (imm11 << 7) | opcode

def encode_j_type(opcode, rd, imm):
    imm20 = (imm >> 20) & 0x1
    imm10_1 = (imm >> 1) & 0x3ff
    imm11 = (imm >> 11) & 0x1
    imm19_12 = (imm >> 12) & 0xff
    return (imm20 << 31) | (imm19_12 << 12) | (imm11 << 20) | (imm10_1 << 21) | (rd << 7) | opcode

def reg_num(reg):
    if reg in REGISTER_MAP:
        return REGISTER_MAP[reg]
    else:
        raise ValueError(f"Invalid register name: {reg}")

def assemble(input_file):
    name, ext = os.path.splitext(input_file)
    if ext != '.s':
        raise ValueError("Input file must have .s extension")
    
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    assembler = Assembler()
    
    for line_num, line in enumerate(lines, 1):
        original_line = line
        line = line.split('#')[0].strip()
        if not line:
            continue
            
        if ':' in line:
            colon_pos = line.find(':')
            label_part = line[:colon_pos].strip()
            rest_part = line[colon_pos+1:].strip()
            
            if not assembler.current_section:
                assembler.current_section = assembler.get_or_create_section('text')
            assembler.current_section.add_label(label_part)
            
            if rest_part:
                original_rest = original_line.split('#')[0]
                original_colon_pos = original_rest.find(':')
                original_rest = original_rest[original_colon_pos+1:].strip()
                
                if rest_part.startswith('.'):
                    original_parts = original_rest.replace(",", "").split()
                    assembler.process_pseudo_op(original_parts, line_num)
                else:
                    rest_lower = rest_part.lower()
                    parts = rest_lower.replace(",", "").split()
                    if parts and parts[0] in INSTRUCTION_SET:
                        if not assembler.current_section:
                            assembler.current_section = assembler.get_or_create_section('text')
                        assembler.current_section.add_data(bytes(4))
        elif line.startswith('.'):
            original_parts = original_line.split('#')[0].strip().replace(",", "").split()
            assembler.process_pseudo_op(original_parts, line_num)
        else:
            line_lower = line.lower()
            parts = line_lower.replace(",", "").split()
            if parts and parts[0] in INSTRUCTION_SET:
                if not assembler.current_section:
                    assembler.current_section = assembler.get_or_create_section('text')
                assembler.current_section.add_data(bytes(4))
    
    all_labels = {}
    for section in assembler.sections.values():
        all_labels.update(section.labels)
    all_labels.update(assembler.symbols)
    
    assembler.current_section = None
    section_positions = {name: 0 for name in assembler.sections.keys()}
    
    for line_num, line in enumerate(lines, 1):
        original_line = line
        line = line.split('#')[0].strip()
        if not line:
            continue
            
        if line.startswith('.'):
            original_parts = original_line.split('#')[0].strip().replace(",", "").split()
            assembler.process_pseudo_op(original_parts, line_num)
        elif line.endswith(":"):
            continue
        else:
            line_lower = line.lower()
            parts = line_lower.replace(",", "").split()
            
            if parts and parts[0] in INSTRUCTION_SET:
                if not assembler.current_section:
                    assembler.current_section = assembler.get_or_create_section('text')
                    
                section = assembler.current_section
                pos = section_positions[section.name]
                pc = section.start_addr + pos
                
                instr_info = INSTRUCTION_SET[parts[0]]
                opcode = instr_info['opcode']
                instruction = 0
                
                if instr_info['type'] == 'R':
                    rd = reg_num(parts[1])
                    rs1 = reg_num(parts[2])
                    rs2 = reg_num(parts[3])
                    funct3 = instr_info['funct3']
                    funct7 = instr_info.get('funct7', 0)
                    instruction = encode_r_type(opcode, rd, funct3, rs1, rs2, funct7)
                elif instr_info['type'] == 'I':
                    rd = reg_num(parts[1])
                    if parts[0].startswith('l'):
                        imm, rs1 = parse_mem_operand(parts[2])
                        rs1 = reg_num(rs1)
                    else:
                        rs1 = reg_num(parts[2])
                        try:
                            imm = int(parts[3], 0)
                        except ValueError:
                            if parts[3] in all_labels:
                                imm = all_labels[parts[3]]
                            else:
                                raise ValueError(f"Line {line_num}: Unknown symbol: {parts[3]}")
                                
                    if parts[0] in ['slli', 'srli', 'srai']:
                        if not 0 <= imm <= 31:
                            raise ValueError(f"Line {line_num}: Shift amount must be 0-31, got {imm}")
                        funct7 = instr_info['funct7']
                        imm = (funct7 << 5) | (imm & 0x1f)
                    else:
                        if not -2048 <= imm <= 2047:
                            if parts[3] not in all_labels:
                                raise ValueError(f"Line {line_num}: I-type immediate out of range: {imm}")
                        imm = imm & 0xfff
                    funct3 = instr_info['funct3']
                    instruction = encode_i_type(opcode, rd, funct3, rs1, imm)
                elif instr_info['type'] == 'S':
                    rs2 = reg_num(parts[1])
                    imm, rs1_str = parse_mem_operand(parts[2])
                    rs1 = reg_num(rs1_str)
                    if not -2048 <= imm <= 2047:
                        raise ValueError(f"Line {line_num}: S-type immediate out of range")
                    funct3 = instr_info['funct3']
                    instruction = encode_s_type(opcode, rs1, rs2, imm, funct3)
                elif instr_info['type'] == 'B':
                    rs1 = reg_num(parts[1])
                    rs2 = reg_num(parts[2])
                    try:
                        imm = int(parts[3])
                    except ValueError:
                        label = parts[3]
                        if label not in all_labels:
                            raise ValueError(f"Line {line_num}: Unknown label: {label}")
                        imm = all_labels[label] - pc
                        if imm % 2 != 0:
                            raise ValueError(f"Line {line_num}: Branch target address must be multiple of 2")
                    if not -4096 <= imm <= 4094:
                        raise ValueError(f"Line {line_num}: B-type immediate out of range")
                    funct3 = instr_info['funct3']
                    instruction = encode_b_type(opcode, rs1, rs2, imm, funct3)
                elif instr_info['type'] == 'U':
                    rd = reg_num(parts[1])
                    try:
                        imm = int(parts[2], 0)
                    except ValueError:
                        if parts[2] in all_labels:
                            imm = all_labels[parts[2]] >> 12
                        else:
                            raise ValueError(f"Line {line_num}: Unknown symbol: {parts[2]}")
                    instruction = ((imm & 0xfffff) << 12) | (rd << 7) | opcode
                elif instr_info['type'] == 'J':
                    rd = reg_num(parts[1])
                    try:
                        imm = int(parts[2], 0)
                        imm = sign_extend(imm, 21)
                    except ValueError:
                        label = parts[2]
                        if label not in all_labels:
                            raise ValueError(f"Line {line_num}: Unknown label: {label}")
                        imm = all_labels[label] - pc
                        if imm % 2 != 0:
                            raise ValueError(f"Line {line_num}: Jump target address must be multiple of 2")
                    if not -1048576 <= imm <= 1048575:
                        raise ValueError(f"Line {line_num}: J-type immediate out of range")
                    instruction = encode_j_type(opcode, rd, imm)
                elif instr_info['type'] == 'SYS':
                    if parts[0] == 'ecall':
                        instruction = 0x00000073
                    elif parts[0] == 'ebreak':
                        instruction = 0x00100073
                
                instr_bytes = instruction.to_bytes(4, byteorder='little')
                for i, byte in enumerate(instr_bytes):
                    section.data[pos + i] = byte
                section_positions[section.name] += 4
    
    output_data = bytearray()
    
    if 'text' in assembler.sections:
        text_section = assembler.sections['text']
        output_data.extend(text_section.data)
    
    if 'data' in assembler.sections:
        data_section = assembler.sections['data']
        current_len = len(output_data)
        if current_len < assembler.data_start_addr:
            padding = assembler.data_start_addr - current_len
            output_data.extend(bytes(padding))
        output_data.extend(data_section.data)
    
    with open(f"{name}.bin", "wb") as bin_file:
        bin_file.write(output_data)
    
    with open(f"{name}.sym", "w") as sym_file:
        sym_file.write("# Symbol Table\n")
        sym_file.write("# Format: symbol_name address section\n")
        for section_name, section in assembler.sections.items():
            for label, address in section.labels.items():
                global_marker = " (global)" if label in assembler.global_symbols else ""
                sym_file.write(f"{label} 0x{address:08x} {section_name}{global_marker}\n")
        
        for symbol, value in assembler.symbols.items():
            global_marker = " (global)" if symbol in assembler.global_symbols else ""
            sym_file.write(f"{symbol} 0x{value:08x} constant{global_marker}\n")
    
    return f"Assembly completed: {name}.bin ({len(output_data)} bytes), {name}.sym"