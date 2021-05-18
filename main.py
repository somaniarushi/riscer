import re
import binascii

################### Data storage ##################

## Defining A Dictionar`y for Conversion ##
opcode_dictionary = {
        "0110011": "R",     # R-Type Operations
        "0000011": "I_L",   # I-Type Operations, Load Operations
        "0010011": "I",     # I-Type Operations, standard
        "0100011": "S",     # S-Type Operations
        "1100011": "SB",    # SB-Type Operations
        "0010111": "U_1",   # U-Type Operations, PC-ref
        "0110111": "U_2",   # U-Type Operations, non-PC-ref
        "1101111": "UJ",    # UJ-Type Operations
        "1100111": "I",     # I-Type Operations, jalr
    }

instruction_dictionary = {
        # R-Types
        "0110011": {
                "000": {
                    "0000000": "add", 
                    "0000001": "mul", 
                    "0100000": "sub",
                },
                "001": {
                    "0000000": "sll",
                    "0000001": "mulh",
                },
                "011": {
                    "0000001": "mulhu",
                },
                "010": {
                    "0000000": "slt",
                },
                "100": {
                    "0000000": "xor",
                },
                "101": {
                    "0000000": "srl",
                    "0100000": "sra",
                },
                "110": {
                    "0000000": "or",
                },
                "111":{ 
                    "0000000": "and",
                },
            },
        # I-Types, Loading
        "0000011": {
                "000": "lb",
                "001": "lh", 
                "010": "lw",
            },
        # I-Types, standard
        "0010011": {
                "000": "addi",
                "001": {
                    "0000000": "slli",
                },
                "010": "slti",
                "100": "xori",
                "101": {
                    "0000000": "srli",
                    "0100000": "srai",
                },
                "110": "ori",
                "111": "andi",
            },
        # S-Types
        "0100011": {
                "000": "sb",
                "001": "sh",
                "010": "sw",
            },
        # SB-Types
        "1100011": {
                "000": "beq",
                "001": "bne",
                "100": "blt",
                "101": "bge",
                "110": "bltu",
                "111": "bgeu",
            },
        "0010111": "auipc",   # U-Type Operations, PC-ref
        "0110111": "lui",   # U-Type Operations, non-PC-ref
        "1101111": "jal",    # UJ-Type Operations
        "1100111": "jalr",     # I-Type Operations, jalr
    }

reg_name = {
    "00000": "x0",
    "00001": "ra",
    "00010": "sp",
    "00011": "gp",
    "00100": "tp",
    "00101": "t0",
    "00110": "t1",
    "00111": "t2",
    "01000": "s0",
    "01001": "s1",
    "01010": "a0",
    "01011": "a1",
    "01100": "a2",
    "01101": "a3",
    "01110": "a4",
    "01111": "a5",
    "10000": "a6",
    "10001": "a7",
    "10010": "s2",
    "10011": "s3",
    "10100": "s4",
    "10101": "s5",
    "10110": "s6",
    "10111": "s7",
    "11000": "s8",
    "11001": "s9",
    "11010": "s10",
    "11011": "s11",
    "11100": "t3",
    "11101": "t4",
    "11110": "t5",
    "11111": "t6"
}

################# RISC Translater #####################

def get_opcode(bytecode):
    '''
    Helper function that accepts a 32-bit bytecode and returns the last 7 bits of opcode.
    '''
    return bytecode[-7:]

def get_func3(bytecode):
    '''
    Helper function that accepts a 32-bit bytecode and returns the 12-14th last bits.
    '''
    return bytecode[-15:-12]

def get_func7(bytecode):
    '''
    Helper function that accepts a 32-bit bytecode and returns the top 7 bits.
    '''
    return bytecode[:7]

def get_inst_type(opcode):
    '''
    Accepts opcode and returns the instruction type of the bytecode using opcode dictionary.
    '''
    assert opcode in opcode_dictionary, "Opcode not recognized"
    return opcode_dictionary[opcode] 

def get_inst(opcode, func3, func7):
    '''
    Returns the name of the instruction 
    '''
    assert opcode in instruction_dictionary
    subtype = instruction_dictionary[opcode]
    if isinstance(subtype, dict):
        subsubtype = instruction_dictionary[opcode][func3]
        if isinstance(subsubtype, dict):
            subsubsubtype = instruction_dictionary[opcode][func3][func7]
            return subsubsubtype
        else:
            return subsubtype
    else:
        return subtype

def get_args(bytecode, type):
    '''
    Dispatches to different argument retrievers based on the type of the instruction format.
    '''
    if type == "R":
        return get_args_R(bytecode)
    if type == 'I':
        return get_args_I(bytecode)
    if type == 'I_L':
        return get_args_IL(bytecode)
    if type == 'S':
        return get_args_S(bytecode)
    if type == 'SB':
        return get_args_SB(bytecode)
    if type == 'U_1' or type == 'U_2':
        return get_args_U(bytecode)

def get_args_U(bc):
    '''
    Get the arguments of a U-type instruction.
    We return the following format: rd, imm
    '''
    def get_imm(bc):
        '''
        Get the value of the immediate as per the U type format. 
        '''
        return str(int(bc[0:20], 2))
    return f"{get_rd(bc)}, {get_imm(bc)}"

def get_args_SB(bc):
    '''
    Get the arguments of an SB type instruction.
    We return the following format: rs1, rs2, imm
    '''
    def get_imm(bc):
        '''
        Get the value of the immediate as per the SB type format.
        '''
        return str(hex(int(bc[0] + bc[-7] + bc[1:7] + bc[-12:-8], 2)))
    return f"{get_rs1(bc)}, {get_rs2(bc)}, {get_imm(bc)}"

def get_args_S(bc):
    '''
    Get the arguments of an S-type instruction.
    We return the following format: rs2, imm(rs1)
    '''
    def get_imm(bc):
        '''
        Get the value of the immediate as per the S type format.
        '''
        return str(int(bc[0:7] + bc[-12:-7], 2))
    
    return f"{get_rs2(bc)}, {get_imm(bc)}({get_rs1(bc)})"

def get_args_IL(bc):
    '''
    Get the arguments of an I-Load type instruction.
    We return the following format: rd, imm(rs1)
    '''
    def get_imm(bc):
        '''
        Get the value of the immediate as per the I type format.
        '''
        return str(int(bc[:12],2))
    
    return f"{get_rd(bc)}, {get_imm(bc)}({get_rs1(bc)})"

def get_args_I(bc):
    '''
    Get the arguments of an I type instruction.
    We return the following format: rd, rs1, imm
    '''
    def get_imm(bc):
        '''
        Get the value of the immediate as per the I type format.
        '''
        return str(int(bc[:12],2))
    
    return f"{get_rd(bc)}, {get_rs1(bc)}, {get_imm(bc)}"

def get_args_R(bc):
    '''
    Get the arguments of an R type instruction.
    We return the following format: rd, rs1, rs2
    '''  
    return f"{get_rd(bc)}, {get_rs1(bc)}, {get_rs2(bc)}"

def get_rd(bc):
    '''
    Return the rd register value in the byte code.
    '''
    c = bc[-12:-7]
    assert c in reg_name
    return reg_name[c]

def get_rs1(bc):
    '''
    Return the rs1 register value in the byte code.
    '''
    c = bc[-20:-15]
    assert c in reg_name
    return reg_name[c]

def get_rs2(bc):
    '''
    Return the rs2 register value in the byte code.
    '''
    c = bc[-25:-20]
    assert c in reg_name
    return reg_name[c]


def analyse(bytecode):
    '''
    Returns a text version of given bytecode instruction
    '''
    opcode = get_opcode(bytecode)
    func3 = get_func3(bytecode)
    func7 = get_func7(bytecode)

    inst_type = get_inst_type(opcode)
    inst = get_inst(opcode, func3, func7)
    return inst + " " + get_args(bytecode, inst_type)

################# Utils ###################

def hex_to_bin(hex_str):
    '''
    Hex to binary string converter.
    '''
    return bin(int(hex_str, 16))[2:]

def pad_zeros(input):
    '''
    Takes in a binary string and pads with zeros until string length is 32 bits.
    '''
    while len(input) != 32:
        input = "0" + input
    return input


############## Runner ###############

if __name__ == "__main__":
    bin = pad_zeros(hex_to_bin("003E8037"))
    result = analyse(bin)
    print(result)