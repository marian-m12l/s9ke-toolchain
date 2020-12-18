; Test asm file

seek(0x000000)
    jmpff .reset_handler        ; Reset interrupt handler
seek(0x000014)
    jmpff .ad_handler           ; AD FIFO full interrupt handler
seek(0x000018)
    jmpff .t0_handler           ; Timer 0 overflow interrupt handler
seek(0x00001c)
    jmpff .p00_handler          ; P0.0 falling/rising edge interrupt handler
seek(0x000020)
    jmpff .t1_handler           ; Timer 1 overflow interrupt handler
seek(0x000024)
    jmpff .p01_handler          ; P0.1 falling/rising edge interrupt handler
seek(0x000028)
    jmpff .t2_handler           ; Timer 2 overflow interrupt handler
seek(0x00002c)
    jmpff .p02_handler          ; P0.2 falling/rising edge interrupt handler
seek(0x000034)
    jmpff .da_handler           ; DA FIFO empty interrupt handler
seek(0x000038)
    jmpff .spi_handler          ; SPI interrupt handler
seek(0x00003c)
    jmpff .msp_handler          ; MSP / I2C interrupt handler
seek(0x000040)
    jmpff .i2s_handler          ; I2S interrupt handler
seek(0x000050)
    jmpff .usb_handler          ; USB interrupt handler
seek(0x000054)
    jmpff .cis_handler          ; CIS HREF interrupt handler
seek(0x000058)
    jmpff .rtc_handler          ; RTC overflow interrupt handler
seek(0x00005c)
    jmpff .nf_handler           ; Nand Flash interrupt handler
seek(0x000060)
    jmpff .dma_cis_w_handler    ; DMA CIS Write interrupt handler
seek(0x000064)
    jmpff .dma_nf_rw_handler    ; DMA Nand Flash R/W interrupt handler
seek(0x000068)
    jmpff .sar_ad_handler       ; SAR ADC interrupt handler
seek(0x000078)
    jmpff .dma_dev_rw_handler   ; DMA DEV R/W interrupt handler

seek(0x000080)
.reset_handler:
    Call .routine1
    Call 0x0100
    Jmp .jmpLabel
    X0 = 0x01
    Y1 = 0x01
.jmpLabel:
    Jmp 0xffd
.jcondLabel:
    Y0 = X0 + 1
    Jeq 0xfe
    Jne 0xfd
    Jgt 0xfc
    Jge 0xfb
    Jlt 0xfa
    Jle 0xf9
    Jav 0xf8
    Jnav 0xf7
    Jac 0xf6
    Jnac 0xf5
    Jmr0s 0xf4
    Jmr0ns 0xf3
    Jmv 0xf2
    Jnmv 0xf1
    Jixv 0xf0
    Jirr 0xef
    Jeq .jcondlabel
    Jne .jcondlabel
    Jgt .jcondlabel
    Jge .jcondlabel
    Jlt .jcondlabel
    Jle .jcondlabel
    Jav .jcondlabel
    Jnav .jcondlabel
    Jac .jcondlabel
    Jnac .jcondlabel
    Jmr0s .jcondlabel
    Jmr0ns .jcondlabel
    Jmv .jcondlabel
    Jnmv .jcondlabel
    Jixv .jcondlabel
    Jirr .jcondlabel
    DM(0x000) = X0
    Y1 = DM(0x123)
    X0.l = 0x00
    X0.h = 0x01
    X1.l = 0xff
    X1.h = 0xff
    Ix0 = 0x01
    RAM(Ix0) = R0 + 1
    RAM(Ix1, 1) = X1 - 1
    RAM(Ix0, -1) = R1 + Y1
    RAM(Ix1, m) = R1 + Y1 + C
    RAM(Ix1) = R0 - R1
    RAM(Ix0, m) = R0 - R0 + C - 1
    RAM(Ix1) = -R0 + Y1
    RAM(Ix0, m) = -R1 + Y0 + C - 1
    X0 = X1 AND Y1
    MR0 = R1 OR R1
    R0 = X1 XOR R0
    X1 = NOT X1
    R0 = BSET.1 R0
    R0 = BCLR.8 Y1
    R0 = BTST.15 Y0
    R0 = BTOG.4 R1
    RAM(Ix0) = X1
    RAM(Ix1, -1) = R0
    RAM(Iy0, 1) = X1
    RAM(Iy1, m) = X0
    MR0 = RAM(Ix0)
    MR1 = RAM(Iy1, 1)
    X0 = RAM(Iy0, -1)
    R1 = RAM(Ix1, m)
    MR0 = ROM(Ix0)
    X1 = ROM(Ix0, 1)
    R0 = ROM(Ix0, -1)
    MR1 = ROM(Iy1, m)
    R1 = SRA.Idx X0
    R0 = SRL.Idx X1
    R1 = SL.Idx MR0
    R1 = IO(0x02)
    IO(0x7f) = X0
    ; TODO AU1
    X0 = R0 + 1
    X1 = X1 - 1
    Y0 = R1 + Y1
    Y1 = R1 + Y1 + C
    R0 = R0 - R1
    R1 = R0 - R0 + C - 1
    MR0 = -R0 + Y1
    MR1 = -R1 + Y0 + C - 1
    MR0 = R1
    Push MR0
    Pop Y1
    R1 = SRA.5 X0
    R0 = SRL.8 X1
    R1 = SL.1 MR0
    Callff .routine2
    Callff 0x000200
    Jmpff .jmpLabel
    Jmpff 0x000080

.routine1:
    X0 = 0x01
    Ret
.routine2:
    X0 = 0x02
    Retff
seek(0x000100)
    X0 = 0x10
    Ret
seek(0x000200)
    X0 = 0x20
    Retff

.ad_handler:
    Nop
    Reti
.t0_handler:
    Nop
    Reti
.p00_handler:
    Nop
    Reti
.t1_handler:
    Nop
    Reti
.p01_handler:
    Nop
    Reti
.t2_handler:
    Nop
    Reti
.p02_handler:
    Nop
    Reti
.da_handler:
    Nop
    Reti
.spi_handler:
    Nop
    Reti
.msp_handler:
    Nop
    Reti
.i2s_handler:
    Nop
    Reti
.usb_handler:
    Nop
    Reti
.cis_handler:
    Nop
    Reti
.rtc_handler:
    Nop
    Reti
.nf_handler:
    Nop
    Reti
.dma_cis_w_handler:
    Nop
    Reti
.dma_nf_rw_handler:
    Nop
    Reti
.sar_ad_handler:
    Nop
    Reti
.dma_dev_rw_handler:
    Nop
    Reti
