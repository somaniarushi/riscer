import sys

################### Data storage ##################

## Defining A Dictionary for Conversion ##
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
        "1110011": "CSR",   # CSR Operations
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
        "1110011": {
                "000": "csrrw",
                "001": "csrrs",
                "010": "csrrc",
                "011": "csrrwi",
                "101": "csrrsi",
                "110": "csrrci",
            },   # CSR Operations
    }

reg_name = {
    "00000": "x0",
    "00001": "x1",
    "00010": "x2",
    "00011": "x3",
    "00100": "x4",
    "00101": "x5",
    "00110": "x6",
    "00111": "x7",
    "01000": "x8",
    "01001": "x9",
    "01010": "x10",
    "01011": "x11",
    "01100": "x12",
    "01101": "x13",
    "01110": "x14",
    "01111": "x15",
    "10000": "x16",
    "10001": "x17",
    "10010": "x18",
    "10011": "x19",
    "10100": "x20",
    "10101": "x21",
    "10110": "x22",
    "10111": "x23",
    "11000": "x24",
    "11001": "x25",
    "11010": "x26",
    "11011": "x27",
    "11100": "x28",
    "11101": "x29",
    "11110": "x30",
    "11111": "x31"
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
            print(opcode, func3, func7)
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
    if type == "UJ":
        return get_args_UJ(bytecode)
    if type == "CSR":
        return get_args_CSR(bytecode)


def get_args_UJ(bc):
    '''
    Get the arguments of a UJ-type instruction.
    We return the following format: rd, imm
    '''
    def get_imm(bc):
        '''
        Get the value of the immediate as per the UJ-type format.
        '''
        return str((int(bc[0] + bc[13:21] + bc[12] + bc[1:12], 2)))
    return f"{get_rd(bc)}, {get_imm(bc)}"

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
        return str((int(bc[0] + bc[24] + bc[1:7] + bc[20:24], 2)))
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

def get_args_CSR(bc):
    '''
    Get the arguments of a CSR type instruction.
    We return the following format: rd, csr, imm
    '''
    def get_csr(bc):
        '''
        Get the value of the csr as per the CSR type format.
        '''
        return str(int(bc[12:20],2))
    return f"{get_rd(bc)}, {get_csr(bc)}, {get_rs1(bc)}"

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
    assert len(sys.argv) == 3, "Please provide input with its type"
    type, code = sys.argv[1], sys.argv[2]
    if type == "bin":
        if code[:2] == "0b":
            code = code[2:]
        bin = pad_zeros(code)
        print("Instruction:\n", analyse(bin))
    else:
        if code[:2] == "0x":
            code = code[2:]
        bin = pad_zeros(hex_to_bin(code))
        print("Instruction:\n", analyse(bin))