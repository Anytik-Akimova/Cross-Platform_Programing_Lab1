# =========================== python ==============================

#we implemented recursive exponentianion
def pow_rec(x, n):
    '''
    check power type (only in VM)
    n // 2
    since 2 is an int, if n is a float then
    // op will throw an error
    '''

    #check if the power is even
    d = n//2
    if d*2 != n: #not even
        if n == 1: #stopping condition
            return x
        else:
            xn = pow_rec(x, d) #even power in recursion
            xn = xn*xn
            xn = xn*x #multiply one last time to get odd power
    else:
        xn = pow_rec(x, d)
        xn = xn*xn

    #print(x, n, xn)
    return xn

# ================================================================

def from_stdin():
    inputs = input().split()
    numbers = []

    for s in inputs:
        try:
            numbers.append(int(s))
        except ValueError:
            numbers.append(float(s))

    return numbers[0], numbers[1]

#xn = pow_rec(x, n)
#print(xn)

# =========================== Bytecode ==============================
import copy 

from vm import VM, parse_string

#cant forget IO
class MyIO:
    def __init__(self, in_buffer):
        self.in_buffer = copy.deepcopy(in_buffer)
        self.out_buffer = []
    
    def print_fn(self, obj):
        print(obj)
        self.out_buffer.append(obj)

    def input_fn(self):
        a = self.in_buffer.pop(0)
        return a


#note: since 2 is an int, if n is a float
#div will automatically throw an error
#div also acts as a type checker here  

#0 does get checked
POW = """\
STORE_VAR "x"
STORE_VAR "n"

LOAD_CONST 0
LOAD_VAR "n"
EQ
CJMP "Power 0"

LOAD_CONST 2
LOAD_VAR "n"
DIV

STORE_VAR "d"
LOAD_VAR "d"

LOAD_CONST 2
MUL

LOAD_VAR "n"
EQ 

CJMP "Even"

LOAD_CONST 1
LOAD_VAR "n"
EQ

CJMP "Stop"

LOAD_VAR "d"
LOAD_VAR "x"
LOAD_CONST "pow"
CALL
STORE_VAR "xn"

LOAD_VAR "xn"
LOAD_VAR "xn"
MUL

LOAD_VAR "x"
MUL
RET

LABEL "Stop"
LOAD_VAR "x"
RET

LABEL "Even"

LOAD_VAR "d"
LOAD_VAR "x"
LOAD_CONST "pow"
CALL
STORE_VAR "xn"

LOAD_VAR "xn"
LOAD_VAR "xn"
MUL
RET

LABEL "Power 0"
LOAD_CONST "This func can't take power of 0."
RET
"""

ENTRY = """\
INPUT_NUMBER
STORE_VAR "x"
INPUT_NUMBER
STORE_VAR "n"

LOAD_VAR "n"
LOAD_VAR "x"
LOAD_CONST "pow"
CALL

STORE_VAR "xn"
LOAD_VAR "xn"
PRINT
"""


# ================================================================

code_pow = parse_string(POW)
code_entry = parse_string(ENTRY)
code = {
    "pow": code_pow,
    "$entrypoint$": code_entry,
}
x, n = from_stdin()
inp = [x, n]
io = MyIO(inp)
vm = VM(input_fn=io.input_fn, print_fn=io.print_fn)
stack, variables = vm.run_code(code)
'''
assert io.out_buffer[0] == (3 + 5)*(5 - 3)
assert variables["a"] == 3
assert variables["b"] == 5
assert "d" not in variables
assert len(stack) == 0
'''
print(stack, variables)