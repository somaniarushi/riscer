# Bytecode to RISC Converter

Reference: https://cs61c.org/resources/pdf?file=riscvcard_large.pdf

## Design Document
Input: 32-bit bytecode
Output: <instruction name> <register name> <register name / immediate>

### Getting Instruction Name

#### Getting Opcode
This is the first step of the process, to understand how the other parts of the bytecode work, and which part of the bytecode computes to an immediate or a register or multiple registers! **The last 7 bytes of the input are always the opcode.**

#### Getting Instruction Type
Based on different opcodes, we have different instruction types, that are formatted differently.
"0110011": "R",     # R-Type Operations
"0000011": "I_L",   # I-Type Operations, Load Operations
"0010011": "I",     # I-Type Operations, standard
"0100011": "S",     # S-Type Operations
"1100011": "SB",    # SB-Type Operations
"0010111": "U_1",   # U-Type Operations, PC-ref
"0110111": "U_2",   # U-Type Operations, non-PC-ref
"1101111": "UJ",    # UJ-Type Operations
"1100111": "I",     # I-Type Operations, jalr

#### Getting Instruction Name
Once we have a instruction type, we have to occassionally use the 