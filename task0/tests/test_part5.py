import copy

from xvm.vm import VM, parse_string

class MyIO:
    def __init__(self, in_buffer):
        self.in_buffer = copy.deepcopy(in_buffer)
        self.out_buffer = []
    
    def print_fn(self, obj):
        print(obj)
        self.out_buffer.append(obj)

    def input_fn(self, obj):
        a = self.in_buffer.pop(0)
        return a


# a = input()
# b = input()
# if a == b:
#   sign = "=="
# else:
#   sign = "!="
# print(a)
# print(sign)
# print(b)
TEST1 = """\
INPUT_NUMBER
STORE_VAR "a"
INPUT_NUMBER
STORE_VAR "b"

LOAD_VAR "a"
LOAD_VAR "b"
NEQ
CJMP else_body

LABEL if_body
LOAD_CONST "=="
STORE_VAR "sign"
JMP after_else

LABEL else_body
LOAD_CONST "!="
STORE_VAR "sign"
LABEL after_else

LOAD_VAR "a"
PRINT
LOAD_VAR "sign"
PRINT
LOAD_VAR "b"
PRINT
"""

def test1():
    code_entry = parse_string(TEST1)
    code = {
        "$entrypoint$": code_entry
    }
    # 3 != 3
    inp = [3, 5]
    io = MyIO(inp)
    vm = VM(input_fn=io.input_fn, print_fn=io.print_fn)
    stack, variables = vm.run_code(code)
    assert " ".join(map(str, io.out_buffer)) == "3 != 5", io.out_buffer
    assert len(stack) == 0

    # 3 == 3
    inp = [3, 3]
    io = MyIO(inp)
    vm = VM(input_fn=io.input_fn, print_fn=io.print_fn)
    stack, variables = vm.run_code(code)
    assert " ".join(map(str, io.out_buffer)) == "3 == 3", io.out_buffer
    assert len(stack) == 0


# N = input()
# s = 0
# for (i=1; i<=N, i+=1):
#   s += i
# print(s)
TEST2 = """\
INPUT_NUMBER
STORE_VAR "N"
LOAD_CONST 0
STORE_VAR "s"
LOAD_CONST 1
STORE_VAR "i"

LABEL for_condition
LOAD_VAR "N"
LOAD_VAR "i"
GT
CJMP after_for

LABEL for_loop_body
LOAD_VAR "s"
LOAD_VAR "i"
ADD
STORE_VAR "s"

LABEL count_inc
LOAD_VAR "i"
LOAD_CONST 1
ADD
STORE_VAR "i"
JMP for_condition

LABEL after_for
LOAD_VAR "s"
PRINT
"""

def test2():
    code_entry = parse_string(TEST2)
    code = {
        "$entrypoint$": code_entry
    }
    # sum(1..100)
    inp = [100]
    io = MyIO(inp)
    vm = VM(input_fn=io.input_fn, print_fn=io.print_fn)
    stack, variables = vm.run_code(code)
    assert io.out_buffer[0] == sum(range(1, 101))
    assert len(stack) == 0

    # sum(1..0)
    inp = [0]
    io = MyIO(inp)
    vm = VM(input_fn=io.input_fn, print_fn=io.print_fn)
    stack, variables = vm.run_code(code)
    assert io.out_buffer[0] == 0
    assert len(stack) == 0