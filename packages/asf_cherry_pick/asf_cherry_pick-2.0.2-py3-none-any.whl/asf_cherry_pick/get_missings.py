#!/usr/bin/env python3

"""
Does a diff between two sets to check missing elements.
Basically makes the same as the comm command.

Sets are built either from a filename or as a list of elements in a directory.

If input are not formated in the same way, user can provide a regex to select
the elements that will be compared.


Examples:

=========

Suppose file D041_urls.txt contains lines like

https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20220523T123454_20220523T123520_043338_052CE2_EDD3.zip
https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20220523T123429_20220523T123456_043338_052CE2_6C68.zip
https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__1SDV_20220523T123404_20220523T123431_043338_052CE2_5FAF.zip

and directory SAFE_D041 contains directories like
SAFE_D041/S1A_IW_SLC__1SDV_20220523T123454_20220523T123520_043338_052CE2_EDD3.SAFE
SAFE_D041/S1A_IW_SLC__1SDV_20170218T123330_20170218T123357_015338_01926D_76B4.SAFE
SAFE_D041/S1A_IW_SLC__1SDV_20170218T123355_20170218T123422_015338_01926D_3DDE.SAFE
SAFE_D041/S1A_IW_SLC__1SDV_20170218T123420_20170218T123452_015338_01926D_787F.SAFE
SAFE_D041/S1A_IW_SLC__1SDV_20170302T123330_20170302T123357_015513_0197BE_2F8E.SAFE

Looking at the first lines we want to match the
S1A_IW_SLC__1SDV_20220523T123454_20220523T123520_043338_052CE2_EDD3

We provide the script with two inputs (input a and input b). For each input, we need to provide
if we will list a director or a file. Finally we need to provide a pattern to match. Pattern
will follow the python regex. The first set of parenthesis define the part that will be
compared.

The script will output all the patterns that are in a and not in b. The last option allows the
user to add a prefix (option -P) and a suffix (option -S) to the found names

Here is a full example:

get_missings.py           # name of the script
-a D041_urls.txt          # input a
-ta f                     # type of a is f, ie a file
-b SAFE_D041              # input b
-tb d                     # type of b is a directory
-pa '.*/(.*).zip'         # pattern of a: skip all everything up to the last /
                          # then grab everything up to pattern .zip
-pb 'SAFE_D041/(.*).SAFE' # grab everything after SAFE_D041/ up to .SAFE
-P 'https://datapool.asf.alaska.edu/SLC/SA/' -S '.zip'

"""

# classical imports
import argparse
import logging
# import numpy as np
from pathlib import Path
import sys
import re

# import matplotlib.pyplot as plt
# if "GDAL_SYS" in os.environ and os.environ["GDAL_SYS"] == 'True':
#    from osgeo import gdal
# else:
#    import nsbas.gdal as gdal
# gdal.UseExceptions()

logger = logging.getLogger(__name__)

def filter(str_list, pattern):
    for elem in str_list:
        m = pattern.search(elem)
        if m:
            yield m[1]

def get_matching_dirs(directory, pattern):
    str_dirs = [str(x) for x in directory.glob("*")]
    res = set(filter(str_dirs, pattern))
    return res

def get_matching_lines(filename, pattern):
    res = set()
    with open(filename) as _f:
        res = set(filter(_f.readlines(), pattern))
    return res

def main():
    parser = argparse.ArgumentParser(description="extract missing data from a target list, given a directory where fetched data lies")
    parser.add_argument("-a", type=str,
                        help="(str) input set a")
    parser.add_argument("-ta", type=str, choices=['f', 'd'],
                        help="(str) type of the input 1, f(ile), d(irectory)")
    parser.add_argument("-b", type=str,
                        help="(str) input set b")
    parser.add_argument("-tb", type=str, choices=['f', 'd'],
                        help="(str) type of the input 2, f(ile), d(irectory)")
    parser.add_argument("-pa", type=str,
                        help="(str, regex) pattern for input 1")
    parser.add_argument("-pb", type=str,
                        help="(str, regex) pattern for input 2")
    parser.add_argument("-P", type=str, default="",
                        help="Prefix to use when printing the missing elems")
    parser.add_argument("-S", type=str, default="",
                        help="Suffix to use when printing the missing elems")
    parser.add_argument("-H", action="store_true",
                        help="provide more detailed help")
    parser.add_argument("-v", type=int, default=3,
                        help=("set logging level:"
                              "0 critical, 1 error, 2 warning,"
                              "3 info, 4 debug, default=info"))
    if "-H" in sys.argv:
        print(__doc__)
        sys.exit(0)
    args = parser.parse_args()
    logging_translate = [logging.CRITICAL, logging.ERROR, logging.WARNING,
                         logging.INFO, logging.DEBUG]
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging_translate[args.v])
    script_base_name = Path(__file__).name
    logger = logging.getLogger(script_base_name + ":main")
    cmd_line = ' '.join(sys.argv)
    logger.info(f"called as {cmd_line}")
    input_1 = args.a
    input_2 = args.b
    pattern1 = re.compile(args.pa)
    pattern2 = re.compile(args.pb)
    if args.ta == "d":
        path_1 = Path(input_1)
        input_1_set = get_matching_dirs(path_1, pattern1)
    else:
        input_1_set = get_matching_lines(input_1, pattern1)
    if args.tb == "d":
        path_2 = Path(input_2)
        input_2_set = get_matching_dirs(path_2, pattern2)
    else:
        input_2_set = get_matching_lines(input_2, pattern2)
    missings = input_1_set - input_2_set
    for elem in missings:
        print(f"{args.P}{elem}{args.S}")
    sys.exit(0)

if __name__ == "__main__":
    main()
