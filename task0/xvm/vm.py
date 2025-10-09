import enum
import math
import json
import pickle

#try converting to int/float, return string otherwise
def convert_to_number(str_element):
    try:
        return int(str_element)
    except ValueError:
        try: 
            return float(str_element)
        except ValueError:
            return str_element

#parser
def parse_string(text):
    # parse opcodes from text
    # CODE <ARG>  -> (OP_CODE, (ARG,))
    # \n -> skip
    code = {}
    instructions = []
    labels = {}
    label_i = 0

    #split into lines
    lines = text.split('\n')
    lines = [line for line in lines if line.strip() != '']

    #now parse each line
    for line in lines:

        #get line elements
        elements = []
        element = ''
        q_fl = False #check for quotes (for string identification)

        for char in line:
            #if char in ("'", '"'):
            if char == '"':
                q_fl = not q_fl
                continue
            if char == ' ' and (not q_fl):
                if element:
                    elements.append(convert_to_number(element))
                    element = ''
            else:
                element += char
        if element:
            elements.append(convert_to_number(element))
    
        #check if first element is an opcode (and valid one)
        assert elements[0] in OpCode.__members__, f"Invalid OpCode input: {elements[0]}"
        #record opcode and save everything else as arguments
        assert len(elements) <=3, f"Too many arguments (max: 2). Got: {len(elements)-1}"

        #check for labels, remember their instuction position
        if elements[0] == OpCode.LABEL.name:
            assert len(elements) == 2, f"LABEL must have one argument. Got: {len(elements)-1}"
            assert isinstance(elements[1], str), f"LABEL takes str as input. Got: {type(elements[1]).__name__}"
            labels[elements[1]] = label_i
            #omit "LABEL <name>" in parsed code. Index = the position of instruction to be executed next
            #label_i += 1
            continue
        
        #replace <label_name> for instruction index


        #check if instr has no args
        if len(elements[1:]) != 0:
            instructions.append(Op(OpCode[elements[0]], *elements[1:]))
        else:
            instructions.append(Op(OpCode[elements[0]]))

        label_i += 1

    #return code: instr, labels
    code = {
            'instructions': instructions, 
            'labels': labels
            }
    
    #print(code)
    return code
    #return instructions, labels

#raw opcodes representation
class OpCode(enum.Enum):
    #memory
    LOAD_CONST=1
    #STORE_CONST=2
    LOAD_VAR=2
    STORE_VAR=3
    #binary
    ADD=4
    SUB=5
    MUL=6
    DIV=7
    #unary
    SQRT=8
    NEG=9
    EXP=10
    #comp
    EQ=11
    NEQ=12
    GT=13
    LT=14
    GE=15 
    LE=16 
    #labels and jumps
    LABEL=17
    JMP=18
    CJMP=19
    #i/o
    PRINT=20
    INPUT_STRING=21
    INPUT_NUMBER=22
    #functions
    CALL=23
    RET=24
    #breakpoint
    BREAKPOINT=25

#operations: opcode + arguments
class Op:
    def __init__(self, opcode: OpCode, *args):
        self.opcode = opcode
        self.args = args
    
    def __str__(self):
        args_str = ", ".join(repr(a) for a in self.args)
        return f"Op({str(self.opcode)}, {args_str})"

    def __repr__(self):
        return self.__str__()

    def text(self):
        args_str = " ".join(str(a) for a in self.args)
        if args_str:
            return f"{str(self.opcode.name)} {args_str}"
        else:
            return f"{str(self.opcode.name)}"

#the virtual machine
class VM():
    def __init__(self, input_fn=input, print_fn=print):
        #stack - list
        self.stack = []
        #variables - dict
        self.variables = dict()
        #frames - list 
        self.frames = []

        #i/o
        self.input_fn = input_fn 
        self.print_fn = print_fn

        #'instruction pointer' and
        #list of saved pointers (like ebp, esp handling) + func names
        #e.g. [{'main': 5}, {'foo': 1}, ...]
        self.ip = 0
        self.saved_ips = []

        #current function indicator
        self.current_frame = '$entrypoint$'

    #operations + parsing
    def run_op(self, op: Op, labels):
        #print(op)
        #print(self.stack, self.frames, self.variables, self.saved_ips)
        match op.opcode:
            #memory
            case OpCode.LOAD_CONST:
                assert len(op.args) == 1, f"LOAD_CONST takes one argument. Got: {op.args}"
                val = op.args[0]
                self.stack.append(val)
            case OpCode.LOAD_VAR:
                assert len(op.args) == 1, f"LOAD_VAR takes one arguments. Got: {op.args}"
                var_name = op.args[0]
                assert var_name in self.variables, f"Variable {var_name!r} not defined."
                value = self.variables[var_name]
                self.stack.append(value)
            case OpCode.STORE_VAR:
                assert len(op.args) == 1, f"STORE_VAR takes one arguments. Got: {op.args}"
                var_name = op.args[0]
                value = self.stack.pop()
                self.variables[var_name] = value

            #binary
            case OpCode.ADD:
                assert len(op.args) == 0, f"ADD takes no arguments. Got: {op.args}"
                arg1 = self.stack.pop()
                arg2 = self.stack.pop()
                assert type(arg1) == type(arg2) and isinstance(arg1, (int, float)),  f"Operands must be same type and either int or float. Got: {type(arg1).__name__} and {type(arg2).__name__}"
                self.stack.append(arg1 + arg2)
            case OpCode.SUB:
                assert len(op.args) == 0, f"SUB takes no arguments. Got: {op.args}"
                arg1 = self.stack.pop()
                arg2 = self.stack.pop()
                assert type(arg1) == type(arg2) and isinstance(arg1, (int, float)),  f"Operands must be same type and either int or float. Got: {type(arg1).__name__} and {type(arg2).__name__}"
                self.stack.append(arg1 - arg2)
            case OpCode.MUL:
                assert len(op.args) == 0, f"MUL takes no arguments. Got: {op.args}"
                arg1 = self.stack.pop()
                arg2 = self.stack.pop()
                assert type(arg1) == type(arg2) and isinstance(arg1, (int, float)),  f"Operands must be same type and either int or float. Got: {type(arg1).__name__} and {type(arg2).__name__}"
                self.stack.append(arg1 * arg2)
            case OpCode.DIV:
                assert len(op.args) == 0, f"DIV takes no arguments. Got: {op.args}"
                arg1 = self.stack.pop()
                arg2 = self.stack.pop()
                assert type(arg1) == type(arg2) and isinstance(arg1, (int, float)),  f"Operands must be same type and either int or float. Got: {type(arg1).__name__} and {type(arg2).__name__}"
                if isinstance(arg1, int):
                    self.stack.append(arg1 // arg2)
                else:
                    self.stack.append(arg1 / arg2)

            #unary
            case OpCode.SQRT:
                assert len(op.args) == 0, f"SQRT takes no arguments. Got: {op.args}"
                arg = self.stack.pop()
                assert isinstance(arg, (int, float)),  f"Operand must be either int or float. Got: {type(arg).__name__}"
                self.stack.append(math.sqrt(arg))
            case OpCode.NEG:
                assert len(op.args) == 0, f"NEG takes no arguments. Got: {op.args}"
                arg = self.stack.pop()
                assert isinstance(arg, (int, float)),  f"Operand must be either int or float. Got: {type(arg).__name__}"
                self.stack.append(-arg)
            case OpCode.EXP:
                assert len(op.args) == 0, f"EXP takes no arguments. Got: {op.args}"
                arg = self.stack.pop()
                assert isinstance(arg, (int, float)),  f"Operand must be either int or float. Got: {type(arg).__name__}"
                self.stack.append(math.exp(arg))
            
            #i/o
            case OpCode.PRINT:
                assert len(op.args) == 0, f"PRINT takes no arguments. Got: {op.args}"
                arg = self.stack.pop()
                self.print_fn(arg)
            case OpCode.INPUT_STRING:
                assert len(op.args) == 0, f"INPUT_STRING takes no arguments. Got: {op.args}"
                arg = self.input_fn()
                assert isinstance(arg, str),  f"Operand must be str. Got: {type(arg).__name__}"
                self.stack.append(arg)
            case OpCode.INPUT_NUMBER:
                assert len(op.args) == 0, f"INPUT_NUMBER takes no arguments. Got: {op.args}"
                arg = self.input_fn()
                assert isinstance(arg, (int, float)),  f"Operand must be float/int. Got: {type(arg).__name__}"
                self.stack.append(arg)

            #comp
            case OpCode.EQ:
                assert len(op.args) == 0, f"EQ takes no arguments. Got: {op.args}"
                arg1 = self.stack.pop()
                arg2 = self.stack.pop()
                assert type(arg1) == type(arg2) and isinstance(arg1, (int, float)),  f"Operands must be same type and either int or float. Got: {type(arg1).__name__} and {type(arg2).__name__}"
                if arg1 == arg2:
                    self.stack.append(1)
                else:
                    self.stack.append(0)
            case OpCode.NEQ:
                assert len(op.args) == 0, f"NEQ takes no arguments. Got: {op.args}"
                arg1 = self.stack.pop()
                arg2 = self.stack.pop()
                assert type(arg1) == type(arg2) and isinstance(arg1, (int, float)),  f"Operands must be same type and either int or float. Got: {type(arg1).__name__} and {type(arg2).__name__}"
                if arg1 != arg2:
                    self.stack.append(1)
                else:
                    self.stack.append(0)
            case OpCode.GT:
                assert len(op.args) == 0, f"GT takes no arguments. Got: {op.args}"
                arg1 = self.stack.pop()
                arg2 = self.stack.pop()
                assert type(arg1) == type(arg2) and isinstance(arg1, (int, float)),  f"Operands must be same type and either int or float. Got: {type(arg1).__name__} and {type(arg2).__name__}"
                if arg1 > arg2:
                    self.stack.append(1)
                else:
                    self.stack.append(0)
            case OpCode.LT:
                assert len(op.args) == 0, f"LT takes no arguments. Got: {op.args}"
                arg1 = self.stack.pop()
                arg2 = self.stack.pop()
                assert type(arg1) == type(arg2) and isinstance(arg1, (int, float)),  f"Operands must be same type and either int or float. Got: {type(arg1).__name__} and {type(arg2).__name__}"
                if arg1 < arg2:
                    self.stack.append(1)
                else:
                    self.stack.append(0)
            case OpCode.GE:
                assert len(op.args) == 0, f"GE takes no arguments. Got: {op.args}"
                arg1 = self.stack.pop()
                arg2 = self.stack.pop()
                assert type(arg1) == type(arg2) and isinstance(arg1, (int, float)),  f"Operands must be same type and either int or float. Got: {type(arg1).__name__} and {type(arg2).__name__}"
                if arg1 >= arg2:
                    self.stack.append(1)
                else:
                    self.stack.append(0)
            case OpCode.LE:
                assert len(op.args) == 0, f"LE takes no arguments. Got: {op.args}"
                arg1 = self.stack.pop()
                arg2 = self.stack.pop()
                assert type(arg1) == type(arg2) and isinstance(arg1, (int, float)),  f"Operands must be same type and either int or float. Got: {type(arg1).__name__} and {type(arg2).__name__}"
                if arg1 <= arg2:
                    self.stack.append(1)
                else:
                    self.stack.append(0)

            #labels, jumps
            case OpCode.CJMP:
                assert len(op.args) == 1, f"CJMP takes one argument. Got: {op.args}"
                val = op.args[0]
                assert isinstance(val, str), f"CJMP takes str as input. Got: {type(val).__name__}"
                fl = self.stack.pop()
                if fl == 1:
                    self.ip = labels[val] - 1
                else:
                    pass
            case OpCode.JMP:
                assert len(op.args) == 1, f"JMP takes one argument. Got: {op.args}"
                val = op.args[0]
                assert isinstance(val, str), f"JMP takes str as input. Got: {type(val).__name__}"
                self.ip = labels[val] - 1

            #function handling
            case OpCode.CALL:
                assert len(op.args) == 0, f"CALL takes no arguments. Got: {op.args}"
                
                #first, pop current func name
                func = self.stack.pop()

                #next, save frame pointer and previous func name
                self.saved_ips.append([self.current_frame, self.ip])
                self.current_frame = func

                #separate variable frames 
                self.frames.append(self.variables) #save old frame
                self.variables = dict() #create new frame

                #finally, reset instruction pointer
                self.ip = -1

            case OpCode.RET:
                assert len(op.args) == 0, f"RET takes no arguments. Got: {op.args}"

                #restore old instruction pointer and function indicator
                #just go one element back and clear saved info
                saved_info = self.saved_ips.pop()
                self.current_frame = saved_info[0]
                self.ip = saved_info[1]
                del saved_info

                #return to frame, clear info
                self.variables = self.frames.pop()

            #breakpoint (dummy op)
            case OpCode.BREAKPOINT:
                assert len(op.args) == 0, f"BREAKPOINT takes no arguments. Got: {op.args}"
                raise StopIteration("Breakpoint hit")

            case _:
                raise NotImplementedError(f"Unknown op: {str(op)}")

    def run_code(self, code):

        elements = list(code.values())
        #if elements are inst list + labels dict -> no functions
        if isinstance(elements[0], list) and isinstance(elements[1], dict):
            #add starting frame
            code = {self.current_frame: code}

        del elements
       
        while self.ip < len(code[self.current_frame]['instructions']): 
            #self.run_op(code[self.ip])
            self.run_op(code[self.current_frame]['instructions'][self.ip], code[self.current_frame]['labels'])
            self.ip += 1
        return self.stack, self.variables
    
    def run_code_from_json(self, json_path: str):
        #open file
        with open(json_path, 'r') as j:
            code = json.loads(j.read())["$entrypoint$"]

        #"parse" it to get our target format (because we use labels)
        #!!! maybe realise this parsing later

        #print(code, len(code))
        while self.ip < len(code):
            opc = code[self.ip]["op"]
            args = code[self.ip].get("arg")   
            assert opc in OpCode.__members__, f"Invalid OpCode input: {opc}"
            if args == None:
                self.run_op(Op(OpCode[opc]), [])
            else:
                self.run_op(Op(OpCode[opc], args), [])
            self.ip += 1
    
    #stack
    def dump_stack(self, pkl_path: str):
        with open(pkl_path, "wb") as file:
            pickle.dump(self.stack, file)
        print(f"Stack serialised to {pkl_path}")

    def load_stack(self, pkl_path: str):
        with open(pkl_path, "rb") as file:
            self.stack = pickle.load(file)
        print(f"Stack deserialised from {pkl_path}")

    #memory
    def dump_memory(self, pkl_path: str):
        with open(pkl_path, "wb") as file:
            pickle.dump(self.variables, file)
        print(f"Memory serialised to {pkl_path}")

    def load_memory(self, pkl_path: str):
        with open(pkl_path, "rb") as file:
            self.variables = pickle.load(file)
        print(f"Memory deserialised from {pkl_path}")