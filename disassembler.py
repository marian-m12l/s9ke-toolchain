#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os

#FW = '/home/marian/Bureau/Perso/SYS.BIN'

#FW = '/home/marian/Bureau/Perso/FW_2_6/FA.BIN'
#FW = '/home/marian/Bureau/Perso/FW_2_6/FU.BIN'
#FW = '/home/marian/Bureau/Perso/FW_2_6/SYS_from_rom.BIN'
FW = '/home/marian/Bureau/Perso/FW_2_6/rom_2_6.bin'

def hex(val, digits):
    return "{0:#0{1}x}".format(val, digits+2)

def signed8(value):
    return -(value & 0x80) | (value & 0x7f)
def signed12(value):
    return -(value & 0x800) | (value & 0x7ff)
def signed16(value):
    return -(value & 0x8000) | (value & 0x7fff)

suffixes = ['eq', 'ne', 'gt', 'ge', 'lt', 'le', 'av', 'nav', 'ac', 'nac', 'mr0s', 'mr0ns', 'mv', 'nmv', 'ixv', 'irr']    # FIXME irr unsupported ???
def condsuffix(cond):
    return suffixes[cond]

registers_reg = ['X0', 'X1', 'R0', 'R1', 'Y0', 'Y1', 'MR0', 'MR1']
registers_reg1 = ['X0', 'X1', 'R0', 'R1', 'Y0', 'Y1', 'Ix0', 'Ix1']
registers_regL = ['X0', 'X1', 'R0', 'R1']
def register(reg):
    return registers_reg[reg]
def register1(reg):
    return registers_reg1[reg]
def registerL(reg):
    return registers_regL[reg]

hilo_suffixes = ['.h', '', '.l', '']     # FIXME index 0x01 unsupported ?!!
def hilo(L):
    return hilo_suffixes[L]

modifiers = ['', ', m', ', 1', ', -1']
def modifier(A):
    return modifiers[A]

operandXop = ['X0', 'X1', 'R0', 'R1']
def operand1(Xop):
    return operandXop[Xop]

operandYop = ['Y0', 'Y1', 'R0', 'R1']
def operand2(Yop):
    return operandYop[Yop]

lu2Mnemonics = ['BCLR', 'BSET', 'BTOG', 'BTST']
def lu2(LU2):
    return lu2Mnemonics[LU2]

indirectIxy = ['Ix0', 'Ix1', 'Iy0', 'Iy1']
def indirect(Ixy):
    return indirectIxy[Ixy]

shiftMnemonics = ['', 'SL', 'SRA', 'SRL']   # FIXME Shift Left Sign Extension ???
def shift(sf):
    return shiftMnemonics[sf]

destXY = ['X0', 'X1', 'Y0', 'Y1']
def dxy(DXY):
    return destXY[DXY]

pushpopMnemonics = ['Push', 'Pop']
def pushpop(pp):
    return pushpopMnemonics[pp]

ioRegisters = dict([
    (0x0000, 'SSF'),
    (0x0001, 'SCR'),
    (0x0002, 'Ix0'),
    (0x0003, 'Ix1'),
    (0x0004, 'Im00'),
    (0x0005, 'Im01'),
    (0x0006, 'Im02'),
    (0x0007, 'Im03'),
    (0x0008, 'Im10'),
    (0x0009, 'Im11'),
    (0x000a, 'Im12'),
    (0x000b, 'Im13'),
    (0x000c, 'OPM_CONTROL'),
    (0x000d, 'RAMBk'),
    (0x000e, 'Ix0Bk'),
    (0x000f, 'Ix1Bk'),
    (0x0010, 'T0'),
    (0x0011, 'T1'),
    (0x0012, 'T2'),
    (0x0013, 'Iy0'),
    (0x0014, 'Iy1'),
    (0x0015, 'PCH'),
    (0x0016, 'PCL'),
    (0x0017, 'MMR'),
    (0x0018, 'Sp'),
    (0x0019, 'MR2'),
    (0x001a, 'Iy0Bk'),
    (0x001b, 'Iy1Bk'),
    (0x001c, 'Iy0BkRAM'),
    (0x001d, 'Iy1BkRAM'),
    (0x001e, 'Ix2'),
    (0x001f, 'Iy2'),
    (0x0020, 'INTEN'),
    (0x0021, 'INTRQ'),
    (0x0022, 'INTPR'),
    (0x0023, 'INTCR'),
    (0x0024, 'PCR1'),
    (0x0025, 'OPM_CTRL1'),
    (0x0026, 'ADC_FIFOSTATUS'),
    (0x0028, 'ADC_DATA'),
    (0x0029, 'WDT'),
    (0x002a, 'ADC_SET1'),
    (0x002b, 'ADC_SET2'),
    (0x002c, 'ImxL'),
    (0x002d, 'ImxC'),
    (0x002e, 'ImyL'),
    (0x002f, 'ImyC'),
    (0x0030, 'P0WKUPEN'),
    (0x0031, 'P1WKUPEN'),
    (0x0032, 'INTEN2'),
    (0x0033, 'INTRQ2'),
    (0x0034, 'INTPR2'),
    (0x0035, 'INTCR2'),
    (0x0036, 'IBx'),
    (0x0037, 'ILx'),
    (0x0038, 'IBy'),
    (0x0039, 'ILy'),
    (0x003a, 'IOSW'),
    (0x003b, 'SP1'),
    (0x003c, 'IOSW2'),
    (0x003d, 'EVENT'),
    (0x003e, 'ShIdx'),
    (0x003f, 'ShV2'),
    (0x0040, 'T1CNTV'),
    (0x0045, 'T0CNT'),
    (0x0046, 'T1CNT'),
    (0x0047, 'T0CNTV'),
    (0x0048, 'INTEC'),
    (0x0049, 'DAC_SET1'),
    (0x004a, 'DAC_SET2'),
    (0x004b, 'DAC_FIFOSTATUS'),
    (0x004c, 'T2CNT'),
    (0x004d, 'EVENT0CNT'),
    (0x004e, 'EVENT1CNT'),
    (0x004f, 'EVENT2CNT'),
    (0x0050, 'I2SCTRL'),
    (0x0051, 'PWM0'),
    (0x0052, 'PWM1'),
    (0x0053, 'PWM2'),
    (0x0054, 'PWM3'),
    (0x0055, 'DAOL'),
    (0x0056, 'DAOR'),
    (0x0057, 'SPIDADA0'),
    (0x0058, 'SPIDADA1'),
    (0x0059, 'SPIDADA2'),
    (0x005a, 'SPIDADA3'),
    (0x005b, 'SPIDADA4'),
    (0x005c, 'SPIDADA5'),
    (0x005d, 'SPICTRL'),
    (0x005e, 'SPICSC'),
    (0x005f, 'SPITRANSFER'),
    (0x0061, 'SPIBR'),
    (0x0062, 'MSPSTAT'),
    (0x0063, 'MSPM1'),
    (0x0064, 'MSPM2'),
    (0x0065, 'MSPBUF'),
    (0x0066, 'MSPADR'),
    (0x0067, 'CHIP_ID'),
    (0x0068, 'P0En'),
    (0x0069, 'P0'),
    (0x006a, 'P0M'),
    (0x006b, 'P0PH'),
    (0x006c, 'P1En'),
    (0x006d, 'P1'),
    (0x006e, 'P1M'),
    (0x006f, 'P1PH'),
    (0x0074, 'P3En'),
    (0x0075, 'P3'),
    (0x0076, 'P3M'),
    (0x0077, 'P3PH'),
    (0x0078, 'P4En'),
    (0x0079, 'P4'),
    (0x007a, 'P4M'),
    (0x007b, 'P4PH'),
    (0x007c, 'SYSCONF'),
    (0x007d, 'ADP'),
    (0x007e, 'ADM'),
    (0x007f, 'ADR')
])
def ioRegisterLabel(ioReg):
    return ioRegisters.get(ioReg, "NOT FOUND") #ioRegisters[ioReg]


def print_instruction(address, instr, comment='', wip=False):
    flag = ''
    if wip:
        flag = '(WIP)\t'
    eolComment = ''
    if wip or len(comment) > 0:
        eolComment = '\t\t\t; ' + flag + comment
    print('%s (%s):\t%s%s' % (hex(address,6), hex(int(address/2),6), instr, eolComment))


address = 0
with open(FW, 'rb') as f:
    word = f.read(2)
    # TODO Print EOL comments to explain each operation
    # TODO Use I/O labels when possible (at least in comments?)
    # TODO Check 3.2.3. Special Registers (IO SPACE) of DSP to determine bit numbering regarding high/low bytes ???
    while word:
        # FIXME Byte order ???
        high = word[1]
        low = word[0]
        #print('%s %s' % (hex(high,2), hex(low,2)))
        # Call
        if high & 0b_1000_0000 == 0:
            abs_addr = ((high & 0b_0111_1111) << 8) + low
            print_instruction(address, 'Call\t%s' % (hex(abs_addr, 4)), '')
        # Jump
        elif ((high >> 4) & 0b_0000_1111) == 0b_1000:
            offset = signed12( ((high & 0b_0000_1111) << 8) + low ) # Offset is signed !
            print_instruction(address, 'Jmp\t%s' % (hex(offset, 3)), 'Dest = %s' % (hex(int(address/2)+1+offset, 6)))
        # Jump Condition
        elif ((high >> 4) & 0b_0000_1111) == 0b_1001:
            cond = high & 0b_0000_1111
            offset = signed8(low)   # Offset is signed !
            mnemonic = 'J' + condsuffix(cond)
            print_instruction(address, '%s\t%s' % (mnemonic, hex(offset, 2)), 'Dest = %s' % (hex(int(address/2)+1+offset, 6)))
        # RW Mem (direct)
        elif ((high >> 5) & 0b_0000_0111) == 0b_101:
            r = (high & 0b_0001_0000) >> 4       # r=0: DM(imm) <= Reg      r=1: Reg <= DM(imm)
            hash = (high & 0b_0000_1000) >> 3    # Offset[8]
            reg = high & 0b_0000_0111
            offset = (hash << 8) | low
            if r:
                print_instruction(address, '%s = DM(%s)' % (register(reg), hex(offset, 2)), '', True)
            else:
                print_instruction(address, 'DM(%s) = %s' % (hex(offset, 2), register(reg)), '', True)
        # Load Immediate
        elif ((high >> 5) & 0b_0000_0111) == 0b_110 and ((high >> 3) & 0b_0000_0011) != 0b_01:
            L = (high & 0b_0001_1000) >> 3       # L=00: Load High, Keep Low     L=10: Keep High, Load Low       L=11: Clear High, Load Low
            reg1 = high & 0b_0000_0111
            imm = low
            print_instruction(address, '%s%s = %s' % (register1(reg1), hilo(L), hex(imm, 2)))
        # AU(2) To Mem
        elif ((high >> 3) & 0b_0001_1111) == 0b_11001 and ((low >> 7) & 0b_0000_0001) == 0b_0:
            A = (high & 0b_0000_0110) >> 1       # A=00: No Change  A=01: By Modifier   A=10: +1    A=11: -1
            Ix = (high & 0b_0000_0001)           # 0: Ix0   1: Ix1
            Xop = (low & 0b_0110_0000) >> 5
            AU = (low & 0b_0001_1100) >> 2
            Yop = (low & 0b_0000_0011)
            modif = modifier(A)                  # Modifier indicates how the data address (indirect register Ix/y) is incremented after the operation (not incremented, +1, -1, +modifier register lm)
            first_operand = operand1(Xop)
            second_operand = operand2(Yop)
            # FIXME What is C ??? --> Carry ???
            if AU == 0b_000:
                operation = '%s + 1' % (first_operand)
            elif AU == 0b_001:
                operation = '%s - 1' % (first_operand)
            elif AU == 0b_010:
                operation = '%s + %s' % (first_operand, second_operand)
            elif AU == 0b_011:
                operation = '%s + %s + C' % (first_operand, second_operand)
            elif AU == 0b_100:
                operation = '%s - %s' % (first_operand, second_operand)
            elif AU == 0b_101:
                operation = '%s - %s + C - 1' % (first_operand, second_operand)
            elif AU == 0b_110:
                operation = '-%s + %s' % (first_operand, second_operand)
            elif AU == 0b_111:
                operation = '-%s + %s + C - 1' % (first_operand, second_operand)
            print_instruction(address, 'RAM(Ix%s%s) = %s' % (Ix, modif, operation), '', True)
        # LU(1)
        elif ((high >> 3) & 0b_0001_1111) == 0b_11001 and ((low >> 7) & 0b_0000_0001) == 0b_1 and ((low >> 2) & 0b_0000_0001) == 0b_0:
            reg = high & 0b_0000_0111
            Xop = (low & 0b_0110_0000) >> 5
            LU1 = (low & 0b_0001_1000) >> 3
            Yop = (low & 0b_0000_0011)
            first_operand = operand1(Xop)
            second_operand = operand2(Yop)
            if LU1 == 0b_00:
                operation = '%s AND %s' % (first_operand, second_operand)
            elif LU1 == 0b_01:
                operation = '%s OR %s' % (first_operand, second_operand)
            elif LU1 == 0b_10:
                operation = '%s XOR %s' % (first_operand, second_operand)
            elif LU1 == 0b_11:
                operation = 'NOT %s' % (first_operand)
            print_instruction(address, '%s = %s' % (register(reg), operation))
        # LU(2)
        elif ((high >> 3) & 0b_0001_1111) == 0b_11001 and ((low >> 7) & 0b_0000_0001) == 0b_1 and ((low >> 2) & 0b_0000_0001) == 0b_1:
            _f = high & 0b_0000_0001              # 0: r0    1: r1
            Cst_x = ((high & 0b_0000_0110) << 1) | ((low & 0b_0110_0000) >> 5)
            LU2 = (low & 0b_0001_1000) >> 3
            Yop = (low & 0b_0000_0011)
            operand = operand2(Yop)
            mnemonic = lu2(LU2)
            print_instruction(address, 'R%s = %s.%d\t%s' % (_f, mnemonic, Cst_x, operand))
        # RW SRAM (indirect)
        elif ((high >> 3) & 0b_0001_1111) == 0b_11100 and ((low >> 7) & 0b_0000_0001) == 0b_0 and (low & 0b_0000_0011) == 0b_00:
            reg = high & 0b_0000_0111
            r = (low & 0b_0100_0000) >> 6        # r=0: RAM(offset) <= Reg      r=1: Reg <= RAM(offset)
            A = (low & 0b_0011_0000) >> 4        # A=00: No Change  A=01: By Modifier   A=10: +1    A=11: -1
            Ixy = (low & 0b_0000_1100) >> 2      # 00: Ix0   01: Ix1    10: Iy0     11: Iy1
            modif = modifier(A)                  # Modifier indicates how the data address (indirect register Ix/y) is incremented after the operation (not incremented, +1, -1, +modifier register lm)
            ind = indirect(Ixy)
            if r:
                print_instruction(address, '%s = RAM(%s%s)' % (register(reg), ind, modif))
            else:
                print_instruction(address, 'RAM(%s%s) = %s' % (ind, modif, register(reg)))
        # Load ROM (indirect)
        elif ((high >> 3) & 0b_0001_1111) == 0b_11100 and ((low >> 6) & 0b_0000_0011) == 0b_01 and (low & 0b_0000_0011) == 0b_01:
            reg = high & 0b_0000_0111
            A = (low & 0b_0011_0000) >> 4        # A=00: No Change  A=01: By Modifier   A=10: +1    A=11: -1
            Ixy = (low & 0b_0000_1100) >> 2      # 00: Ix0   01: Ix1    10: Iy0     11: Iy1
            modif = modifier(A)                  # Modifier indicates how the data address (indirect register Ix/y) is incremented after the operation (not incremented, +1, -1, +modifier register lm)
            ind = indirect(Ixy)
            print_instruction(address, '%s = ROM(%s%s)' % (register(reg), ind, modif))
        # Shift index
        elif ((high >> 3) & 0b_0001_1111) == 0b_11100 and ((low >> 6) & 0b_0000_0011) == 0b_01 and (low & 0b_0000_0111) == 0b_010:
            reg = high & 0b_0000_0111
            _f = (low & 0b_0010_0000) >> 5       # 0: r0    1: r1
            sf = (low & 0b_0001_1000) >> 3       # 00: Shift Left Sign Extension    01: A/L Shift Left  10: A Shift Right   11: L Shift Right
            mnemonic = shift(sf)
            # FIXME: Number of bits to shift is determined by the ShIdx I/O (0x003e)
            print_instruction(address, 'R%s = %s.Idx %s' % (_f, mnemonic, register(reg)), '', True)
        # I/O (1)
        elif ((high >> 3) & 0b_0001_1111) == 0b_11100 and ((low >> 7) & 0b_0000_0001) == 0b_1:
            r = (high & 0b_0000_0100) >> 2        # r=0: IO(offset) <= RegL      r=1: RegL <= IO(offset)
            regL = (high & 0b_0000_0011)
            offset = low & 0b_0111_1111
            if r:
                print_instruction(address, '%s = IO(%s)' % (registerL(regL), hex(offset, 2)), 'I/O register = %s' % (ioRegisterLabel(offset)))
            else:
                print_instruction(address, 'IO(%s) = %s' % (hex(offset, 2), registerL(regL)), 'I/O register = %s' % (ioRegisterLabel(offset)))
        # AU(1)
        elif ((high >> 3) & 0b_0001_1111) == 0b_11101:
            regDst = high & 0b_0000_0111
            regSrc = (low & 0b_1110_0000) >> 5
            AU = (low & 0b_0001_1100) >> 2
            Yop = (low & 0b_0000_0011)
            first_operand = register(regSrc)
            second_operand = operand2(Yop)
            if AU == 0b_000:
                operation = '%s + 1' % (first_operand)
            elif AU == 0b_001:
                operation = '%s - 1' % (first_operand)
            elif AU == 0b_010:
                operation = '%s + %s' % (first_operand, second_operand)
            elif AU == 0b_011:
                operation = '%s + %s + C' % (first_operand, second_operand)
            elif AU == 0b_100:
                operation = '%s - %s' % (first_operand, second_operand)
            elif AU == 0b_101:
                operation = '%s - %s + C - 1' % (first_operand, second_operand)
            elif AU == 0b_110:
                operation = '-%s + %s' % (first_operand, second_operand)
            elif AU == 0b_111:
                operation = '-%s + %s + C - 1' % (first_operand, second_operand)
            print_instruction(address, '%s = %s' % (register(regDst), operation), '', True)
        # MAC
        elif ((high >> 3) & 0b_0001_1111) == 0b_11110:
            MAC = high & 0b_0000_0111
            M = (low & 0b_1000_0000) >> 7        # 0: simple MAC    1: multiple-function
            Ix = (low & 0b_0100_0000) >> 6       # 0: Ix0   1: Ix1
            A = (low & 0b_0011_0000) >> 4        # A=00: No Change  A=01: By Modifier   A=10: +1    A=11: -1
            DXY = (low & 0b_0000_1100) >> 2      # 00: X0   01: X1  10: Y0  11: Y1
            X = (low & 0b_0000_0010) >> 1        # 0: X0    1: X1
            Y = low & 0b_0000_0001               # 0: Y0    1: Y1
            first_operand = operand1(X)
            second_operand = operand2(Y)
            if MAC == 0b_000:
                operation = '%s * %s (IS)' % (first_operand, second_operand)
            elif MAC == 0b_001:
                operation = 'MR + %s * %s (IS)' % (first_operand, second_operand)
            elif MAC == 0b_010:
                operation = 'MR - %s * %s (IS)' % (first_operand, second_operand)
            elif MAC == 0b_011:
                # FIXME Unsupported
                operation = 'TBD'
            elif MAC == 0b_100:
                operation = '%s * %s (FS)' % (first_operand, second_operand)
            elif MAC == 0b_101:
                operation = 'MR + %s * %s (FS)' % (first_operand, second_operand)
            elif MAC == 0b_110:
                operation = 'MR - %s * %s (FS)' % (first_operand, second_operand)
            elif MAC == 0b_111:
                # FIXME Unsupported
                operation = 'TBD'
            # Optional second (parallel) operation (load from RAM)
            if M == 0b_0:
                operation2 = ''
            elif M == 0b_1:
                modif = modifier(A)              # Modifier indicates how the data address (indirect register Ix/y) is incremented after the operation (not incremented, +1, -1, +modifier register lm)
                operation2 = ', %s = RAM(Ix%s%s)' % (dxy(DXY), Ix, modif)
            print_instruction(address, 'MR = %s%s' % (operation, operation2), '', True)
        # Reg Move
        elif high == 0b_1111_1000 and (low & 0b_0000_0011) == 0b_00:
            regSrc = (low & 0b_1110_0000) >> 5
            regDst = (low & 0b_0001_1100) >> 2
            print_instruction(address, '%s = %s' % (register(regDst), register(regSrc)))
        # Push / Pop
        elif high == 0b_1111_1000 and (low & 0b_0001_1110) >> 1 == 0b_0001:
            reg = (low & 0b_1110_0000) >> 5
            U = low & 0b_0000_0001               # 0: push  1: pop
            mnemonic = pushpop(U)
            print_instruction(address, '%s %s' % (mnemonic, register(reg)))
        # Shift
        elif ((high >> 1) & 0b_0111_1111) == 0b_111_1101:
            _f = high & 0b_0000_0001             # 0: r0    1: r1
            reg = (low & 0b_1110_0000) >> 5
            sf = (low & 0b_0001_1000) >> 3       # 00: Shift Left Sign Extension    01: A/L Shift Left  10: A Shift Right   11: L Shift Right
            sh = low & 0b_0000_0111              # Number of bits to shift (000: 1, 001: 2, ...)
            mnemonic = shift(sf)
            print_instruction(address, 'R%s = %s.%s %s' % (_f, mnemonic, (sh+1), register(reg)), '', True)
        # I/O (2) + Push / Pop I/O
        elif high == 0b_1111_1100 and (low & 0b_1000_0000) >> 7 == 0b_1:
            r = (low & 0b_0100_0000) >> 6        # 0: Push IO(offset)   1: Pop IO(offset)
            offset = low & 0b_0011_1111
            mnemonic = pushpop(r)
            print_instruction(address, '%s IO(%s)' % (mnemonic, hex(offset, 2)), 'I/O register = %s' % (ioRegisterLabel(offset)), True)
        # Reserved  FIXME Should throw en error ???
        elif high == 0b_1111_1100 and (low & 0b_1000_0000) >> 7 == 0b_0:
            print_instruction(address, 'Reserved', '', True)
        # Callff (2-words instruction)
        elif high == 0b_1111_1101:
            abs_addr_high = low
            second_word = f.read(2)
            #print('%s %s' % (hex(second_word[0],2), hex(second_word[1],2)))
            # FIXME Byte order ???
            abs_addr_low = (second_word[1] << 8) | second_word[0]
            abs_addr = (abs_addr_high << 16) | abs_addr_low
            print_instruction(address, 'Callff\t%s' % (hex(abs_addr, 6)), '', True)
            address += 2
        # Jumpff (2-words instruction)
        elif high == 0b_1111_1110:
            abs_addr_high = low
            second_word = f.read(2)
            #print('%s %s' % (hex(second_word[0],2), hex(second_word[1],2)))
            # FIXME Byte order ???
            abs_addr_low = (second_word[1] << 8) | second_word[0]
            abs_addr = (abs_addr_high << 16) | abs_addr_low
            print_instruction(address, 'Jmpff\t%s' % (hex(abs_addr, 6)), '', True)
            address += 2
        # Do0   FIXME No operation documentation??? Should fail ???
        elif high == 0b_1111_1100 and (low & 0b_1100_0000) >> 6 == 0b_00:
            cntV = low & 0b_0011_1111
            print_instruction(address, 'Do0\t%s' % (cntV), '', True)
        # Do1   FIXME No operation documentation??? Should fail ???
        elif high == 0b_1111_1100 and (low & 0b_1100_0000) >> 6 == 0b_01:
            cntV = low & 0b_0011_1111
            print_instruction(address, 'Do1\t%s' % (cntV), '', True)
        # Loop0 FIXME No operation documentation??? Should fail ???
        elif high == 0b_1111_1111 and low == 0b_1111_1100:
            print_instruction(address, 'Loop0', '', True)
        # Loop1 FIXME No operation documentation??? Should fail ???
        elif high == 0b_1111_1111 and low == 0b_1111_1110:
            print_instruction(address, 'Loop1', '', True)
        # Ret
        elif high == 0b_1111_1111 and low == 0b_0100_0000:
            print_instruction(address, 'Ret')
        # Reti
        elif high == 0b_1111_1111 and low == 0b_0100_0001:
            print_instruction(address, 'Reti')
        # Retff
        elif high == 0b_1111_1111 and low == 0b_0100_0010:
            print_instruction(address, 'Retff')
        # ICEC  FIXME Unused ???
        elif high == 0b_1111_1111 and low == 0b_1111_1101:
            print_instruction(address, 'ICE Call Function', '', True)
        # NOP
        elif high == 0b_1111_1111 and low == 0b_1111_1111:
            print_instruction(address, 'Nop')
        # DisSPSW   FIXME Undocumented ?! Should fail ??? (Clear SCR.SPSW)
        elif high == 0b_1111_1111 and low == 0b_0000_0001:
            print_instruction(address, 'DisSPSW', '', True)
        # EnSPSW    FIXME Undocumented ?! Should fail ??? (Enable SCR.SPSW write)
        elif high == 0b_1111_1111 and low == 0b_1111_1111:
            print_instruction(address, 'EnSPSW', ', True')
        # EMAC      FIXME CONFLICTS WITH MAC OPERATION (0b_11110...) ?!
        elif ((high >> 3) & 0b_1111_1000) == 0b_11110 and (low & 0b_01000000) >> 6 == 0b_1:
            MAC = high & 0b_0000_0111
            EM = (low & 0b_1000_0000) >> 7       # 0: simple MAC    1: multiple-function
            AmX = (low & 0b_0010_0000) >> 5      # 0: ImxL (Linear)     1: ImxC (Circular)
            AmY = (low & 0b_0001_0000) >> 4      # 0: ImyL (Linear)     1: ImyC (Circular)
            DmX = (low & 0b_0000_1000) >> 3      # 0: X0    1: X1
            DmY = (low & 0b_0000_0100) >> 2      # 0: Y0    1: Y1
            X = (low & 0b_0000_0010) >> 1        # 0: X0    1: X1
            Y = low & 0b_0000_0001               # 0: Y0    1: Y1
            # TODO Multiple Functions with Double-Fetched
            # When MMR register (0x0017) bit13 is set, MAC operation should enable Double Fetch Instruction
            # -> same binary instruction, different behaviour and parameter layout...
            print_instruction(address, 'EMAC')
            break
        # Unhandled opcode
        else:
            print('%s\tUNKNOWN' % hex(address,6))
            # TODO Should break and throw an error
        # Read next word
        word = f.read(2)
        address += 2

print('Done.')
