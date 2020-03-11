# Copyright (c) 2016, Jeffrey Pfau
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""Create a C source and header file out of one or more binaries"""

import argparse
import os.path
import re
import struct
import sys

header = """/* Auto-generated by bin2c.py */
#include <stddef.h>

"""


def output_bin(in_name, h, c, block_size=16, indent="\t"):
    basename = os.path.basename(in_name)
    symbol_name = re.sub(r"\W", "_", basename)

    print("extern const unsigned char {}_start[];".format(symbol_name), file=h)
    print("extern const size_t {}_size;".format(symbol_name), file=h)
    print("const unsigned char {}_start[] = {{".format(symbol_name), file=c)
    with open(in_name, "rb") as i:
        block = i.read(block_size)
        while block:
            print(indent,
                  (" ".join("0x{:02X}," for _ in range(len(block))))\
                  .format(*struct.unpack("B" * len(block), block)),
                  sep="", file=c)
            block = i.read(block_size)
    print("};", file=c)
    print("const size_t {0}_size = sizeof({0}_start);".format(symbol_name), file=c)


def output_set(out_name, in_names, **kwargs):
    with open(out_name + ".h", "w") as h, open(out_name + ".c", "w") as c:
        hname = re.sub(r"\W", "_", out_name).upper()
        print("#ifndef _{0}_H".format(hname), file=h)
        print("#define _{0}_H".format(hname), file=h)
        h.write(header)
        c.write(header)

        for in_name in in_names:
            output_bin(in_name, h, c, **kwargs)
        print("", file=h)
        print("#endif", file=h)


def _main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-o', metavar="OUTPUT", type=str,
                        help="output file basename")
    parser.add_argument('-b', '--block-size', metavar="INT", type=int,
                        help="number of spaces to indent (default \\t)")
    parser.add_argument('-i', '--indent', metavar="INT", default=-1, type=int,
                        help="number of bytes per line")
    parser.add_argument('input', type=str, nargs='+', help="input files")
    args = parser.parse_args()
    if not args:
        sys.exit(1)
    indent = " " * args.indent if args.indent >= 0 else "\t"
    if not args.o:
        for in_name in args.input:
            output_set(in_name, [in_name],
                       block_size=args.block_size, indent=indent)
    else:
        output_set(args.o, args.input, block_size=args.block_size)

if __name__ == "__main__":
    _main()
