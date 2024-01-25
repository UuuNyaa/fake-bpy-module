import os

from parsy import ParseError

import sys


SCRIPT_FILE = os.path.abspath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_FILE)

p = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "..", "src"))
print(p)
sys.path.append(p)


from parse_sphinx import parse_type

parse_type.DATA_TYPE.parse("!!!!!! (dict mapping vert/edge/face types to float) - Undocumented.")

INPUT_DATA_FILE = os.path.join(SCRIPT_DIR, "blender-4.0-data_types.log")

with open(INPUT_DATA_FILE, "rt", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        try:
            parse_type.DATA_TYPE.parse(line)
            # print(f"{DATA_TYPE.parse(line)}\t{line}")
        except ParseError as e:
            print(f"\t{line}")
