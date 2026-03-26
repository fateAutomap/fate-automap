import os
import re


# ------------------------------------------------------------
# Read value depending on mode
# ------------------------------------------------------------

def read_value(data, addr, size):

    if size == 1:
        return data[addr]

    if size == 2:
        return (data[addr] << 8) | data[addr+1]

    if size == 4:
        return (
            (data[addr]   << 24) |
            (data[addr+1] << 16) |
            (data[addr+2] << 8)  |
            data[addr+3]
        )


# ------------------------------------------------------------
# Parse comparison line
# ------------------------------------------------------------

def parse_rule(line):

    ops = ["<<", ">>", "==", "!=", ">=", "<="]

    for op in ops:
        if op in line:
            left, right = line.split(op)
            return left.strip(), op, right.strip()

    raise ValueError(f"Invalid rule: {line}")


# ------------------------------------------------------------
# Apply comparison rule
# ------------------------------------------------------------

def test_rule(v1, v2, op):

    if op == ">>":
        return v1 > v2

    if op == "<<":
        return v1 < v2

    if op == "==":
        return v1 == v2

    if op == "!=":
        return v1 != v2

    if op == ">=":
        return v1 >= v2

    if op == "<=":
        return v1 <= v2


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():

    instruction_file = input("Instruction filename: ")

    with open(instruction_file) as f:
        lines = [x.strip() for x in f if x.strip()]

    mode = lines[0].lower()

    if mode == "byte":
        size = 1
        label = "bytes"

    elif mode == "word":
        size = 2
        label = "words"

    elif mode == "dword":
        size = 4
        label = "dwords"

    else:
        raise ValueError("First line must be byte, word, or dword")

    rules = []

    for line in lines[1:]:
        f1, op, f2 = parse_rule(line)
        rules.append((f1, op, f2))

    # --------------------------------------------------------

    files = set()

    for f1, op, f2 in rules:
        files.add(f1)
        files.add(f2)

    files = sorted(files)

    datasets = {}

    for f in files:
        with open(f, "rb") as fh:
            datasets[f] = fh.read()

    file_size = len(next(iter(datasets.values())))

    max_addr = file_size - (size - 1)

    addresses = list(range(max_addr))

    print("Initial candidates:", len(addresses))

    # --------------------------------------------------------

    for f1, op, f2 in rules:

        data1 = datasets[f1]
        data2 = datasets[f2]

        new_addresses = []

        for addr in addresses:

            v1 = read_value(data1, addr, size)
            v2 = read_value(data2, addr, size)

            if test_rule(v1, v2, op):
                new_addresses.append(addr)

        addresses = new_addresses

        print(f"{f1} {op} {f2} -> remaining {len(addresses)}")

        if not addresses:
            break

    # --------------------------------------------------------
    # Write matrix
    # --------------------------------------------------------

    with open("comparison.txt", "w") as out:

        out.write(f"{len(addresses)} {label}\n\n")

        header = "ADDRESS   "

        for f in files:
            header += f"{f}   "

        out.write(header + "\n")

        for addr in addresses:

            row = f"0x{addr:05X} "

            for f in files:

                val = read_value(datasets[f], addr, size)

                if size == 1:
                    row += f" {val:02X} "

                elif size == 2:
                    row += f" {val:04X} "

                else:
                    row += f" {val:08X} "

            out.write(row.rstrip() + "\n")

    print("\nSaved comparison.txt")


# ------------------------------------------------------------

if __name__ == "__main__":
    main()
