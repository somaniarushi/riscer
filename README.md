# Bytecode to RISC Converter

Reference: https://cs61c.org/resources/pdf?file=riscvcard_large.pdf

## Usage
The file accepts either binary or hexadecimal codes. We have to tell the script what kind of code is being provided by passing either "bin" or "hex" as an argument to the script. 

To use the converter, clone this repo to your local machine and run the following command in your terminal:
```
python3 main.py [bin/hex] [code]
```
Eg: `python3 main.py hex 0x00b542b3` returns `xor t0, a0, a1`


## Design Document
Input: 32-bit bytecode
Output: <instruction name> <register name> <register name / immediate>

### Getting Instruction Name

#### Getting Opcode
This is the first step of the process, to understand how the other parts of the bytecode work, and which part of the bytecode computes to an immediate or a register or multiple registers! **The last 7 bytes of the input are always the opcode.**

#### Getting Instruction Type
Based on different opcodes, we have different instruction types, that are formatted differently. 

| Opcode | Type |
| -------| ------ |
| 0110011 | R-Type Operations | 
| 0000011 | I-Type Operations, Load Operations | 
| 0010011 | I-Type Operations, standard | 
| 0100011 | S-Type Operations | 
| 1100011 | SB-Type Operations | 
| 0010111 | U-Type Operations, PC-ref | 
| 0110111 | U-Type Operations, non-PC-ref | 
| 1101111 | UJ-Type Operations | 
| 1100111 | I-Type Operations, jalr | 



#### Getting Instruction Name
Once we have a instruction type, we have to use the func3 and func7 (sometimes) to get the name of the instruction. This is a deep lookup table.

#### Getting Arguments
Once we have the instruction name, based on the instruction type, we format different instructions differently

| Type | Format | 
| ----- | ------ |
| R-type | `inst rd rs1 rs2` | 
| I-type standard | `inst rd rs1 imm` | 
| I-type load | `inst rd imm(rs1)` |
| S-type | `inst rs2 imm(rs1)` |
| SB-type | `inst rs1 rs2 imm` | 
| U-type | `inst rd imm` |
| UJ-type | `inst rd imm` | 
| I-type jump | `inst rd rs1 imm` | 
