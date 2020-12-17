#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os
import signal
import sys
import re
from math import copysign

FW = '../FW_2_6/rom_2_6.bin'


# Internal registers
internal = {
    'X0': 0x0000,
    'X1': 0x0000,
    'Y0': 0x0000,
    'Y1': 0x0000,
    'R0': 0x0000,
    'R1': 0x0000,
    'MR0': 0x0000,
    'MR1': 0x0000
}
# I/O registers
ioReg = {
    'SSF': 0x0000,          # bit5: Index Register Overflow Flag   bit4: MAC Overflow Flag  bit3: Arithmetic Overflow Flag  bit2: Carry Flag    bit1: Negative Flag bit0: Zero Flag
    'SCR': 0x0002,
	'Ix0': 0x0000,
	'Ix1': 0x0000,
	'Im00': 0x0000,         # Ix0/Iy0 modifier: ''
	'Im01': 0x0000,         # Ix0/Iy0 modifier: ', m'   (value can be changed)
	'Im02': 0x0001,         # Ix0/Iy0 modifier: ', 1'
	'Im03': 0xffff,         # Ix0/Iy0 modifier: ', -1'
	'Im10': 0x0000,         # Ix1/Iy1 modifier: ''
	'Im11': 0x0000,         # Ix1/Iy1 modifier: ', m'   (value can be changed)
	'Im12': 0x0001,         # Ix1/Iy1 modifier: ', 1'
	'Im13': 0xffff,         # Ix1/Iy1 modifier: ', -1'
	'OPM_CTRL': 0x0003,
	'RAMBk': 0x00,
	'Ix0Bk': 0x00,
	'Ix1Bk': 0x00,
	'T0': 0x0700,
	'T1': 0x0700,
	'T2': 0x0700,
	'Iy0': 0x0000,
	'Iy1': 0x0000,
	'PCH': 0x00,
	'PCL': 0x0000,
	'MMR': 0x0000,
	'Sp': 0x0100,
	'MR2': 0x0000,
	'Iy0Bk': 0x00,
	'Iy1Bk': 0x00,
	'Iy0BkRAM': 0x00,
	'Iy1BkRAM': 0x00,
	'Ix2': 0x0000,
	'Iy2': 0x0000,
	'INTEN': 0x0000,
	'INTRQ': 0x0000,
	'INTPR': 0x0000,
	'INTCR': 0x0000,
	'PCR1': 0x0020,
	'OPM_CTRL1': 0x0000,
	'ADC_FIFOSTATUS': 0x0200,
	'ADC_DATA': 0x0000,
	'WDT': 0x8000,
	'ADC_SET1': 0x0000,
	'ADC_SET2': 0x0000,
	'ImxL': 0x0000,
	'ImxC': 0x0000,
	'ImyL': 0x0000,
	'ImyC': 0x0000,
	'P0WKUPEN': 0x0000,
	'P1WKUPEN': 0x0000,
	'INTEN2': 0x0000,
	'INTRQ2': 0x0000,
	'INTPR2': 0x0000,
	'INTCR2': 0x0000,
	'IBx': 0x0000,
	'ILx': 0x0000,
	'IBy': 0x0000,
	'ILy': 0x0000,
	'IOSW': 0x0000,
	'SP1': 0x0200,
	'IOSW2': 0x0000,
	'EVENT': 0x0000,
	'ShIdx': 0x0000,
	'ShV2': 0x0000,
	'T1CNTV': 0x0000,
	'T0CNT': 0x0000,
	'T1CNT': 0x0000,
	'T0CNTV': 0x0000,
	'INTEC': 0x0000,
	'DAC_SET1': 0x0000,
	'DAC_SET2': 0x0000,
	'DAC_FIFOSTATUS': 0x0200,
	'T2CNT': 0x0000,
	'EVENT0CNT': 0x0000,
	'EVENT1CNT': 0x0000,
	'EVENT2CNT': 0x0000,
	'I2SCTRL': 0x0000,
	'PWM0': 0x0000,
	'PWM1': 0x0000,
	'PWM2': 0x0000,
	'PWM3': 0x0000,
	'DAOL': 0x0000,
	'DAOR': 0x0000,
	'SPIDADA0': 0x0000,
	'SPIDADA1': 0x0000,
	'SPIDADA2': 0x0000,
	'SPIDADA3': 0x0000,
	'SPIDADA4': 0x0000,
	'SPIDADA5': 0x0000,
	'SPICTRL': 0x0000,
	'SPICSC': 0x0000,
	'SPITRANSFER': 0x0000,
	'SPIBR': 0x0000,
	'MSPSTAT': 0x0000,
	'MSPM1': 0x0000,
	'MSPM2': 0x0000,
	'MSPBUF': 0x0000,
	'MSPADR': 0x0000,
	'CHIP_ID': 0x0fff,
	'P0En': 0x0000,
	'P0': 0xffff,
	'P0M': 0x0000,
	'P0PH': 0xffff,
	'P1En': 0x0000,
	'P1': 0xffff,
	'P1M': 0x0000,
	'P1PH': 0xffff,
	'P3En': 0x0000,
	'P3': 0xf800,
	'P3M': 0x0000,
	'P3PH': 0xffff,
	'P4En': 0x0000,
	'P4': 0x0fff,
	'P4M': 0x0000,
	'P4PH': 0xffff,
	'SYSCONF': 0x0022,
	'ADP': 0x0000,
	'ADM': 0x0000,
	'ADR': 0x0000
}
# Program RAM
PRAM = [0x0000] * 0x8000
# Working RAM
WRAM = [0x0000] * 0x4000
# Part of the WRAM (up to 12K words) can be assigned to Program RAM (0x200000-0x202fff)
PRAM200000 = [0x0000] * 0x3000
# Entire ROM is loaded into External Program Memory (0x400000-0xbfffff)
CS1ROM = [0x0000] * 0x800000



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

class bcolors:
    ADDRESS = '\033[90m'
    EOLCOMMENT = '\033[96m'
    EXECUTION = '\033[33m'
    ERROR = '\033[1m\033[91m'
    CONTROL = '\033[36m'
    JUMP = '\033[1m\033[95m'
    REGVAL = '\033[1m\033[92m'
    ROM = '\033[1m\033[94m'
    RAM = '\033[1m\033[95m'
    ENDC = '\033[0m'

def print_instruction(address, instr, comment='', wip=False):
    flag = ''
    if wip:
        flag = '(WIP)\t'
    eolComment = ''
    if wip or len(comment) > 0:
        eolComment = '\t\t\t; ' + flag + comment
    print(f"{bcolors.ADDRESS}{hex(address,6)} ({hex(int(address/2),6)}):{bcolors.ENDC}\t{instr}{bcolors.EOLCOMMENT}{eolComment}{bcolors.ENDC}")

def print_execution(message):
    print(f"{bcolors.EXECUTION}\t\t\t\t\t\t\t\t\t\t{message}{bcolors.ENDC}")

def print_error(message):
    print(f"{bcolors.ERROR}\t\t\t\t\t\t\t\t\t\t{message}{bcolors.ENDC}")

def print_control(message):
    print(f"{bcolors.CONTROL}{message}{bcolors.ENDC}")


def incrementPC(count = 1):
    global ioReg
    summedL = ioReg['PCL'] + count
    ioReg['PCL'] = summedL & 0xffff
    carry = (summedL & 0xff0000) >> 16
    if carry > 0:
        summedH = ioReg['PCH'] + carry
        ioReg['PCH'] = summedH & 0xff
        if summedH > 0xff:
            # TODO Handle PC overflow ???
            raise
    print_execution(f"{bcolors.REGVAL}PC{bcolors.ENDC}{bcolors.EXECUTION} was incremented to {bcolors.REGVAL}{hex((ioReg['PCH'] << 16) | ioReg['PCL'], 6)}{bcolors.ENDC}{bcolors.EXECUTION}")

def setPC(newPC):
    global ioReg
    ioReg['PCL'] = (newPC) & 0xffff
    ioReg['PCH'] = ((newPC & 0xff0000) >> 16) & 0xff
    print_execution(f"{bcolors.REGVAL}PC{bcolors.ENDC}{bcolors.EXECUTION} was set to {bcolors.REGVAL}{hex((ioReg['PCH'] << 16) | ioReg['PCL'], 6)}{bcolors.ENDC}{bcolors.EXECUTION}")

def getOpCode(PC):
    global PRAM
    global CS1ROM
    if PC < 0x8000:
        return PRAM[PC]
    elif PC >= 0x200000 and PC < 0x203000:
        return PRAM200000[PC - 0x200000]
    elif PC >= 0x400000 and PC < 0xC00000:
        return CS1ROM[PC - 0x400000]
    else:
        # TODO ???
        print_error('Cannot get opcode at address %s' % hex(PC, 6))
        raise

def push(value):
    global ioReg
    global WRAM
    WRAM[ioReg['Sp']] = value
    print_execution(f"Pushed {bcolors.REGVAL}{hex(value, 4)}{bcolors.ENDC}{bcolors.EXECUTION} on stack")
    ioReg['Sp'] = ioReg['Sp'] + 1
    print_execution(f"{bcolors.REGVAL}Sp{bcolors.ENDC}{bcolors.EXECUTION} incremented to {bcolors.REGVAL}{hex(ioReg['Sp'], 4)}{bcolors.ENDC}{bcolors.EXECUTION}")

def pop():
    global ioReg
    global WRAM
    popped = WRAM[ioReg['Sp']-1]
    print_execution(f"Popped {bcolors.REGVAL}{hex(popped, 4)}{bcolors.ENDC}{bcolors.EXECUTION} from stack")
    ioReg['Sp'] = ioReg['Sp'] - 1
    print_execution(f"{bcolors.REGVAL}Sp{bcolors.ENDC}{bcolors.EXECUTION} decremented to {bcolors.REGVAL}{hex(ioReg['Sp'], 4)}{bcolors.ENDC}{bcolors.EXECUTION}")
    return popped

flags = dict([
    ('IOF', 0b_10_0000),
    ('MOF', 0b_01_0000),
    ('AOF', 0b_00_1000),
    ('CF', 0b_00_0100),
    ('NF', 0b_00_0010),
    ('ZF', 0b_00_0001)
])
def setFlag(flagName):
    global ioReg
    ioReg['SSF'] = ioReg['SSF'] | flags[flagName]
    print_execution(f"Flag {bcolors.REGVAL}{flagName}{bcolors.ENDC}{bcolors.EXECUTION} was set")
def clearFlag(flagName):
    global ioReg
    ioReg['SSF'] = ioReg['SSF'] & ~flags[flagName]
    print_execution(f"Flag {bcolors.REGVAL}{flagName}{bcolors.ENDC}{bcolors.EXECUTION} was cleared")
def getFlag(flagName):
    if (ioReg['SSF'] & flags[flagName]) != 0:
        return 1
    else:
        return 0

sign = lambda x : copysign(1, x)

def incrementIndexRegister(indirectRegName, modif):
    modifierReg = 'Im' + indirectRegName[-1] + str(modif)
    print_execution('Updating indirect register %s with modifier register %s' % (indirectRegName, modifierReg))
    summedIx = ioReg[indirectRegName] + ioReg[modifierReg]
    ioReg[indirectRegName] = summedIx & 0xffff
    carry = (summedIx & 0xff0000) >> 8
    if carry > 0:
        setFlag('IOF')
        summedBk = ioReg[bkReg] + carry
        ioReg[bkReg] = summedBk & 0xff
        print_execution('Indirect register OVERFLOW: incremented bank register %s by %s to %s' % (bkReg, hex(carry, 2), hex(ioReg[BkReg], 2)))
        if summedBk > 0xff:
            # TODO Handle Bk overflow ???
            raise
    else:
        clearFlag('IOF')
    print_execution(f"Indirect register {bcolors.REGVAL}{indirectRegName}{bcolors.ENDC}{bcolors.EXECUTION} incremented by {hex(ioReg[modifierReg], 4)} to {bcolors.REGVAL}{hex(ioReg[indirectRegName], 4)}{bcolors.ENDC}{bcolors.EXECUTION}")

def setRegisterImmediate(reg1Name, hiloSuffix, value):
    global internal
    global ioReg
    if reg1Name == 'Ix0' or reg1Name == 'Ix1':
        if hiloSuffix == '.h':
            ioReg[reg1Name] = (value & 0xff) << 8 | (ioReg[reg1Name] & 0xff)
        elif hiloSuffix == '.l':
            ioReg[reg1Name] = (ioReg[reg1Name] & 0xff00) | (value & 0xff)
        else:
            ioReg[reg1Name] = value & 0xff
        print_execution(f"Register {bcolors.REGVAL}{reg1Name}{bcolors.ENDC}{bcolors.EXECUTION} set to {bcolors.REGVAL}{hex(ioReg[reg1Name], 4)}{bcolors.ENDC}{bcolors.EXECUTION}")
    else:
        if hiloSuffix == '.h':
            internal[reg1Name] = (value & 0xff) << 8 | (internal[reg1Name] & 0xff)
        elif hiloSuffix == '.l':
            internal[reg1Name] = (internal[reg1Name] & 0xff00) | (value & 0xff)
        else:
            internal[reg1Name] = value & 0xff
        print_execution(f"Register {bcolors.REGVAL}{reg1Name}{bcolors.ENDC}{bcolors.EXECUTION} set to {bcolors.REGVAL}{hex(internal[reg1Name], 4)}{bcolors.ENDC}{bcolors.EXECUTION}")

def setRegisterFromROM(regName, indirectRegName, modif):
    global internal
    global ioReg
    global PRAM
    bkReg = indirectRegName + 'Bk'
    offset = ioReg[bkReg] + ioReg[indirectRegName]
    if offset < 0x8000:
        internal[regName] = PRAM[offset]
    elif offset >= 0x200000 and offset < 0x203000:
        internal[regName] = PRAM200000[offset - 0x200000]
    elif offset >= 0x400000 and offset < 0xC00000:
        internal[regName] =  CS1ROM[offset - 0x400000]
    else:
        # TODO ???
        print_error('Cannot read ROM at address %s' % hex(offset, 6))
        raise
    print_execution(f"Register {bcolors.REGVAL}{regName}{bcolors.ENDC}{bcolors.EXECUTION} set by {bcolors.ROM}ROM({hex(offset, 6)}){bcolors.ENDC}{bcolors.EXECUTION} to {bcolors.REGVAL}{hex(internal[regName], 4)}{bcolors.ENDC}{bcolors.EXECUTION}")
    incrementIndexRegister(indirectRegName, modif)

def setRegFromIO(regLName, ioRegName):
    global internal
    global ioReg
    internal[regLName] = ioReg[ioRegName]
    print_execution(f"Register {bcolors.REGVAL}{regLName}{bcolors.ENDC}{bcolors.EXECUTION} set to {bcolors.REGVAL}{hex(internal[regLName], 4)}{bcolors.ENDC}{bcolors.EXECUTION}")

def setIOFromReg(ioRegName, regLName):
    global internal
    global ioReg
    ioReg[ioRegName] = internal[regLName]
    print_execution(f"I/O register {bcolors.REGVAL}{ioRegName}{bcolors.ENDC}{bcolors.EXECUTION} set to {bcolors.REGVAL}{hex(ioReg[ioRegName], 4)}{bcolors.ENDC}{bcolors.EXECUTION}")
    
def computeAUWithRegisters(regName, AU, first_operand, second_operand):
    global internal
    carry = getFlag('CF')
    if AU == 0b_000:
        result = internal[first_operand] + 1
        if sign(internal[first_operand]) == 1 and sign(result) == -1:
            setFlag('AOF')
        else:
            clearFlag('AOF')
    elif AU == 0b_001:
        result = internal[first_operand] - 1
        if sign(internal[first_operand]) == -1 and sign(result) == 1:
            setFlag('AOF')
        else:
            clearFlag('AOF')
    elif AU == 0b_010:
        result = internal[first_operand] + internal[second_operand]
        if sign(internal[first_operand])==sign(internal[second_operand]) and sign(result)!=sign(internal[first_operand]):
            setFlag('AOF')
        else:
            clearFlag('AOF')
    elif AU == 0b_011:
        # FIXME WHAT IS C ??? --> Carry ???
        result = internal[first_operand] + internal[second_operand] + carry
        #operation = '%s + %s + C' % (first_operand, second_operand)
        if sign(internal[first_operand])==sign(internal[second_operand]) and sign(result)!=sign(internal[first_operand]):
            setFlag('AOF')
        else:
            clearFlag('AOF')
    elif AU == 0b_100:
        result = internal[first_operand] - internal[second_operand]
        if sign(internal[first_operand])!=sign(internal[second_operand]) and sign(result)!=sign(internal[first_operand]):
            setFlag('AOF')
        else:
            clearFlag('AOF')
    elif AU == 0b_101:
        # FIXME WHAT IS C ??? --> Carry ???
        result = internal[first_operand] - internal[second_operand] + carry - 1
        #operation = '%s - %s + C - 1' % (first_operand, second_operand)
        if sign(internal[first_operand])!=sign(internal[second_operand]) and sign(result)!=sign(internal[first_operand]):
            setFlag('AOF')
        else:
            clearFlag('AOF')
    elif AU == 0b_110:
        result = -internal[first_operand] + internal[second_operand]
        if sign(internal[first_operand])!=sign(internal[second_operand]) and sign(result)!=sign(internal[second_operand]):
            setFlag('AOF')
        else:
            clearFlag('AOF')
    elif AU == 0b_111:
        # FIXME WHAT IS C ??? --> Carry ???
        result = -internal[first_operand] + internal[second_operand] + carry - 1
        #operation = '-%s + %s + C - 1' % (first_operand, second_operand)
        if sign(internal[first_operand])!=sign(internal[second_operand]) and sign(result)!=sign(internal[second_operand]):
            setFlag('AOF')
        else:
            clearFlag('AOF')
    internal[regName] = result & 0xffff
    print_execution(f"Register {bcolors.REGVAL}{regName}{bcolors.ENDC}{bcolors.EXECUTION} set to {bcolors.REGVAL}{hex(internal[regName], 4)}{bcolors.ENDC}{bcolors.EXECUTION}")
    # Update Flags
    if internal[regName] == 0x0000:
        setFlag('ZF')
    else:
        clearFlag('ZF')
    if (internal[regName] & 0x8000) >> 15 == 0b_1: # FIXME signed ???
        setFlag('NF')
    else:
        clearFlag('NF')
    # FIXME For substraction, CF=0 if borrowing !!!
    if (result >> 16) > 0: # FIXME carry ???
        setFlag('CF')
    else:
        clearFlag('CF')

def computeAUWithRegistersToRAM(indirectRegName, modif, AU, first_operand, second_operand):
    global internal
    global WRAM
    global PRAM200000
    bkReg = indirectRegName + 'Bk'
    offset = ioReg[bkReg] + ioReg[indirectRegName]
    carry = getFlag('CF')
    if AU == 0b_000:
        result = internal[first_operand] + 1
        if sign(internal[first_operand]) == 1 and sign(result) == -1:
            setFlag('AOF')
        else:
            clearFlag('AOF')
    elif AU == 0b_001:
        result = internal[first_operand] - 1
        if sign(internal[first_operand]) == -1 and sign(result) == 1:
            setFlag('AOF')
        else:
            clearFlag('AOF')
    elif AU == 0b_010:
        result = internal[first_operand] + internal[second_operand]
        if sign(internal[first_operand])==sign(internal[second_operand]) and sign(result)!=sign(internal[first_operand]):
            setFlag('AOF')
        else:
            clearFlag('AOF')
    elif AU == 0b_011:
        # FIXME WHAT IS C ??? --> Carry ???
        result = internal[first_operand] + internal[second_operand] + carry
        #operation = '%s + %s + C' % (first_operand, second_operand)
        if sign(internal[first_operand])==sign(internal[second_operand]) and sign(result)!=sign(internal[first_operand]):
            setFlag('AOF')
        else:
            clearFlag('AOF')
    elif AU == 0b_100:
        result = internal[first_operand] - internal[second_operand]
        if sign(internal[first_operand])!=sign(internal[second_operand]) and sign(result)!=sign(internal[first_operand]):
            setFlag('AOF')
        else:
            clearFlag('AOF')
    elif AU == 0b_101:
        # FIXME WHAT IS C ??? --> Carry ???
        result = internal[first_operand] - internal[second_operand] + carry - 1
        #operation = '%s - %s + C - 1' % (first_operand, second_operand)
        if sign(internal[first_operand])!=sign(internal[second_operand]) and sign(result)!=sign(internal[first_operand]):
            setFlag('AOF')
        else:
            clearFlag('AOF')
    elif AU == 0b_110:
        result = -internal[first_operand] + internal[second_operand]
        if sign(internal[first_operand])!=sign(internal[second_operand]) and sign(result)!=sign(internal[second_operand]):
            setFlag('AOF')
        else:
            clearFlag('AOF')
    elif AU == 0b_111:
        # FIXME WHAT IS C ??? --> Carry ???
        result = -internal[first_operand] + internal[second_operand] + carry - 1
        #operation = '-%s + %s + C - 1' % (first_operand, second_operand)
        if sign(internal[first_operand])!=sign(internal[second_operand]) and sign(result)!=sign(internal[second_operand]):
            setFlag('AOF')
        else:
            clearFlag('AOF')
    truncated = result & 0xffff
    # Program RAM within WRAM
    if offset >= 0x200000 and offset < 0x203000:
        PRAM200000[offset - 0x200000] = truncated
    # FIXME Handle MMIO when offset > 0x3fff
    elif offset > 0x3fff:
        # TODO
        print_error('NOT YET IMPLEMENTED (writing to MMIO: %s)' % hex(offset, 6))
    else:
        WRAM[offset] = truncated
    print_execution(f"{bcolors.RAM}RAM({hex(offset, 6)}){bcolors.ENDC}{bcolors.EXECUTION} set to {bcolors.REGVAL}{hex(truncated, 4)}{bcolors.ENDC}{bcolors.EXECUTION}")
    # Update Flags
    if truncated == 0x0000:
        setFlag('ZF')
    else:
        clearFlag('ZF')
    if (truncated & 0x8000) >> 15 == 0b_1: # FIXME signed ???
        setFlag('NF')
    else:
        clearFlag('NF')
    # FIXME For substraction, CF=0 if borrowing !!!
    if (result >> 16) > 0: # FIXME carry ???
        setFlag('CF')
    else:
        clearFlag('CF')
    incrementIndexRegister(indirectRegName, modif)

def setRegisterFromRAM(regName, indirectRegName, modif):
    global internal
    global ioReg
    global WRAM
    global PRAM200000
    bkReg = indirectRegName + 'Bk'
    offset = ioReg[bkReg] + ioReg[indirectRegName]
    # Program RAM within WRAM
    if offset >= 0x200000 and offset < 0x203000:
        internal[regName] = PRAM200000[offset - 0x200000]
    # FIXME Handle MMIO when offset > 0x3fff
    elif offset > 0x3fff:
        # TODO
        print_error('NOT YET IMPLEMENTED (reading from MMIO: %s)' % hex(offset, 6))
    else:
        internal[regName] = WRAM[offset]
    print_execution(f"Register {bcolors.REGVAL}{regName}{bcolors.ENDC}{bcolors.EXECUTION} set by {bcolors.RAM}RAM({hex(offset, 6)}){bcolors.ENDC}{bcolors.EXECUTION} to {bcolors.REGVAL}{hex(internal[regName], 4)}{bcolors.ENDC}{bcolors.EXECUTION}")
    incrementIndexRegister(indirectRegName, modif)

def setRAMFromRegister(indirectRegName, modif, regName):
    global internal
    global ioReg
    global WRAM
    global PRAM200000
    bkReg = indirectRegName + 'Bk'
    offset = ioReg[bkReg] + ioReg[indirectRegName]
    # Program RAM within WRAM
    if offset >= 0x200000 and offset < 0x203000:
        PRAM200000[offset - 0x200000] = internal[regName]
    # FIXME Handle MMIO when offset > 0x3fff
    elif offset > 0x3fff:
        # TODO
        print_error('NOT YET IMPLEMENTED (writing to MMIO: %s)' % hex(offset, 6))
    else:
        WRAM[offset] = internal[regName]
    print_execution(f"{bcolors.RAM}RAM({hex(offset, 6)}){bcolors.ENDC}{bcolors.EXECUTION} set to {bcolors.REGVAL}{hex(internal[regName], 4)}{bcolors.ENDC}{bcolors.EXECUTION}")
    incrementIndexRegister(indirectRegName, modif)

def setRegisterFromRAMDirect(regName, offset):
    global internal
    global ioReg
    global WRAM
    addr = (ioReg['RAMBk'] & 0x00fe) >> 1 | offset
    internal[regName] = WRAM[addr]
    print_execution(f"Register {bcolors.REGVAL}{regName}{bcolors.ENDC}{bcolors.EXECUTION} set by {bcolors.RAM}RAM({hex(addr, 6)}){bcolors.ENDC}{bcolors.EXECUTION} to {bcolors.REGVAL}{hex(internal[regName], 4)}{bcolors.ENDC}{bcolors.EXECUTION}")

def setRAMFromRegisterDirect(offset, regName):
    global internal
    global ioReg
    global WRAM
    addr = (ioReg['RAMBk'] & 0x00fe) >> 1 | offset
    WRAM[addr] = internal[regName]
    print_execution(f"{bcolors.RAM}RAM({hex(addr, 6)}){bcolors.ENDC}{bcolors.EXECUTION} set to {bcolors.REGVAL}{hex(WRAM[addr], 4)}{bcolors.ENDC}{bcolors.EXECUTION}")

def pushPopRegister(U, regName):
    global internal
    if U == 0:
        push(internal[regName])
    else:
        internal[regName] = pop()

def pushPopIO(r, ioRegName):
    global ioReg
    if r == 0:
        push(ioReg[ioRegName])
    else:
        ioReg[ioRegName] = pop()

def regMove(regDstName, regSrcName):
    global internal
    internal[regDstName] = internal[regSrcName]
    print_execution(f"Register {bcolors.REGVAL}{regDstName}{bcolors.ENDC}{bcolors.EXECUTION} set to {bcolors.REGVAL}{hex(internal[regDstName], 4)}{bcolors.ENDC}{bcolors.EXECUTION}")

def computeLU1(regName, LU1, first_operand, second_operand):
    global internal
    if LU1 == 0b_00:
        internal[regName] = internal[first_operand] & internal[second_operand]
    elif LU1 == 0b_01:
        internal[regName] = internal[first_operand] | internal[second_operand]
    elif LU1 == 0b_10:
        internal[regName] = internal[first_operand] ^ internal[second_operand]
    elif LU1 == 0b_11:
        internal[regName] = ~internal[first_operand]
    print_execution(f"Register {bcolors.REGVAL}{regName}{bcolors.ENDC}{bcolors.EXECUTION} set to {bcolors.REGVAL}{hex(internal[regName], 4)}{bcolors.ENDC}{bcolors.EXECUTION}")
    # Update Flags
    if internal[regName] == 0x0000:
        setFlag('ZF')
    else:
        clearFlag('ZF')
    if (internal[regName] & 0x8000) >> 15 == 0b_1: # FIXME signed ???
        setFlag('NF')
    else:
        clearFlag('NF')
    # FIXME Carry can only be cleared ???
    clearFlag('CF')
    # FIXME Arithmetic Overflow can only be cleared ???
    clearFlag('AOF')

def computeLU2(regName, LU2, Cst_x, operand):
    global internal
    if LU2 == 0b_00:
        # Clear bit
        internal[regName] = internal[operand] & ~(1 << Cst_x)
    elif LU2 == 0b_01:
        # Set bit
        internal[regName] = internal[operand] | (1 << Cst_x)
    elif LU2 == 0b_10:
        # Toggle bit
        internal[regName] = internal[operand] ^ (1 << Cst_x)
    elif LU2 == 0b_11:
        # Test bit
        internal[regName] = internal[operand] & (1 << Cst_x)
    print_execution(f"Register {bcolors.REGVAL}{regName}{bcolors.ENDC}{bcolors.EXECUTION} set to {bcolors.REGVAL}{hex(internal[regName], 4)}{bcolors.ENDC}{bcolors.EXECUTION}")
    # Update Flags
    if internal[regName] == 0x0000:
        setFlag('ZF')
    else:
        clearFlag('ZF')
    if (internal[regName] & 0x8000) >> 15 == 0b_1: # FIXME signed ???
        setFlag('NF')
    else:
        clearFlag('NF')
    # FIXME Carry can only be cleared ???
    clearFlag('CF')
    # FIXME Arithmetic Overflow can only be cleared ???
    clearFlag('AOF')

def computeShift(regDstName, sf, count, regSrcName):
    global internal
    if sf == 0b_00:
        # FIXME Left Shift Sign Extension ???
        result = internal[regSrcName] << count
        if (result & 0x10000) >> 16 == 0b_1:
            setFlag('CF')
        else:
            clearFlag('CF')
    elif LU2 == 0b_01:
        # Left Shift
        result = internal[regSrcName] << count
        if (result & 0x10000) >> 16 == 0b_1:
            setFlag('CF')
        else:
            clearFlag('CF')
    elif LU2 == 0b_10:
        # Arithmetic Right Shift
        result = internal[regSrcName] >> count
        if (internal[regSrcName] & (1 << (count-1))) >> (count-1) == 0b_1:
            setFlag('CF')
        else:
            clearFlag('CF')
    elif LU2 == 0b_11:
        # Logic Right Shift FIXME Should prepend zeroes !!!
        result = (internal[regSrcName] & 0xffff) >> count
        if (internal[regSrcName] & (1 << (count-1))) >> (count-1) == 0b_1:
            setFlag('CF')
        else:
            clearFlag('CF')
    internal[regDstName] = result & 0xffff
    print_execution(f"Register {bcolors.REGVAL}{regDstName}{bcolors.ENDC}{bcolors.EXECUTION} set to {bcolors.REGVAL}{hex(internal[regDstName], 4)}{bcolors.ENDC}{bcolors.EXECUTION}")
    # Update Flags
    if internal[regDstName] == 0x0000:
        setFlag('ZF')
    else:
        clearFlag('ZF')
    if (internal[regDstName] & 0x8000) >> 15 == 0b_1: # FIXME signed ???
        setFlag('NF')
    else:
        clearFlag('NF')
    # FIXME Arithmetic Overflow can only be cleared ???
    clearFlag('AOF')

def computeShiftWithIndex(regDstName, sf, regSrcName):
    count = ioReg['ShIdx'] & 0x000f
    computeShift(regDstName, sf, count, regSrcName)

def conditionMatched(cond):
    if cond == 0b_0000:     # Jeq: Jump if zero
        return getFlag('ZF') == 1
    elif cond == 0b_0001:   # Jne: Jump if _not_ zero
        return getFlag('ZF') == 0
    elif cond == 0b_0010:   # Jgt: Jump if greater than zero
        return (~(getFlag('NF')^getFlag('AOF')) & ~getFlag('ZF')) == 1
    elif cond == 0b_0011:   # Jge: Jump if greater than or equal to zero
        return (~(getFlag('NF')^getFlag('AOF')) | getFlag('ZF')) == 1
    elif cond == 0b_0100:   # Jlt: Jump if less than zero
        return ((getFlag('NF')^getFlag('AOF')) & ~getFlag('ZF')) == 1
    elif cond == 0b_0101:   # Jle: Jump if less than or equal to zero
        return ((getFlag('NF')^getFlag('AOF')) | getFlag('ZF')) == 1
    elif cond == 0b_0110:   # Jav: Jump if Arithmetic Overflow
        return getFlag('AOF') == 1
    elif cond == 0b_0111:   # Jnav: Jump if Arithmetic Overflow
        return getFlag('AOF') == 0
    elif cond == 0b_1000:   # Jac: Jump if Carry
        return getFlag('CF') == 1
    elif cond == 0b_1001:   # Jnac: Jump if _not_ Carry
        return getFlag('CF') == 0
    elif cond == 0b_1010:   # Jmr0s: Jump if MR0 negative
        return (internal['MR0'] & 0x8000) >> 15 == 1
    elif cond == 0b_1011:   # Jmr0ns: Jump if MR0 _not_ negative
        return (internal['MR0'] & 0x8000) >> 15 == 0
    elif cond == 0b_1100:   # Jmv: Jump if MAC Overflow
        return getFlag('MOF') == 1
    elif cond == 0b_1101:   # Jnmv: Jump if _not_ MAC Overflow
        return getFlag('MOF') == 0
    elif cond == 0b_1110:   # Jixv: Jump if Index Overflow
        return getFlag('IOF') == 1
    elif cond == 0b_1111:   # Jirr: Jump if Special EIR Case
        raise
        # FIXME return IntRR[7]


# TODO MMIO









# Open file
address = 0
with open(FW, 'rb') as f:
    # Load complete rom into CS1ROM
    word = f.read(2)
    while word and address < 0x800000:
        high = word[1]
        low = word[0]
        #print('Loading value %s into CS1ROM[%s]' % (hex((high << 8) | low, 4), hex(address, 4)))
        CS1ROM[address] = (high << 8) | low
        word = f.read(2)
        address += 1
    print_execution('Loaded %d words into CS1ROM.' % address)
# Load first 32KW into Program RAM
address = 0
for word in CS1ROM:
    if address == 0x8000:
        break
    #print('Loading value %s into PRAM[%s]' % (hex(word, 4), hex(address, 4)))
    PRAM[address] = word
    address += 1
print_execution('Loaded %d words into PRAM.' % address)

# Start executing at 0x000000 (Default PC value)
# FIXME Starting point as argument ? (another interrupt, fa 0x40000, fu 0x3000, ...)

# Execution control
breakpoints = [0x000000, 0x0004e5, 0x000100, 0x001ec5]
quit = False
stepByStep = False
ioRegex = re.compile('^io (.+)$')
wramRegex = re.compile('^wram (.+)$')
pramRegex = re.compile('^pram (.+)$')
romRegex = re.compile('^rom (.+)$')
# Stop on Ctrl+C
def sigint_handler(sig, frame):
    global stepByStep
    if stepByStep:
        sys.exit(1)
    else:
        stepByStep = True
signal.signal(signal.SIGINT, sigint_handler)

# Execution
while not quit:
    PC = (ioReg['PCH'] << 16) | ioReg['PCL']
    opcode = getOpCode(PC)
    high = (opcode & 0xff00) >> 8
    low = opcode & 0xff
    #print("opcode@%s: %s" % (hex(PC, 6), hex(opcode, 4)))
    #print('%s %s' % (hex(high,2), hex(low,2)))
    # TODO Handle breakpoints (address, condition, ...) + dump registers / stack / ram ?
    if PC in breakpoints or stepByStep:
        while True:
            command = input(f"{bcolors.CONTROL}> {bcolors.ENDC}")
            try:
                ioMatch = ioRegex.match(command)
                wramMatch = wramRegex.match(command)
                pramMatch = pramRegex.match(command)
                romMatch = romRegex.match(command)
                if 'q' == command:  # Stop emulator
                    print_control('Stopping emulator.')
                    quit = True
                    break
                elif 'c' == command:    # Continue execution
                    stepByStep = False
                    break
                elif 's' == command or '' == command:   # Step-by-step, next instruction
                    stepByStep = True
                    break
                elif 'reg' == command:
                    print_control("Internal registers:\t%s" % ("\t".join("{}={}".format(k, hex(v, 4)) for k, v in internal.items())))
                elif ioMatch:
                    if ioMatch.group(1).startswith('0x'):
                        ioAddr = int(ioMatch.group(1), 16)
                        print_control("I/O register: %s(%s)=%s" % (hex(ioAddr, 2), ioRegisterLabel(ioAddr), hex(ioReg[ioRegisterLabel(ioAddr)], 4)))
                    else:
                        print_control("I/O register: %s=%s" % (ioMatch.group(1), hex(ioReg[ioMatch.group(1)], 4)))
                elif wramMatch:
                    wramAddr = int(wramMatch.group(1), 16)
                    print_control("WRAM word: %s=%s" % (hex(wramAddr, 6), hex(WRAM[wramAddr], 4)))
                elif pramMatch:
                    pramAddr = int(pramMatch.group(1), 16)
                    if pramAddr < 0x8000:
                        pramWord = PRAM[pramAddr]
                    elif pramAddr >= 0x200000 and pramAddr < 0x203000:
                        pramWord = PRAM200000[pramAddr - 0x200000]
                    elif pramAddr >= 0x400000 and pramAddr < 0xC00000:
                        pramWord =  CS1ROM[pramAddr - 0x400000]
                    else:
                        # TODO ???
                        print_error('Cannot read ROM at address %s' % hex(pramAddr, 6))
                        raise
                    print_control("PRAM word: %s=%s" % (hex(pramAddr, 6), hex(pramWord, 4)))
                elif romMatch:
                    romAddr = int(romMatch.group(1), 16)
                    print_control("ROM word: %s=%s" % (hex(romAddr, 6), hex(CS1ROM[romAddr], 4)))
                else:
                    print_control(f'{bcolors.ERROR}Invalid command.{bcolors.ENDC}')
                    print_control("""Usage:
\tc:                    Continue execution
\ts or <enter>:         Step-by-step / Next instruction
\treg:                  Print internal registers
\tio <addr>|<label>:    Print I/O register
\twram <addr>:          Print WRAM word
\tpram <addr>:          Print PRAM word
\trom <addr>:           Print ROM word
\tq:                    Quit""")
            except:
                print_control(f'{bcolors.ERROR}Oops! Something bad occurred. Try again!{bcolors.ENDC}')
        if quit:
            continue

    # Call
    if high & 0b_1000_0000 == 0:
        abs_addr = ((high & 0b_0111_1111) << 8) + low
        print_instruction(PC*2, 'Call\t%s' % (hex(abs_addr, 4)), '')
        push(PC+1)
        setPC(abs_addr)
    # Jump
    elif ((high >> 4) & 0b_0000_1111) == 0b_1000:
        offset = signed12( ((high & 0b_0000_1111) << 8) + low ) # Offset is signed !
        print_instruction(PC*2, 'Jmp\t%s' % (hex(offset, 3)), 'Dest = %s' % (hex(PC+1+offset, 6)))
        incrementPC(offset+1)
    # Jump Condition
    elif ((high >> 4) & 0b_0000_1111) == 0b_1001:
        cond = high & 0b_0000_1111
        offset = signed8(low)   # Offset is signed !
        mnemonic = 'J' + condsuffix(cond)
        print_instruction(PC*2, '%s\t%s' % (mnemonic, hex(offset, 2)), 'Dest = %s' % (hex(PC+1+offset, 6)))
        if conditionMatched(cond):
            print_execution(f"Condition {bcolors.JUMP}MATCHED{bcolors.ENDC}{bcolors.EXECUTION}")
            incrementPC(offset+1)
        else:
            incrementPC()
    # RW Mem (direct)
    elif ((high >> 5) & 0b_0000_0111) == 0b_101:
        r = (high & 0b_0001_0000) >> 4       # r=0: DM(imm) <= Reg      r=1: Reg <= DM(imm)
        hash = (high & 0b_0000_1000) >> 3    # Offset[8]
        reg = high & 0b_0000_0111
        offset = (hash << 8) | low
        if r:
            print_instruction(PC*2, '%s = DM(%s)' % (register(reg), hex(offset, 3)), '', True)
            setRegisterFromRAMDirect(register(reg), offset)
        else:
            print_instruction(PC*2, 'DM(%s) = %s' % (hex(offset, 3), register(reg)), '', True)
            setRAMFromRegisterDirect(offset, register(reg))
        incrementPC()
    # Load Immediate
    elif ((high >> 5) & 0b_0000_0111) == 0b_110 and ((high >> 3) & 0b_0000_0011) != 0b_01:
        L = (high & 0b_0001_1000) >> 3       # L=00: Load High, Keep Low     L=10: Keep High, Load Low       L=11: Clear High, Load Low
        reg1 = high & 0b_0000_0111
        imm = low
        print_instruction(PC*2, '%s%s = %s' % (register1(reg1), hilo(L), hex(imm, 2)))
        setRegisterImmediate(register1(reg1), hilo(L), imm)
        incrementPC()
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
        print_instruction(PC*2, 'RAM(Ix%s%s) = %s' % (Ix, modif, operation), '', True)
        computeAUWithRegistersToRAM('Ix%s' % Ix, A, AU, first_operand, second_operand)
        incrementPC()
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
        print_instruction(PC*2, '%s = %s' % (register(reg), operation))
        computeLU1(register(reg), LU1, first_operand, second_operand)
        incrementPC()
    # LU(2)
    elif ((high >> 3) & 0b_0001_1111) == 0b_11001 and ((low >> 7) & 0b_0000_0001) == 0b_1 and ((low >> 2) & 0b_0000_0001) == 0b_1:
        _f = high & 0b_0000_0001              # 0: r0    1: r1
        Cst_x = ((high & 0b_0000_0110) << 1) | ((low & 0b_0110_0000) >> 5)
        LU2 = (low & 0b_0001_1000) >> 3
        Yop = (low & 0b_0000_0011)
        operand = operand2(Yop)
        mnemonic = lu2(LU2)
        print_instruction(PC*2, 'R%s = %s.%d\t%s' % (_f, mnemonic, Cst_x, operand))
        computeLU2('R%s' % _f, LU2, Cst_x, operand)
        incrementPC()
    # RW SRAM (indirect)
    elif ((high >> 3) & 0b_0001_1111) == 0b_11100 and ((low >> 7) & 0b_0000_0001) == 0b_0 and (low & 0b_0000_0011) == 0b_00:
        reg = high & 0b_0000_0111
        r = (low & 0b_0100_0000) >> 6        # r=0: RAM(offset) <= Reg      r=1: Reg <= RAM(offset)
        A = (low & 0b_0011_0000) >> 4        # A=00: No Change  A=01: By Modifier   A=10: +1    A=11: -1
        Ixy = (low & 0b_0000_1100) >> 2      # 00: Ix0   01: Ix1    10: Iy0     11: Iy1
        modif = modifier(A)                  # Modifier indicates how the data address (indirect register Ix/y) is incremented after the operation (not incremented, +1, -1, +modifier register lm)
        ind = indirect(Ixy)
        if r:
            print_instruction(PC*2, '%s = RAM(%s%s)' % (register(reg), ind, modif))
            setRegisterFromRAM(register(reg), ind, A)
        else:
            print_instruction(PC*2, 'RAM(%s%s) = %s' % (ind, modif, register(reg)))
            setRAMFromRegister(ind, A, register(reg))
        incrementPC()
    # Load ROM (indirect)
    elif ((high >> 3) & 0b_0001_1111) == 0b_11100 and ((low >> 6) & 0b_0000_0011) == 0b_01 and (low & 0b_0000_0011) == 0b_01:
        reg = high & 0b_0000_0111
        A = (low & 0b_0011_0000) >> 4        # A=00: No Change  A=01: By Modifier   A=10: +1    A=11: -1
        Ixy = (low & 0b_0000_1100) >> 2      # 00: Ix0   01: Ix1    10: Iy0     11: Iy1
        modif = modifier(A)                  # Modifier indicates how the data address (indirect register Ix/y) is incremented after the operation (not incremented, +1, -1, +modifier register lm)
        ind = indirect(Ixy)
        print_instruction(PC*2, '%s = ROM(%s%s)' % (register(reg), ind, modif))
        setRegisterFromROM(register(reg), ind, A)
        incrementPC()
    # Shift index
    elif ((high >> 3) & 0b_0001_1111) == 0b_11100 and ((low >> 6) & 0b_0000_0011) == 0b_01 and (low & 0b_0000_0111) == 0b_010:
        reg = high & 0b_0000_0111
        _f = (low & 0b_0010_0000) >> 5       # 0: r0    1: r1
        sf = (low & 0b_0001_1000) >> 3       # 00: Shift Left Sign Extension    01: A/L Shift Left  10: A Shift Right   11: L Shift Right
        mnemonic = shift(sf)
        # Number of bits to shift is determined by the ShIdx I/O (0x003e)
        print_instruction(PC*2, 'R%s = %s.Idx %s' % (_f, mnemonic, register(reg)), '', True)
        computeShiftWithIndex('R%s' % _f, sf, register(reg))
        incrementPC()
    # I/O (1)
    elif ((high >> 3) & 0b_0001_1111) == 0b_11100 and ((low >> 7) & 0b_0000_0001) == 0b_1:
        r = (high & 0b_0000_0100) >> 2        # r=0: IO(offset) <= RegL      r=1: RegL <= IO(offset)
        regL = (high & 0b_0000_0011)
        offset = low & 0b_0111_1111
        if r:
            print_instruction(PC*2, '%s = IO(%s)' % (registerL(regL), hex(offset, 2)), 'I/O register = %s' % (ioRegisterLabel(offset)))
            setRegFromIO(registerL(regL), ioRegisterLabel(offset))
        else:
            print_instruction(PC*2, 'IO(%s) = %s' % (hex(offset, 2), registerL(regL)), 'I/O register = %s' % (ioRegisterLabel(offset)))
            setIOFromReg(ioRegisterLabel(offset), registerL(regL))
        incrementPC()
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
        print_instruction(PC*2, '%s = %s' % (register(regDst), operation), '', True)
        computeAUWithRegisters(register(regDst), AU, first_operand, second_operand)
        incrementPC()
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
        print_instruction(PC*2, 'MR = %s%s' % (operation, operation2), '', True)
        print_error('NOT YET IMPLEMENTED')
        # FIXME Also update MOF flag
        incrementPC()
    # Reg Move
    elif high == 0b_1111_1000 and (low & 0b_0000_0011) == 0b_00:
        regSrc = (low & 0b_1110_0000) >> 5
        regDst = (low & 0b_0001_1100) >> 2
        print_instruction(PC*2, '%s = %s' % (register(regDst), register(regSrc)))
        regMove(register(regDst), register(regSrc))
        incrementPC()
    # Push / Pop
    elif high == 0b_1111_1000 and (low & 0b_0001_1110) >> 1 == 0b_0001:
        reg = (low & 0b_1110_0000) >> 5
        U = low & 0b_0000_0001               # 0: push  1: pop
        mnemonic = pushpop(U)
        print_instruction(PC*2, '%s %s' % (mnemonic, register(reg)))
        pushPopRegister(U, register(reg))
        incrementPC()
    # Shift
    elif ((high >> 1) & 0b_0111_1111) == 0b_111_1101:
        _f = high & 0b_0000_0001             # 0: r0    1: r1
        reg = (low & 0b_1110_0000) >> 5
        sf = (low & 0b_0001_1000) >> 3       # 00: Shift Left Sign Extension    01: A/L Shift Left  10: A Shift Right   11: L Shift Right
        sh = low & 0b_0000_0111              # Number of bits to shift (000: 1, 001: 2, ...)
        mnemonic = shift(sf)
        print_instruction(PC*2, 'R%s = %s.%s %s' % (_f, mnemonic, (sh+1), register(reg)), '', True)
        computeShift('R%s' % _f, sf, sh+1, register(reg))
        incrementPC()
    # I/O (2) + Push / Pop I/O
    elif high == 0b_1111_1100 and (low & 0b_1000_0000) >> 7 == 0b_1:
        r = (low & 0b_0100_0000) >> 6        # 0: Push IO(offset)   1: Pop IO(offset)
        offset = low & 0b_0011_1111
        mnemonic = pushpop(r)
        print_instruction(PC*2, '%s IO(%s)' % (mnemonic, hex(offset, 2)), 'I/O register = %s' % (ioRegisterLabel(offset)), True)
        pushPopIO(r, ioRegisterLabel(offset))
        incrementPC()
    # Reserved  FIXME Should throw en error ???
    elif high == 0b_1111_1100 and (low & 0b_1000_0000) >> 7 == 0b_0:
        print_instruction(PC*2, 'Reserved', '', True)
        print_error('NOT YET IMPLEMENTED')
        incrementPC()
    # Callff (2-words instruction)
    elif high == 0b_1111_1101:
        abs_addr_high = low
        second_word = getOpCode(PC+1)
        #print('%s %s' % (hex(second_word[0],2), hex(second_word[1],2)))
        abs_addr_low = second_word
        abs_addr = (abs_addr_high << 16) | abs_addr_low
        print_instruction(PC*2, 'Callff\t%s' % (hex(abs_addr, 6)), '', True)
        retAddr = PC+2
        retH = (retAddr >> 16) & 0xff
        retL = retAddr & 0xffff
        push(retL)
        push(retH)
        setPC(abs_addr)
    # Jumpff (2-words instruction)
    elif high == 0b_1111_1110:
        abs_addr_high = low
        second_word = getOpCode(PC+1)
        #print('%s %s' % (hex(second_word[0],2), hex(second_word[1],2)))
        abs_addr_low = second_word
        abs_addr = (abs_addr_high << 16) | abs_addr_low
        print_instruction(PC*2, 'Jmpff\t%s' % (hex(abs_addr, 6)), '', True)
        setPC(abs_addr)
    # Do0   FIXME No operation documentation??? Should fail ???
    elif high == 0b_1111_1100 and (low & 0b_1100_0000) >> 6 == 0b_00:
        cntV = low & 0b_0011_1111
        print_instruction(PC*2, 'Do0\t%s' % (cntV), '', True)
        print_error('NOT YET IMPLEMENTED')
        incrementPC()
    # Do1   FIXME No operation documentation??? Should fail ???
    elif high == 0b_1111_1100 and (low & 0b_1100_0000) >> 6 == 0b_01:
        cntV = low & 0b_0011_1111
        print_instruction(PC*2, 'Do1\t%s' % (cntV), '', True)
        print_error('NOT YET IMPLEMENTED')
        incrementPC()
    # Loop0 FIXME No operation documentation??? Should fail ???
    elif high == 0b_1111_1111 and low == 0b_1111_1100:
        print_instruction(PC*2, 'Loop0', '', True)
        print_error('NOT YET IMPLEMENTED')
        incrementPC()   # FIXME
    # Loop1 FIXME No operation documentation??? Should fail ???
    elif high == 0b_1111_1111 and low == 0b_1111_1110:
        print_instruction(PC*2, 'Loop1', '', True)
        print_error('NOT YET IMPLEMENTED')
        incrementPC()   # FIXME
    # Ret
    elif high == 0b_1111_1111 and low == 0b_0100_0000:
        print_instruction(PC*2, 'Ret')
        retAddr = pop()
        setPC(retAddr)
    # Reti
    elif high == 0b_1111_1111 and low == 0b_0100_0001:
        print_instruction(PC*2, 'Reti')
        retH = pop()
        retL = pop()
        retAddr = (retH << 16) | retL
        setPC(retAddr)
    # Retff
    elif high == 0b_1111_1111 and low == 0b_0100_0010:
        print_instruction(PC*2, 'Retff')
        retH = pop()
        retL = pop()
        retAddr = (retH << 16) | retL
        setPC(retAddr)
    # ICEC  FIXME Unused ???
    elif high == 0b_1111_1111 and low == 0b_1111_1101:
        print_instruction(PC*2, 'ICE Call Function', '', True)
        print_error('NOT YET IMPLEMENTED')
        incrementPC()
    # NOP
    elif high == 0b_1111_1111 and low == 0b_1111_1111:
        print_instruction(PC*2, 'Nop')
        incrementPC()
    # DisSPSW   FIXME Undocumented ?! Should fail ??? (Clear SCR.SPSW)
    elif high == 0b_1111_1111 and low == 0b_0000_0001:
        print_instruction(PC*2, 'DisSPSW', '', True)
        print_error('NOT YET IMPLEMENTED')
        incrementPC()
    # EnSPSW    FIXME Undocumented ?! Should fail ??? (Enable SCR.SPSW write)
    elif high == 0b_1111_1111 and low == 0b_1111_1111:
        print_instruction(PC*2, 'EnSPSW', ', True')
        print_error('NOT YET IMPLEMENTED')
        incrementPC()
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
        print_instruction(PC*2, 'EMAC')
        print_error('NOT YET IMPLEMENTED')
        incrementPC()
    # Unhandled opcode
    else:
        print('%s\tUNKNOWN' % hex(PC*2,6))
        print_error('UNKNOWN INSTRUCTION')
        raise
        # TODO Should break and throw an error
