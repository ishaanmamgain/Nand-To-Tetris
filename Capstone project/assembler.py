#!/usr/bin/env python3
"""Hack assembler.  Usage: python assembler.py InputFile.asm  ->  InputFile.hack
Author: Ishaan Mamgain (2501730241)
Extra feature (K=41, K mod 3 = 2): warn when the same label is declared twice.
"""
import os
import sys

COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "!D": "0001101", "!A": "0110001",
    "-D": "0001111", "-A": "0110011", "D+1": "0011111", "A+1": "0110111",
    "D-1": "0001110", "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
    "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
    "M": "1110000", "!M": "1110001", "-M": "1110011", "M+1": "1110111",
    "M-1": "1110010", "D+M": "1000010", "D-M": "1010011", "M-D": "1000111",
    "D&M": "1000000", "D|M": "1010101",
}
# commutative aliases
for _k, _v in [("A+D", "D+A"), ("A&D", "D&A"), ("A|D", "D|A"),
               ("M+D", "D+M"), ("M&D", "D&M"), ("M|D", "D|M")]:
    COMP[_k] = COMP[_v]
COMP["D|M"] = "1010101"

JUMP = {"": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
        "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"}

PREDEFINED = {"SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
              "SCREEN": 16384, "KBD": 24576}
PREDEFINED.update({f"R{i}": i for i in range(16)})


def clean(line):
    """Remove comments and all whitespace."""
    return "".join(line.split("//")[0].split())


def dest_bits(dest):
    return "".join("1" if ch in dest else "0" for ch in "ADM")


def pass1(lines):
    """Record label addresses, return (symbols, instructions[(text, src_line)])."""
    symbols = dict(PREDEFINED)
    label_lines = {}                       # label -> list of source lines
    instructions = []
    for lineno, raw in enumerate(lines, start=1):
        text = clean(raw)
        if not text:
            continue
        if text.startswith("(") and text.endswith(")"):
            name = text[1:-1]
            label_lines.setdefault(name, []).append(lineno)
            occ = len(label_lines[name])
            if occ > 1:
                print(f"WARNING: label '{name}' declared more than once "
                      f"(occurrence #{occ} at line {lineno}; first declared at "
                      f"line {label_lines[name][0]}). Keeping the first address.",
                      file=sys.stderr)
            else:
                symbols[name] = len(instructions)
        else:
            instructions.append((text, lineno))
    return symbols, instructions


def pass2(symbols, instructions):
    out = []
    next_var = 16
    for text, lineno in instructions:
        if text.startswith("@"):
            sym = text[1:]
            if sym.isdigit():
                value = int(sym)
            else:
                if sym not in symbols:
                    symbols[sym] = next_var
                    next_var += 1
                value = symbols[sym]
            out.append(format(value, "016b"))
        else:
            dest, jump = "", ""
            comp = text
            if "=" in comp:
                dest, comp = comp.split("=", 1)
            if ";" in comp:
                comp, jump = comp.split(";", 1)
            if comp not in COMP or jump not in JUMP:
                raise SyntaxError(f"line {lineno}: cannot assemble '{text}'")
            out.append("111" + COMP[comp] + dest_bits(dest) + JUMP[jump])
    return out


def main():
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".asm"):
        print("Usage: python assembler.py InputFile.asm")
        sys.exit(1)
    src = sys.argv[1]
    with open(src) as f:
        lines = f.readlines()
    symbols, instructions = pass1(lines)
    binary = pass2(symbols, instructions)
    dst = os.path.splitext(src)[0] + ".hack"
    with open(dst, "w") as f:
        f.write("\n".join(binary) + "\n")
    print(f"Wrote {len(binary)} instructions to {dst}")


if __name__ == "__main__":
    main()
