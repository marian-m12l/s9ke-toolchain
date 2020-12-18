#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import re
import os
import struct
import sys


SOURCE = './test.asm'
TARGET = './test.bin'
if len(sys.argv) > 1:
    SOURCE = sys.argv[1]
if len(sys.argv) > 2:
    TARGET = sys.argv[2]

def hex(val, digits):
    return "{0:#0{1}x}".format(val, digits+2)

suffixes = ['eq', 'ne', 'gt', 'ge', 'lt', 'le', 'av', 'nav', 'ac', 'nac', 'mr0s', 'mr0ns', 'mv', 'nmv', 'ixv', 'irr']    # FIXME irr unsupported ???
def condcode(suffix):
    return suffixes.index(suffix)

registers_reg = ['x0', 'x1', 'r0', 'r1', 'y0', 'y1', 'mr0', 'mr1']
registers_reg1 = ['x0', 'x1', 'r0', 'r1', 'y0', 'y1', 'ix0', 'ix1']
registers_regL = ['x0', 'x1', 'r0', 'r1']
def regcode(reg):
    return registers_reg.index(reg)
def reg1code(reg):
    return registers_reg1.index(reg)
def regLcode(reg):
    return registers_regL.index(reg)

hilo_suffixes = ['.h', 'N/A', '.l', '']     # FIXME index 0x01 unsupported ?!!
def hilocode(hilo):
    return hilo_suffixes.index(hilo)

operandXop = ['x0', 'x1', 'r0', 'r1']
def op1code(reg):
    return operandXop.index(reg)

operandYop = ['y0', 'y1', 'r0', 'r1']
def op2code(reg):
    return operandYop.index(reg)

modifiers = ['', ', m', ', 1', ', -1']
def modifier(m):
    return modifiers.index(m)

lu1Mnemonics = ['and', 'or', 'xor', 'not']
def lu1code(lu1):
    return lu1Mnemonics.index(lu1)

lu2Mnemonics = ['bclr', 'bset', 'btog', 'btst']
def lu2code(lu2):
    return lu2Mnemonics.index(lu2)

indirectIxy = ['ix0', 'ix1', 'iy0', 'iy1']
def indirectcode(Ixy):
    return indirectIxy.index(Ixy)

shiftMnemonics = ['N/A', 'sl', 'sra', 'srl']   # FIXME Shift Left Sign Extension ???
def shiftcode(sf):
    return shiftMnemonics.index(sf)

pushpopMnemonics = ['push', 'pop']
def pushpopcode(pp):
    return pushpopMnemonics.index(pp)


seekRegex = re.compile('^seek\((0x[0-9a-fA-F]{6})\)$')
labelRegex = re.compile('^(\..+):$')

# First pass: count each opcode's size (1 or 2 words) + account for seek() statements + store labels/address map
address = 0x000000
lineNumber = 1
labels = dict([])
with open(SOURCE) as f:
    line = f.readline()
    while line:
        # Strip comments
        instruction = line.split(';')[0].strip().lower()
        if instruction:
            print(f"Line {lineNumber} ({hex(address, 6)}): {instruction}")
            seekMatch = seekRegex.match(instruction)
            labelMatch = labelRegex.match(instruction)
            if seekMatch:
                seekAddr = int(seekMatch.group(1), 16)
                print(f"Seeking address {hex(seekAddr, 6)}")
                if seekAddr < address:
                    raise Exception(f"Line {lineNumber} ({hex(address, 6)}): seek address ({hex(seekAddr, 6)}) cannot be less than current address")
                address = seekAddr
            elif labelMatch:
                # Store label location for second pass
                label = labelMatch.group(1)
                labels[label] = address
                print(f"Storing address {hex(address, 6)} for label {label}")
            elif instruction.startswith('callff') or instruction.startswith('jmpff'):
                # Two-words instructions
                address += 2
            else:
                address += 1
        line = f.readline()
        lineNumber += 1



callRegex = re.compile('^call (0x[0-9a-fA-F]{4}|\.[^ ]+)$')
jmpRegex = re.compile('^jmp (0x[0-9a-fA-F]{3}|\.[^ ]+)$')
jcondRegex = re.compile('^(j(eq|ne|gt|ge|lt|le|av|nav|ac|nac|mr0s|mr0ns|mv|nmv|ixv|irr)) (0x[0-9a-fA-F]{2}|\.[^ ]+)$')
rwmemRegex1 = re.compile('^([^ ]+) = dm\((0x[0-9a-fA-F]{3})\)$')
rwmemRegex2 = re.compile('^dm\((0x[0-9a-fA-F]{3})\) = ([^ ]+)$')
loadImmRegex = re.compile('^([^ .]+)(.h|.l)? = (0x[0-9a-fA-F]{2})$')
au2Regex1 = re.compile('^ram\(ix(0|1)(, (1|-1|m))?\) = -([^ -]+) \+ ([^ ]+)( \+ c - 1)?$')
au2Regex2 = re.compile('^ram\(ix(0|1)(, (1|-1|m))?\) = ([^ -]+) - ([^ ]+) \+ c - 1$')
au2Regex3 = re.compile('^ram\(ix(0|1)(, (1|-1|m))?\) = ([^ -]+) \+ ([^ ]+) \+ c$')
au2Regex4 = re.compile('^ram\(ix(0|1)(, (1|-1|m))?\) = ([^ -]+) (\+|-) ([^ ]+)$')
lu1Regex1 = re.compile('^([^ ]+) = ([^ ]+) (and|or|xor) ([^ ]+)$')
lu1Regex2 = re.compile('^([^ ]+) = not ([^ ]+)$')
lu2Regex = re.compile('^r(0|1) = (bclr|bset|btog|btst).([0-9]+) ([^ ]+)$')
rwramRegex1 = re.compile('^([^ ]+) = ram\(([^ ,]+)(, (1|-1|m))?\)$')
rwramRegex2 = re.compile('^ram\(([^ ,]+)(, (1|-1|m))?\) = ([^ ]+)$')
romRegex = re.compile('^([^ ]+) = rom\(([^ ,]+)(, (1|-1|m))?\)$')
shiftIdxRegex = re.compile('^r(0|1) = (sl|sra|srl).idx ([^ ]+)$')
io1Regex1 = re.compile('^([^ ]+) = io\((0x[0-9a-fA-F]{2})\)$')
io1Regex2 = re.compile('^io\((0x[0-9a-fA-F]{2})\) = ([^ ]+)$')
au1Regex1 = re.compile('^([^ ]+) = -([^ -]+) \+ ([^ ]+)( \+ c - 1)?$')
au1Regex2 = re.compile('^([^ ]+) = ([^ -]+) - ([^ ]+) \+ c - 1$')
au1Regex3 = re.compile('^([^ ]+) = ([^ -]+) \+ ([^ ]+) \+ c$')
au1Regex4 = re.compile('^([^ ]+) = ([^ -]+) (\+|-) ([^ ]+)$')
regMoveRegex = re.compile('^([^ ]+) = ([^ ]+)$')
pushPopRegex = re.compile('^(push|pop) ([^ ]+)$')
shiftRegex = re.compile('^r(0|1) = (sl|sra|srl).([0-9]+) ([^ ]+)$')
callffRegex = re.compile('^callff (0x[0-9a-fA-F]{6}|\.[^ ]+)$')
jmpffRegex = re.compile('^jmpff (0x[0-9a-fA-F]{6}|\.[^ ]+)$')
retRegex = re.compile('^ret$')
retiRegex = re.compile('^reti$')
retffRegex = re.compile('^retff$')
nopRegex = re.compile('^nop$')

# Second pass: generate opcode for each instruction + write output file
address = 0x000000
lineNumber = 1
with open(SOURCE) as f, open(TARGET,'wb') as output:
    line = f.readline()
    while line:
        # Strip comments
        instruction = line.split(';')[0].strip().lower()
        if instruction:
            print(f"Line {lineNumber} ({hex(address, 6)}): {instruction}")
            seekMatch = seekRegex.match(instruction)
            labelMatch = labelRegex.match(instruction)
            callMatch = callRegex.match(instruction)
            jmpMatch = jmpRegex.match(instruction)
            jcondMatch = jcondRegex.match(instruction)
            rwmem1Match = rwmemRegex1.match(instruction)
            rwmem2Match = rwmemRegex2.match(instruction)
            loadImmMatch = loadImmRegex.match(instruction)
            au21Match = au2Regex1.match(instruction)
            au22Match = au2Regex2.match(instruction)
            au23Match = au2Regex3.match(instruction)
            au24Match = au2Regex4.match(instruction)
            lu11Match = lu1Regex1.match(instruction)
            lu12Match = lu1Regex2.match(instruction)
            lu2Match = lu2Regex.match(instruction)
            rwram1Match = rwramRegex1.match(instruction)
            rwram2Match = rwramRegex2.match(instruction)
            romMatch = romRegex.match(instruction)
            shiftIdxMatch = shiftIdxRegex.match(instruction)
            io11Match = io1Regex1.match(instruction)
            io12Match = io1Regex2.match(instruction)
            au11Match = au1Regex1.match(instruction)
            au12Match = au1Regex2.match(instruction)
            au13Match = au1Regex3.match(instruction)
            au14Match = au1Regex4.match(instruction)
            regMoveMatch = regMoveRegex.match(instruction)
            pushPopMatch = pushPopRegex.match(instruction)
            shiftMatch = shiftRegex.match(instruction)
            callffMatch = callffRegex.match(instruction)
            jmpffMatch = jmpffRegex.match(instruction)
            retMatch = retRegex.match(instruction)
            retiMatch = retiRegex.match(instruction)
            retffMatch = retffRegex.match(instruction)
            nopMatch = nopRegex.match(instruction)
            if seekMatch:
                seekAddr = int(seekMatch.group(1), 16)
                print(f"Seeking address {hex(seekAddr, 6)}")
                if seekAddr < address:
                    raise Exception(f"Line {lineNumber} ({hex(address, 6)}): seek address ({hex(seekAddr, 6)}) cannot be less than current address")
                # Write blank words
                while address < seekAddr:
                    output.write(struct.pack('<H', 0x0000))
                    address += 1
            elif labelMatch:
                pass
            # Call
            elif callMatch:
                dest = callMatch.group(1)
                if dest.startswith('0x'):
                    destAddr = int(dest, 16)
                elif dest.startswith('.'):
                    destAddr = labels[dest]
                    # TODO handle missing label
                    # TODO handle destination out of range (15 bits)
                else:
                    raise Exception(f"Line {lineNumber} ({hex(address, 6)}): invalid destination ({dest}) for instruction call")
                opcode = destAddr & 0x7fff
                output.write(struct.pack('<H', opcode))
                address += 1
            # Jump
            elif jmpMatch:
                dest = jmpMatch.group(1)
                if dest.startswith('0x'):
                    offset = int(dest, 16)
                elif dest.startswith('.'):
                    offset = labels[dest] - (address + 1)
                    # TODO handle missing label
                    # TODO handle offset out of range (12 bits)
                else:
                    raise Exception(f"Line {lineNumber} ({hex(address, 6)}): invalid destination ({dest}) for instruction jmp")
                opcode = 0x8000 | (offset & 0x0fff)
                output.write(struct.pack('<H', opcode))
                address += 1
            # Jump Condition
            elif jcondMatch:
                cond = jcondMatch.group(2)
                dest = jcondMatch.group(3)
                if dest.startswith('0x'):
                    offset = int(dest, 16)
                elif dest.startswith('.'):
                    offset = labels[dest] - (address + 1)
                    # TODO handle missing label
                    # TODO handle offset out of range (8 bits)
                else:
                    raise Exception(f"Line {lineNumber} ({hex(address, 6)}): invalid destination ({dest}) for instruction {jcondMatch.group(1)}")
                opcode = 0x9000 | (condcode(cond) & 0x0f) << 8 | (offset & 0x00ff)
                output.write(struct.pack('<H', opcode))
                address += 1
            # RW Mem (direct)
            elif rwmem1Match:
                destReg = rwmem1Match.group(1)
                srcAddr = rwmem1Match.group(2)
                addr = int(srcAddr, 16)
                opcode = 0xb000 | (regcode(destReg) & 0x07) << 8 | (addr & 0x0100) << 3 | (addr & 0x00ff)
                output.write(struct.pack('<H', opcode))
                address += 1
            elif rwmem2Match:
                destAddr = rwmem2Match.group(1)
                srcReg = rwmem2Match.group(2)
                addr = int(destAddr, 16)
                opcode = 0xa000 | (regcode(srcReg) & 0x07) << 8 | (addr & 0x0100) << 3 | (addr & 0x00ff)
                output.write(struct.pack('<H', opcode))
                address += 1
            # Load Immediate
            elif loadImmMatch:
                destReg = loadImmMatch.group(1)
                hilo = loadImmMatch.group(2) or ''
                imm = loadImmMatch.group(3)
                value = int(imm, 16)
                opcode = 0xc000 | (hilocode(hilo) & 0x03) << 11 | (reg1code(destReg) & 0x07) << 8 | (value & 0x00ff)
                output.write(struct.pack('<H', opcode))
                address += 1
            # AU(2) To Mem
            elif au21Match:
                destIx = au21Match.group(1)
                modif = au21Match.group(2) or ''
                op1 = au21Match.group(4)
                op2 = au21Match.group(5)
                carry = au21Match.group(6)
                if carry is None:
                    au = 0x6
                else:
                    au = 0x7
                opcode = 0xc800 | (modifier(modif) & 0x03) << 9 | (int(destIx) & 0x01) << 8 | (op1code(op1) & 0x03) << 5 | au << 2 | op2code(op2)
                output.write(struct.pack('<H', opcode))
                address += 1
            elif au22Match:
                destIx = au22Match.group(1)
                modif = au22Match.group(2) or ''
                op1 = au22Match.group(4)
                op2 = au22Match.group(5)
                au = 0x5
                opcode = 0xc800 | (modifier(modif) & 0x03) << 9 | (int(destIx) & 0x01) << 8 | (op1code(op1) & 0x03) << 5 | au << 2 | op2code(op2)
                output.write(struct.pack('<H', opcode))
                address += 1
            elif au23Match:
                destIx = au23Match.group(1)
                modif = au23Match.group(2) or ''
                op1 = au23Match.group(4)
                op2 = au23Match.group(5)
                au = 0x3
                opcode = 0xc800 | (modifier(modif) & 0x03) << 9 | (int(destIx) & 0x01) << 8 | (op1code(op1) & 0x03) << 5 | au << 2 | op2code(op2)
                output.write(struct.pack('<H', opcode))
                address += 1
            elif au24Match:
                destIx = au24Match.group(1)
                modif = au24Match.group(2) or ''
                op1 = au24Match.group(4)
                operation = au24Match.group(5)
                op2 = au24Match.group(6)
                if operation == '+':
                    if op2 == '1':
                        au = 0x0
                        yop = 0x0   # Unused operand 2 is set to 0, as observed in actual firmware
                    else:
                        au = 0x2
                        yop = op2code(op2)
                elif operation == '-':
                    if op2 == '1':
                        au = 0x1
                        yop = 0x0   # Unused operand 2 is set to 0, as observed in actual firmware
                    else:
                        au = 0x4
                        yop = op2code(op2)
                opcode = 0xc800 | (modifier(modif) & 0x03) << 9 | (int(destIx) & 0x01) << 8 | (op1code(op1) & 0x03) << 5 | au << 2 | yop
                output.write(struct.pack('<H', opcode))
                address += 1
            # LU(1)
            elif lu11Match:
                destReg = lu11Match.group(1)
                op1 = lu11Match.group(2)
                operation = lu11Match.group(3)
                op2 = lu11Match.group(4)
                lu1 = lu1code(operation)
                opcode = 0xc880 | (regcode(destReg) & 0x07) << 8 | (op1code(op1) & 0x03) << 5 | lu1 << 3 | op2code(op2)
                output.write(struct.pack('<H', opcode))
                address += 1
            elif lu12Match:
                destReg = lu12Match.group(1)
                op1 = lu12Match.group(2)
                op2 = 0x0   # Unused operand 2 is set to 0, as observed in actual firmware
                lu1 = 0x3
                opcode = 0xc880 | (regcode(destReg) & 0x07) << 8 | (op1code(op1) & 0x03) << 5 | lu1 << 3 | op2
                output.write(struct.pack('<H', opcode))
                address += 1
            # LU(2)
            elif lu2Match:
                destR = lu2Match.group(1)
                operation = lu2Match.group(2)
                bit = lu2Match.group(3)
                opReg = lu2Match.group(4)
                lu2 = lu2code(operation)
                opcode = 0xc884 | (int(destR) & 0x01) << 8 | (int(bit) & 0x0c) << 7 | (int(bit) & 0x03) << 5 | lu2 << 3 | op2code(opReg)
                output.write(struct.pack('<H', opcode))
                address += 1
            # RW SRAM (indirect)
            elif rwram1Match:
                destReg = rwram1Match.group(1)
                indirectReg = rwram1Match.group(2)
                modif = rwram1Match.group(3) or ''
                opcode = 0xe040 | (regcode(destReg) & 0x07) << 8 | (modifier(modif) & 0x03) << 4 | (indirectcode(indirectReg) & 0x03) << 2
                output.write(struct.pack('<H', opcode))
                address += 1
            elif rwram2Match:
                indirectReg = rwram2Match.group(1)
                modif = rwram2Match.group(2) or ''
                srcReg = rwram2Match.group(4)
                opcode = 0xe000 | (regcode(srcReg) & 0x07) << 8 | (modifier(modif) & 0x03) << 4 | (indirectcode(indirectReg) & 0x03) << 2
                output.write(struct.pack('<H', opcode))
                address += 1
            # Load ROM (indirect)
            elif romMatch:
                destReg = romMatch.group(1)
                indirectReg = romMatch.group(2)
                modif = romMatch.group(3) or ''
                opcode = 0xe041 | (regcode(destReg) & 0x07) << 8 | (modifier(modif) & 0x03) << 4 | (indirectcode(indirectReg) & 0x03) << 2
                output.write(struct.pack('<H', opcode))
                address += 1
            # Shift index
            elif shiftIdxMatch:
                destR = shiftIdxMatch.group(1)
                operation = shiftIdxMatch.group(2)
                opReg = shiftIdxMatch.group(3)
                sf = shiftcode(operation)
                opcode = 0xe042 | (int(destR) & 0x01) << 5 | sf << 3 | regcode(opReg) << 8
                output.write(struct.pack('<H', opcode))
                address += 1
            # I/O (1)
            elif io11Match:
                destReg = io11Match.group(1)
                offset = io11Match.group(2)
                opcode = 0xe480 | (regLcode(destReg) & 0x03) << 8 | (int(offset, 16) & 0x7f)
                output.write(struct.pack('<H', opcode))
                address += 1
            elif io12Match:
                offset = io12Match.group(1)
                srcReg = io12Match.group(2)
                opcode = 0xe080 | (regLcode(srcReg) & 0x03) << 8 | (int(offset, 16) & 0x7f)
                output.write(struct.pack('<H', opcode))
                address += 1
            # AU(1)
            elif au11Match:
                destReg = au11Match.group(1)
                op1 = au11Match.group(2)
                op2 = au11Match.group(3)
                carry = au11Match.group(4)
                if carry is None:
                    au = 0x6
                else:
                    au = 0x7
                opcode = 0xe800 | (regcode(destReg) & 0x07) << 8 | (regcode(op1) & 0x07) << 5 | au << 2 | op2code(op2)
                output.write(struct.pack('<H', opcode))
                address += 1
            elif au12Match:
                destReg = au12Match.group(1)
                op1 = au12Match.group(2)
                op2 = au12Match.group(3)
                au = 0x5
                opcode = 0xe800 | (regcode(destReg) & 0x07) << 8 | (regcode(op1) & 0x07) << 5 | au << 2 | op2code(op2)
                output.write(struct.pack('<H', opcode))
                address += 1
            elif au13Match:
                destReg = au13Match.group(1)
                op1 = au13Match.group(2)
                op2 = au13Match.group(3)
                au = 0x3
                opcode = 0xe800 | (regcode(destReg) & 0x07) << 8 | (regcode(op1) & 0x07) << 5 | au << 2 | op2code(op2)
                output.write(struct.pack('<H', opcode))
                address += 1
            elif au14Match:
                destReg = au14Match.group(1)
                op1 = au14Match.group(2)
                operation = au14Match.group(3)
                op2 = au14Match.group(4)
                if operation == '+':
                    if op2 == '1':
                        au = 0x0
                        yop = 0x0   # Unused operand 2 is set to 0, as observed in actual firmware
                    else:
                        au = 0x2
                        yop = op2code(op2)
                elif operation == '-':
                    if op2 == '1':
                        au = 0x1
                        yop = 0x0   # Unused operand 2 is set to 0, as observed in actual firmware
                    else:
                        au = 0x4
                        yop = op2code(op2)
                opcode = 0xe800 | (regcode(destReg) & 0x07) << 8 | (regcode(op1) & 0x07) << 5 | au << 2 | yop
                output.write(struct.pack('<H', opcode))
                address += 1
            # TODO MAC
            # Reg Move
            elif regMoveMatch:
                destReg = regMoveMatch.group(1)
                srcReg = regMoveMatch.group(2)
                opcode = 0xf800 | (regcode(srcReg) & 0x07) << 5 | (regcode(destReg) & 0x07) << 2
                output.write(struct.pack('<H', opcode))
                address += 1
            # Push / Pop
            elif pushPopMatch:
                operation = pushPopMatch.group(1)
                opReg = pushPopMatch.group(2)
                u = pushpopcode(operation)
                opcode = 0xf802 | (regcode(opReg) & 0x07) << 5 | u
                output.write(struct.pack('<H', opcode))
                address += 1
            # Shift
            elif shiftMatch:
                destR = shiftMatch.group(1)
                operation = shiftMatch.group(2)
                bits = shiftMatch.group(3)
                opReg = shiftMatch.group(4)
                sf = shiftcode(operation)
                opcode = 0xfa00 | (int(destR) & 0x01) << 8 | regcode(opReg) << 5 | sf << 3 | (int(bits)-1 & 0x07)
                output.write(struct.pack('<H', opcode))
                address += 1
            # TODO I/O (2) + Push / Pop I/O
            # Callff
            elif callffMatch:
                dest = callffMatch.group(1)
                if dest.startswith('0x'):
                    destAddr = int(dest, 16)
                elif dest.startswith('.'):
                    destAddr = labels[dest]
                    # TODO handle missing label
                else:
                    raise Exception(f"Line {lineNumber} ({hex(address, 6)}): invalid destination ({dest}) for instruction callff")
                word1 = (0b_1111_1101 << 8) | ((destAddr & 0xff0000) >> 16)
                word2 = destAddr & 0xffff
                output.write(struct.pack('<H', word1))
                output.write(struct.pack('<H', word2))
                address += 2
            # Jmpff
            elif jmpffMatch:
                dest = jmpffMatch.group(1)
                if dest.startswith('0x'):
                    destAddr = int(dest, 16)
                elif dest.startswith('.'):
                    destAddr = labels[dest]
                    # TODO handle missing label
                else:
                    raise Exception(f"Line {lineNumber} ({hex(address, 6)}): invalid destination ({dest}) for instruction jmpff")
                word1 = (0b_1111_1110 << 8) | ((destAddr & 0xff0000) >> 16)
                word2 = destAddr & 0xffff
                output.write(struct.pack('<H', word1))
                output.write(struct.pack('<H', word2))
                address += 2
            # Ret
            elif retMatch:
                opcode = 0xff40
                output.write(struct.pack('<H', opcode))
                address += 1
            # Reti
            elif retiMatch:
                opcode = 0xff41
                output.write(struct.pack('<H', opcode))
                address += 1
            # Retff
            elif retffMatch:
                opcode = 0xff42
                output.write(struct.pack('<H', opcode))
                address += 1
            # NOP
            elif nopMatch:
                opcode = 0xffff
                output.write(struct.pack('<H', opcode))
                address += 1
            # TODO EMAC
            else:
                raise Exception(f"Line {lineNumber} ({hex(address, 6)}): unsupported instruction ({instruction})")
        line = f.readline()
        lineNumber += 1
