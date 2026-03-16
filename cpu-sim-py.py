#!/usr/bin/env python3
"""Simple 8-bit CPU simulator with registers, ALU, and memory."""
import sys

class CPU:
    def __init__(self,mem_size=256):
        self.regs=[0]*8  # R0-R7
        self.mem=[0]*mem_size;self.pc=0;self.flags={'Z':0,'C':0,'N':0}
        self.halted=False
    def _set_flags(self,val):
        self.flags['Z']=int(val==0);self.flags['N']=int(val<0);self.flags['C']=int(val>255 or val<0)
        return val&0xFF
    def run(self,program,max_steps=10000):
        self.mem[:len(program)]=program;self.pc=0;steps=0
        while not self.halted and steps<max_steps:
            op=self.mem[self.pc];self.pc+=1;steps+=1
            if op==0x00:self.halted=True  # HLT
            elif op==0x01:  # MOV Rd, imm
                rd=self.mem[self.pc];imm=self.mem[self.pc+1];self.pc+=2;self.regs[rd]=imm
            elif op==0x02:  # MOV Rd, Rs
                rd=self.mem[self.pc];rs=self.mem[self.pc+1];self.pc+=2;self.regs[rd]=self.regs[rs]
            elif op==0x03:  # ADD Rd, Rs
                rd=self.mem[self.pc];rs=self.mem[self.pc+1];self.pc+=2
                self.regs[rd]=self._set_flags(self.regs[rd]+self.regs[rs])
            elif op==0x04:  # SUB Rd, Rs
                rd=self.mem[self.pc];rs=self.mem[self.pc+1];self.pc+=2
                self.regs[rd]=self._set_flags(self.regs[rd]-self.regs[rs])
            elif op==0x05:  # MUL Rd, Rs
                rd=self.mem[self.pc];rs=self.mem[self.pc+1];self.pc+=2
                self.regs[rd]=self._set_flags(self.regs[rd]*self.regs[rs])
            elif op==0x06:  # CMP Rd, Rs
                rd=self.mem[self.pc];rs=self.mem[self.pc+1];self.pc+=2
                self._set_flags(self.regs[rd]-self.regs[rs])
            elif op==0x10:  # JMP addr
                self.pc=self.mem[self.pc]
            elif op==0x11:  # JZ addr
                addr=self.mem[self.pc];self.pc+=1
                if self.flags['Z']:self.pc=addr
            elif op==0x12:  # JNZ addr
                addr=self.mem[self.pc];self.pc+=1
                if not self.flags['Z']:self.pc=addr
            elif op==0x20:  # LOAD Rd, [addr]
                rd=self.mem[self.pc];addr=self.mem[self.pc+1];self.pc+=2;self.regs[rd]=self.mem[addr]
            elif op==0x21:  # STORE [addr], Rs
                addr=self.mem[self.pc];rs=self.mem[self.pc+1];self.pc+=2;self.mem[addr]=self.regs[rs]
            elif op==0x30:  # INC Rd
                rd=self.mem[self.pc];self.pc+=1;self.regs[rd]=self._set_flags(self.regs[rd]+1)
            elif op==0x31:  # DEC Rd
                rd=self.mem[self.pc];self.pc+=1;self.regs[rd]=self._set_flags(self.regs[rd]-1)
        return steps

def main():
    if len(sys.argv)>1 and sys.argv[1]=="--test":
        cpu=CPU()
        # R0=5, R1=3, R0=R0+R1=8
        prog=[0x01,0,5, 0x01,1,3, 0x03,0,1, 0x00]
        cpu.run(prog)
        assert cpu.regs[0]==8,f"R0={cpu.regs[0]}"
        # Loop: count down from 5
        cpu2=CPU()
        prog2=[0x01,0,5, 0x31,0, 0x12,3, 0x00]  # MOV R0,5; DEC R0; JNZ 3; HLT
        cpu2.run(prog2)
        assert cpu2.regs[0]==0
        # MUL
        cpu3=CPU()
        prog3=[0x01,0,6, 0x01,1,7, 0x05,0,1, 0x00]
        cpu3.run(prog3)
        assert cpu3.regs[0]==42,f"6*7={cpu3.regs[0]}"
        # Memory load/store
        cpu4=CPU();cpu4.mem[200]=99
        prog4=[0x20,0,200, 0x00]  # LOAD R0,[200]; HLT
        cpu4.run(prog4)
        assert cpu4.regs[0]==99
        print("All tests passed!")
    else:
        cpu=CPU();cpu.run([0x01,0,6,0x01,1,7,0x05,0,1,0x00])
        print(f"6 × 7 = {cpu.regs[0]}")
if __name__=="__main__":main()
