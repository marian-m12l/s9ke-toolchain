A toolchain for SONiX S9KE DSP Core
===================================

This repository hosts a series of tools targeting the S9KE DSP core, which is shared by several SONiX SoCs like SNC7001A or SNP70032.


DISCLAIMER
----------

This software is still in a **very** early stage of development, and as such is, well... pretty crappy and unreliable. USE AT YOUR OWN RISK.

I am (and this work is) in no way affiliated with SONiX.


USAGE
-----

### Prerequisite

* Python 3

### General observations

A few characteristics of the DSP to keep in mind:
- Works with 16-bit words
- Little-endian
- All addresses are **word addresses*

Memory organization:
- Internal registers (16 bits): `X0`, `X1`, `Y0`, `Y1`, `R0`, `R1`, `MR0`, `MR1`
- I/O registers (16 bits mostly, some are 8 bits): `0x00` to `0x7f`
- PRAM (Program RAM): 32K words on the SNC7001A (`0x000000-0x007fff`)
- WRAM (Working RAM): 16K words on the SNC7001A, shared with additional PRAM configured by SYSCONF register (`0x000000-0x003fff`)
- Additional PRAM (0 to 12KW) shared with WRAM (`0x200000-0x201fff`)
- CS1 SPI Flash External Program Memory is mapped to `0x400000-0xbfffff`
- Memory mapped devices
    - USB Control Register (`0xe000-0xe9ff`)
    - Nand Flash / SD Card Register (`0xf000-0xf0ff`)
    - DMA Schedule Register (`0xf100-0xf1ff`)
    - Fractional PLL Register (`0xf300-0xf303`)
    - SPI Flash Register (`0xf800-0xf8ff`)
    - DMA1 Control Register (`0xfe27-0xfe2c`)

Links to the reference documentation from SONiX:
- [SNP70032 Programming Guide](http://www.sonix.com.tw/files/1/5276A1A128C1C1C2E050007F01006B42)
- [SNP70032 Application Note](http://www.sonix.com.tw/files/1/5276B03253141849E050007F010070E8)
- [SNP70032 Spec Sheet](http://www.sonix.com.tw/files/1/5276ABD22E860967E050007F01006FB4)
- [SNC7001A Spec Sheet](http://www.sonix.com.tw/files/1/99D017BD23A88753E050007F0100100A)

#### I/O Registers

| Label           | Description                 | Offset |
| --------------- | --------------------------- | ------ |
| SSF             | System Status Flag          | 0x00 |
| SCR             | System Control              | 0x01 |
| Ix0             | Indirect Addressing x0      | 0x02 |
| Ix1             | Indirect Addressing x1      | 0x03 |
| Im00            | Ix0/Iy0 Modifier 0          | 0x04 |
| Im01            | Ix0/Iy0 Modifier 1          | 0x05 |
| Im02            | Ix0/Iy0 Modifier 2          | 0x06 |
| Im03            | Ix0/Iy0 Modifier 3          | 0x07 |
| Im10            | Ix1/Iy1 Modifier 0          | 0x08 |
| Im11            | Ix1/Iy1 Modifier 1          | 0x09 |
| Im12            | Ix1/Iy1 Modifier 2          | 0x0a |
| Im13            | Ix1/Iy1 Modifier 3          | 0x0b |
| OPM_CONTROL     | Operation mode Control      | 0x0c |
| RAMBk           | RAM Bank Selector           | 0x0d |
| Ix0Bk           | Ix0 Bank Selector           | 0x0e |
| Ix1Bk           | Ix1 Bank Selector           | 0x0f |
| T0              | Timer 0                     | 0x10 |
| T1              | Timer 1                     | 0x11 |
| T2              | Timer 2                     | 0x12 |
| Iy0             | Indirect Addressing y0      | 0x13 |
| Iy1             | Indirect Addressing y1      | 0x14 |
| PCH             | Program Counter High        | 0x15 |
| PCL             | Program Counter Low         | 0x16 |
| MMR             | MAC mode                    | 0x17 |
| Sp              | Stack Pointer               | 0x18 |
| MR2             | Sign Extension / MR2        | 0x19 |
| Iy0Bk           | Iy0 ROM Bank Selector       | 0x1a |
| Iy1Bk           | Iy1 ROM Bank Selector       | 0x1b |
| Iy0BkRAM        | Iy0 RAM Bank Selector       | 0x1c |
| Iy1BkRAM        | Iy1 RAM Bank Selector       | 0x1d |
| Ix2             | Indirect Addressing x2      | 0x1e |
| Iy2             | Indirect Addressing y2      | 0x1f |
| INTEN           | Interrupt Channel Enable    | 0x20 |
| INTRQ           | Interrupt Channel Request   | 0x21 |
| INTPR           | Interrupt Channel Priority  | 0x22 |
| INTCR           | Interrupt Channel Clear Req | 0x23 |
| PCR1            | Peripheral Control 1        | 0x24 |
| OPM_CTRL1       | Operation Mode Control 1    | 0x25 |
| ADC_FIFOSTATUS  | ADC FIFO Status             | 0x26 |
| ADC_DATA        | ADC Result                  | 0x28 |
| WDT             | Watch Dog Timer             | 0x29 |
| ADC_SET1        | Control ADC Signal 1        | 0x2a |
| ADC_SET2        | Control ADC Signal 2        | 0x2b |
| ImxL            | Ix2 Modifier Linear Mode    | 0x2c |
| ImxC            | Ix2 Modifier Circular Mode  | 0x2d |
| ImyL            | Iy2 Modifier Linear Mode    | 0x2e |
| ImyC            | Iy2 Modifier Circular Mode  | 0x2f |
| P0WKUPEN        | P0 Wake Up Enable           | 0x30 |
| P1WKUPEN        | P1 Wake Up Enable           | 0x31 |
| INTEN2          | Interrupt Channel Enable    | 0x32 |
| INTRQ2          | Interrupt Channel Request   | 0x33 |
| INTPR2          | Interrupt Channel Priority  | 0x34 |
| INTCR2          | Interrupt Channel Clear Req | 0x35 |
| IBx             | Ix2 Base Address            | 0x36 |
| ILx             | Ix2 Length                  | 0x37 |
| IBy             | Iy2 Base Address            | 0x38 |
| ILy             | Iy2 Length                  | 0x39 |
| IOSW            | I/O Byte Swap               | 0x3a |
| SP1             | Stack Pointer 2 For OS      | 0x3b |
| IOSW2           | I/O Byte Swap 2             | 0x3c |
| EVENT           | Timer Event Control         | 0x3d |
| ShIdx           | Index Shift Amount          | 0x3e |
| ShV2            | Shift Result                | 0x3f |
| T1CNTV          | Counter Value of T1         | 0x40 |
| T0CNT           | Timer 0 Counter             | 0x45 |
| T1CNT           | Timer 1 Counter             | 0x46 |
| T0CNTV          | Counter Value of T0         | 0x47 |
| INTEC           | Interrupt Edge Control      | 0x48 |
| DAC_SET1        | Control DAC Signal 1        | 0x49 |
| DAC_SET2        | Control DAC Signal 2        | 0x4a |
| DAC_FIFOSTATUS  | DAC FIFO Status             | 0x4b |
| T2CNT           | Timer 2 Counter             | 0x4c |
| EVENT0CNT       | EVENT0 Count Value          | 0x4d |
| EVENT1CNT       | EVENT1 Count Value          | 0x4e |
| EVENT2CNT       | EVENT2 Count Value          | 0x4f |
| I2SCTRL         | I2S Control                 | 0x50 |
| PWM0            | PWM Control of P0.3         | 0x51 |
| PWM1            | PWM Control of P0.4         | 0x52 |
| PWM2            | PWM Control of P0.5         | 0x53 |
| PWM3            | PWM Control of P0.6         | 0x54 |
| DAOL            | Left Channel DA Output      | 0x55 |
| DAOR            | Right Channel DA Output     | 0x56 |
| SPIDADA0        | SPI Data Buffer             | 0x57 |
| SPIDADA1        | SPI Data Buffer             | 0x58 |
| SPIDADA2        | SPI Data Buffer             | 0x59 |
| SPIDADA3        | SPI Data Buffer             | 0x5a |
| SPIDADA4        | SPI Data Buffer             | 0x5b |
| SPIDADA5        | SPI Data Buffer             | 0x5c |
| SPICTRL         | SPI Control Register        | 0x5d |
| SPICSC          | SPI Chip Select Control     | 0x5e |
| SPITRANSFER     | SPI Bit Transfer Control    | 0x5f |
| SPIBR           | SPI Baud Rate               | 0x61 |
| MSPSTAT         | MSP Status                  | 0x62 |
| MSPM1           | MSP Mode Register 1         | 0x63 |
| MSPM2           | MSP Mode Register 2         | 0x64 |
| MSPBUF          | MSP Data Buffer             | 0x65 |
| MSPADR          | MSP Address                 | 0x66 |
| CHIP_ID         | Chip ID                     | 0x67 |
| P0En            | I/O Port 0 Enable           | 0x68 |
| P0              | I/O Port 0                  | 0x69 |
| P0M             | I/O Port 0 Direction        | 0x6a |
| P0PH            | I/O Port 0 Pull-High        | 0x6b |
| P1En            | I/O Port 1 Enable           | 0x6c |
| P1              | I/O Port 1                  | 0x6d |
| P1M             | I/O Port 1 Direction        | 0x6e |
| P1PH            | I/O Port 1 Pull-High        | 0x6f |
| P3En            | I/O Port 3 Enable           | 0x74 |
| P3              | I/O Port 3                  | 0x75 |
| P3M             | I/O Port 3 Direction        | 0x76 |
| P3PH            | I/O Port 3 Pull-High        | 0x77 |
| P4En            | I/O Port 4 Enable           | 0x78 |
| P4              | I/O Port 4                  | 0x79 |
| P4M             | I/O Port 4 Direction        | 0x7a |
| P4PH            | I/O Port 4 Pull-High        | 0x7b |
| SYSCONF         | Internal System Config      | 0x7c |
| ADP             | SAR ADC Input Pin           | 0x7d |
| ADM             | SAR ADC Mode Control        | 0x7e |
| ADR             | SAR ADC Result              | 0x7f |


### Disassembler

Set the path to the ROM file (constant `FW`), then run the script to print assembly:

```
disassembler.py
```

### Emulator

Set the path to the ROM file (constant `FW`), optionally set some breakpoints in the `breakpoints` array, then run the script to start executing:

```
emulator.py
```

The emulator will load the ROM and position PC at address `0x000000`.
The emulator starts in "step-by-step" mode. You can pause the execution at any time with `^C`.
In step-by-step mode, a few commands are available:
- `c`: Continue execution
- `s` or just pressing `<enter>`: Step-by-step / Next instruction
- `reg`: Print internal registers
- `io <addr>|<label>`: Print I/O register
- `wram <addr>`: Print WRAM word
- `pram <addr>`: Print PRAM word
- `rom <addr>`: Print ROM word
- `q`: Quit

When executing an instruction, the emulator prints:
- The opcode address (both byte address and word address)
- The assembly mnemonic
- A potential EOL comment
- Any change happening to the internal registers, I/O registers, WRAM, Flags, ...


### Assembler

The assembler takes two arguments: the path to the source `.asm` file and the path to the output binary file:

```
assembler.py source.asm target.bin
```

There is a `test.asm` file that covers (almost) all instructions, and show how to use labels and "seek" guidelines.

**PLEASE NOTE THAT NO ASSEMBLED BINARY HAS BEEN TESTED ON AN ACTUAL DEVICE YET**


LICENSE
-------

This project is licensed under the terms of the **Mozilla Public License 2.0**. The terms of the license are in
the `LICENSE` file.
