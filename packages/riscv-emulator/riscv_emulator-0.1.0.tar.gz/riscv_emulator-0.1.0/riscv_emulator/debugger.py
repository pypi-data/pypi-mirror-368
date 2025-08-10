from riscv_emulator.disassembler import disassemble

ABI_REGS = ['zero', 'ra', 'sp', 'gp', 'tp', 't0', 't1', 't2', 's0', 's1', 'a0', 'a1', 'a2', 'a3', 'a4',
    'a5', 'a6', 'a7', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11', 't3', 't4', 't5', 't6']

def debugger(emu) :
    print("\nEntered Debugger - type 'help' for options.")
    while True:
        cmd = input(">>> ").strip().lower()
        if cmd == "help":
            print("Available commands:")
            print(" regs    →   show all registers (type 'abi'/'numreg' for alternate register output format)")
            print(" mem [addr]    →   show 16 bytes from memory at [addr]")
            print(" dsm [hexcode]    →   disassemble [hexcode] to assembly")
            print(" pc    →   show current program counter")
            print(" cont    →   continue execution")
            print(" step    →   one step of instruction")
            print(" exit    →   exit emulator")
        elif cmd == "regs":
            if emu.abi:
                for i in range(32):
                    print(f"{ABI_REGS[i]} = {emu.rg[i]}")
            else:
                for i in range(32):
                    print(f"x{i} = {emu.rg[i]}")
        elif cmd == "abi":
            emu.abi = True
            print("Swapped to ABI register naming")
        elif cmd == "numreg":
            emu.abi = False
            print("Swapped to numerical register naming")
        elif cmd.startswith("mem"):
            try:
                addr = int(cmd.split()[1], 0)
                dump_memory(addr, emu.memory)
            except:
                print("Invalid address.")
        elif cmd.startswith("dsm"):
            parts = cmd.split()
            if (len(parts) < 2):
                print("Usage: dsm [hexcode] [count]")
            else:
                try:
                    hexcode = parts[1]
                    if (hexcode.startswith("0x")):
                        hexcode = hexcode.removeprefix("0x")
                    if len(hexcode) != 8:
                        raise ValueError("Hexcode must be exactly 8 hex digits (4 bytes).")
                    print(disassemble(hexcode))
                except Exception as e:
                    print("Error in dsm:", e)
        elif cmd == "pc":
            print(f"PC = {emu.pc:#x}")
        elif cmd == "cont":
            break
        elif cmd == "step":
            instr = int.from_bytes(emu.memory[emu.pc:emu.pc+4], byteorder='little')
            emu.execute(instr)
            print(f"Stepped one instruction to PC = {emu.pc:#x}")
        elif cmd == "exit":
            print("Exiting emulator...")
            exit()
        else:
            print("Command not recognized.")

def dump_memory(addr, memory, length=16):
    print(f"Memory at {hex(addr)}:")
    for i in range(0, length, 4):
        chunk = memory[addr+i:addr+i+4]
        val = int.from_bytes(chunk, byteorder='little')
        print(f" {hex(addr+i)}: {val:08x}")