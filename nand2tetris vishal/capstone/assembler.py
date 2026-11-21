import sys
import os

PREDEFINED_SYMBOLS = {
    "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
    "SCREEN": 16384, "KBD": 24576,
    **{f"R{i}": i for i in range(16)}
}

DEST_TABLE = {
    "": "000", "M": "001", "D": "010", "MD": "011",
    "A": "100", "AM": "101", "AD": "110", "AMD": "111"
}

JUMP_TABLE = {
    "": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"
}

COMP_TABLE = {
    # a = 0
    "0": "0101010",   "1": "0111111",   "-1": "0111010",
    "D": "0001100",   "A": "0110000",   "!D": "0001101",
    "!A": "0110001",  "-D": "0001111",  "-A": "0110011",
    "D+1": "0011111", "A+1": "0110111", "D-1": "0001110",
    "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
    "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
    # a = 1
    "M": "1110000",   "!M": "1110001",  "-M": "1110011",
    "M+1": "1110111", "M-1": "1110010", "D+M": "1000010",
    "D-M": "1010011", "M-D": "1000111", "D&M": "1000000",
    "D|M": "1010101"
}


def clean_line(line):
    """Remove comments and all whitespace from a line."""
    line = line.split("//")[0]
    return "".join(line.split())


def assemble(asm_path):
    with open(asm_path, "r") as f:
        raw_lines = f.readlines()

    symbol_table = dict(PREDEFINED_SYMBOLS)
    user_symbols = {}  # Tracks labels and variables for symbols.txt (K mod 3 == 0)

    instructions = []
    rom_address = 0

    for raw in raw_lines:
        line = clean_line(raw)
        if not line:
            continue
        if line.startswith("(") and line.endswith(")"):
            label = line[1:-1]
            symbol_table[label] = rom_address
            user_symbols[label] = rom_address
        else:
            instructions.append(line)
            rom_address += 1

    hack_lines = []
    next_var_address = 16

    for inst in instructions:
        if inst.startswith("@"):
            symbol = inst[1:]
            if symbol.isdigit():
                addr = int(symbol)
            else:
                if symbol not in symbol_table:
                    symbol_table[symbol] = next_var_address
                    user_symbols[symbol] = next_var_address
                    next_var_address += 1
                addr = symbol_table[symbol]
            hack_lines.append(f"0{addr:015b}")
        else:
            dest, comp, jump = "", inst, ""
            if "=" in comp:
                dest, comp = comp.split("=", 1)
            if ";" in comp:
                comp, jump = comp.split(";", 1)

            bits = "111" + COMP_TABLE[comp] + DEST_TABLE[dest] + JUMP_TABLE[jump]
            hack_lines.append(bits)

    out_path = os.path.splitext(asm_path)[0] + ".hack"
    with open(out_path, "w") as f:
        f.write("\n".join(hack_lines) + "\n")

    # Extra feature (K = 12 -> 12 mod 3 == 0): Save labels & variables to symbols.txt
    symbols_path = os.path.join(os.path.dirname(os.path.abspath(asm_path)), "symbols.txt")
    with open(symbols_path, "w") as f:
        for name, addr in user_symbols.items():
            f.write(f"{name} = {addr}\n")

    print(f"Assembled {len(hack_lines)} instructions -> {out_path}")
    print(f"Saved {len(user_symbols)} labels/variables -> {symbols_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python assembler.py <file.asm>")
        sys.exit(1)
    assemble(sys.argv[1])