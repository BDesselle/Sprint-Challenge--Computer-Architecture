"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000

CMP = 0b10100111
JMP = 0b01010100
JNE = 0b01010110
JEQ = 0b01010101


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.registers = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.sp = 7
        self.registers[7] = 0xF4
        self.flags = {}
        self.branchtable = {}
        self.branchtable[ADD] = self.add
        self.branchtable[LDI] = self.ldi
        self.branchtable[PRN] = self.prn
        self.branchtable[MUL] = self.mul
        self.branchtable[PUSH] = self.push
        self.branchtable[POP] = self.pop
        self.branchtable[CALL] = self.call
        self.branchtable[RET] = self.ret
        self.branchtable[JMP] = self.jmp
        self.branchtable[JNE] = self.jne
        self.branchtable[JEQ] = self.jeq
        self.branchtable[CMP] = self.cmp_func

    def load(self, filename):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        program = []

        try:
            address = 0
            with open(filename) as f:
                for line in f:
                    comment_split = line.split("#")
                    num = comment_split[0].strip()

                    if num == "":
                        continue  # Ignore irrelevant lines

                    value = int(num, 2)

                    program.append(value)

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {filename} Not Found")
            sys.exit(1)

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        a = self.registers[reg_a]
        b = self.registers[reg_b]

        if op == "ADD":
            self.registers[reg_a] += self.registers[reg_b]
        # elif op == "SUB": etc
        elif op == "MUL":
            self.registers[reg_a] *= self.registers[reg_b]
        elif op == "CMP":
            if a == b:
                self.flags['E'] = 1
            else:
                self.flags['E'] = 0
            if a < b:
                self.flags['L'] = 1
            else:
                self.flags['L'] = 0
            if a > b:
                self.flags['G'] = 1
            else:
                self.flags['G'] = 0
        else:
            raise Exception("Unsupported ALU operation")

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def jeq(self, a=None, b=None):
        if self.flags['E'] == 1:
            self.pc = self.registers[a]
        else:
            self.pc += 2

    def jmp(self, a=None, b=None):
        self.pc = self.registers[a]

    def jne(self, a=None, b=None):
        if self.flags['E'] == 0:
            self.pc = self.registers[a]
        else:
            self.pc += 2

    def cmp_func(self, a=None, b=None):
        self.alu("CMP", a, b)

    def ldi(self, a=None, b=None):
        self.registers[a] = b

    def prn(self, a=None, b=None):
        print(self.registers[a])

    def add(self, a=None, b=None):
        self.alu("ADD", a, b)

    def mul(self, a=None, b=None):
        self.alu("MUL", a, b)

    def push(self, a=None, b=None):
        self.registers[self.sp] -= 1
        val = self.registers[a]
        self.ram_write(self.registers[self.sp], val)

    def pop(self, a=None, b=None):
        val = self.ram_read(self.registers[self.sp])
        self.registers[a] = val
        self.registers[self.sp] += 1

    def call(self, a=None, b=None):
        val = self.pc + 2
        self.registers[self.sp] -= 1
        self.ram_write(self.registers[self.sp], val)
        reg = self.ram_read(self.pc + 1)
        addr = self.registers[reg]
        self.pc = addr

    def ret(self, a=None, b=None):
        ret_addr = self.registers[self.sp]
        self.pc = self.ram_read(ret_addr)
        self.registers[self.sp] += 1

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        running = True

        jumps = [CALL, RET, JEQ, JNE, JMP]

        while running:
            IR = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            if IR == HLT:
                print("Exiting program...")
                running = False
                print("Program exited")
            elif IR in jumps:
                self.branchtable[IR](operand_a, operand_b)
            elif IR in self.branchtable:
                self.branchtable[IR](operand_a, operand_b)
                self.pc += (IR >> 6) + 1
            else:
                print(IR)
