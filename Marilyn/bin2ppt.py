#! /usr/bin/env python3
# Print out the contents of a paper tape binary file
#  As a pattern of holes
#  Optionally:
#  --ascii
#    Hex
#    7-bit ASCII (strip 7th parity bit)
#  --bcd
#    Monrobot machine format - parity bit moved
#    Monrobot BCD character
#  --monrobot
#    Monrobot machine format - parity bit moved
#  And:
#  --ut1
#    Decode as Monrobot UT-1 format tape
#  And:
#  --even
#  --odd
#    Parity error indicator  

import sys
import argparse
from curses.ascii import controlnames

# Monrobot character set
BCD=[" ","1","2","3","4","5","6","7","8","9","~","#","@",":",">","~",
     "0","/","S","T","U","V","W","X","Y","Z","+",",","%","bs","tb",'"',
     "-","J","K","L","M","N","O","P","Q","R","!","$","*",")",";","~",
     "&","A","B","C","D","E","F","G","H","I","lc",".","uc","(","<","cr"]
hexdigit = "abcdefABCDEF"
sexdigit = "STUVWXSTUVWX"
hextosex = str.maketrans(hexdigit, sexdigit)

def mach_to_ext(mach):
    # WRITE ME
    pass

def ext_to_mach(ext):
   # mach = (ext& 0x8f) | (ext & 0x10) << 2 | (ext & 0x60) >> 1 
   mach = (ext& 0x8f) | (ext & 0x60) >> 1  # Zero Parity bit
   # Don't generate T7-8 Parity Error bit
   return mach

def mach_to_sex(num):
    hexstr = f'{num:02X}'
    return hexstr.translate(hextosex)

def addr_to_sex(num):
    hexstr = f'{num:03X}'
    return hexstr.translate(hextosex)

def hword_to_sex(num):
    hexstr = f'{num:04X}'
    return hexstr.translate(hextosex)

def word_to_sex(num):
    hexstr = f'{num:08X}'
    return hexstr.translate(hextosex)

def word_to_string(word):
    # Characters are packed 6, 6, 6, 6, 6, 2(flag)
    flags = [" ", "|", "}", " "]
    string = ""
    for i in [26, 20, 14, 8, 2]:
        char = (word >> i) & 0x3f
        string += BCD[char]
    flag = word & 0x3
    string += flags[flag]
    return string

# ---
parser = argparse.ArgumentParser(
    prog='bin2ppt',
    description='Pretty print a binary paper tape file')
parser.add_argument('infile', nargs='?', help="binary input file, or STDIN")
parser.add_argument("-t", "--tape", action="store_true", help="decode as holes in a tape")
decode = parser.add_mutually_exclusive_group()
decode.add_argument("-a", "--ascii", action="store_true", help="decode as ASCII")
decode.add_argument("-b", "--bcd", action="store_true", help="decode as Monrobot and BCD")
decode.add_argument("-m", "--monrobot", action="store_true", help="decode as Monrobot only")
parser.add_argument("-u", "--ut1", action="store_true", help="decode as Monrobot program tape")
parity_opt = parser.add_mutually_exclusive_group()
parity_opt.add_argument("-e", "--even", action="store_true", help="check for even parity")
parity_opt.add_argument("-o", "--odd", action="store_true", help="check for odd parity")
args = parser.parse_args()

with open(args.infile, 'rb') if args.infile else sys.stdin.buffer as f:
    tape = f.read()
    rowcount = 0
    state = 0

    for row in tape:
        rowcount += 1
        if row == None:
            break

        line = []
        holes = '|'
        parity = 0
        for i in range(7,-1,-1):
            if row & 1<<i:
                hole = 'o'
                parity ^= 1
            else:
                hole = ' '
            holes += hole
            if i == 3: # add sprocket hole
                holes += '.'
        holes += '|'
        if args.tape:
            line.append(holes)

        if args.ascii:
            byte7 = row & 0x7f
            if byte7 < ord(' '):
                asc = controlnames[byte7]
            elif byte7 <= ord('~'):
                asc = chr(byte7)
            else:
                asc = 'DEL'
            line.append(asc)

        # Needed for printing, and for decoding the tape
        mach = ext_to_mach(row)
        sex = mach_to_sex(mach)

        if mach < len(BCD):
            bcd = BCD[mach]
        elif mach == 0x80:
            bcd = 'CR'
        else:
            bcd = "~"

        if args.monrobot or args.bcd:
            line.append("{:>2}".format(sex))
        if args.bcd:
            line.append("{:>2}".format(bcd))

        if parity == 0 and args.odd:
            line.append("EVEN PARITY")
        elif parity == 1 and args.even:
            line.append("ODD PARITY")

        if line:
            print(" ".join(line)) # Print out all the optional fields

        if args.ut1:
            match state:
                case 0:
                    if sex == "TX":
                        # found Start Code
                        print(f"# Found Start Code at {rowcount}")
                        state = 1
                case 1:
                    addr1 = mach
                    state = 2
                case 2:
                    addr2 = mach
                    addr = addr1 << 6 | addr2
                    print("# Start Address {}".format(addr_to_sex(addr)))
                    state = 3
                case 3:
                    mach1 = mach
                    sex1 = sex
                    state = 4
                    if sex == "S1" or sex == "S0":
                        print(f"# Found End of Data at {rowcount}")
                        state = 9
                case 4:
                    mach2 = mach
                    sex2 = sex
                    state = 5
                case 5:
                    mach3 = mach
                    sex3 = sex
                    state = 6
                case 6:
                    mach4 = mach
                    sex4 = sex
                    state = 7
                case 7:
                    mach5 = mach
                    sex5 = sex
                    state = 8
                case 8:
                    mach6 = mach
                    sex6 = sex
                    addr_sex = addr_to_sex(addr)
                    if mach1 > 0x3f or mach2 > 0x3f or mach3 > 0xf or \
                       mach4 > 0x3f or mach5 > 0x3f or mach6 > 0xf:
                        print("# Extra bits {}: {} {} {} {} {} {}".format(rowcount, sex1, sex2, sex3, sex4, sex5, sex6))
                    # assemble as 6, 6, 4, 6, 6, 4 bits
                    word = ((((mach1 << 6 | mach2) << 4 | mach3) <<6 | mach4) << 6 | mach5) <<4 | mach6
                    word_sex = word_to_sex(word)
                    word_string = word_to_string(word)
                    print("{}: {} {}".format(addr_sex, word_sex, word_string))
                    addr += 1
                    state = 3
                case 9:
                    # trailer - loop
                    state = 9
