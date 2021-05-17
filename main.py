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
    "00000": "zerp",
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
    "01111": "a5"
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
    

def get_args_R(bc):
    '''
    Get the arguments of an R type instruction
    We return the following format: rd rs1 rs2
    '''
    def get_rd(bc):
        c = bc[-12:-7]
        assert c in reg_name
        return reg_name[c]
    
    def get_rs1(bc):
        c = bc[-20:-15]
        assert c in reg_name
        return reg_name[c]
    
    def get_rs2(bc):
        c = bc[-25:-20]
        assert c in reg_name
        return reg_name[c]
    
    return ", ".join([get_rd(bc), get_rs1(bc), get_rs2(bc)])

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
    bin = pad_zeros(hex_to_bin("40728433"))
    result = analyse(bin)
    print(result)