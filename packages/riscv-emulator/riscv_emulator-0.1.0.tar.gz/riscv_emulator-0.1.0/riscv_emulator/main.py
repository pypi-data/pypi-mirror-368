import argparse
from riscv_emulator.assembler import assemble
from riscv_emulator.emulator import emulator
from riscv_emulator.disassembler import disassemble

def main():
    parser = argparse.ArgumentParser(
        description="RISC-V Emulator CLI"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    assemble_parser = subparsers.add_parser("assemble", help="Assemble a .s file into a binary")
    assemble_parser.add_argument("input", help="Input assembly file (.s)")

    run_parser = subparsers.add_parser("run", help="Run a binary file in the emulator")
    run_parser.add_argument("binary", help="Binary file to run")

    full_parser = subparsers.add_parser("full", help="Assemble and run a file in one step")
    full_parser.add_argument("input", help="Input assembly file (.s)")

    dis_parser = subparsers.add_parser("disassemble", help="Disassemble a binary file")
    dis_parser.add_argument("hexcode", help="Hexcode to disassemble")

    args = parser.parse_args()

    if args.command == "assemble":
        assemble(args.input)

    elif args.command == "run":
        emu = emulator()
        emu.load_program(args.binary)
        emu.run()

    elif args.command == "full":
        assemble(args.input)
        emu = emulator()
        bin_file = args.input.rsplit(".", 1)[0] + ".bin"
        emu.load_program(bin_file)
        emu.run()
        emu.debug()

    elif args.command == "disassemble":
        print(disassemble(args.hexcode))

if __name__ == "__main__":
    main()
