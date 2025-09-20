import enum
from typing import Any
import json


class OpCode(enum.Enum):
    LOAD_CONST=1
    STORE_VAR=2
    LOAD_VAR=3
    ADD=4
    SUB=5


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


class VM:
    def __init__(self):
        self.stack = []
        self.variables = dict()

    def run_op(self, op: Op):
        print(op)
        if op.opcode == OpCode.LOAD_CONST:
            assert len(op.args) == 1, f"LOAD_CONST takes one argument. Got: {op.args}"
            val = op.args[0]
            self.stack.append(val)
        elif op.opcode == OpCode.ADD:
            assert len(op.args) == 0, f"ADD takes no arguments. Got: {op.args}"
            arg1 = self.stack.pop()
            arg2 = self.stack.pop()
            self.stack.append(arg1 + arg2)
        elif op.opcode == OpCode.SUB:
            assert len(op.args) == 0, f"SUB takes no arguments. Got: {op.args}"
            arg1 = self.stack.pop()
            arg2 = self.stack.pop()
            self.stack.append(arg1 - arg2)
        elif op.opcode == OpCode.STORE_VAR:
            assert len(op.args) == 1, f"STORE_VAR takes one arguments. Got: {op.args}"
            var_name = op.args[0]
            value = self.stack.pop()
            self.variables[var_name] = value
        elif op.opcode == OpCode.LOAD_VAR:
            assert len(op.args) == 1, f"LOAD_VAR takes one arguments. Got: {op.args}"
            var_name = op.args[0]
            assert var_name in self.variables, f"Variable {var_name!r} not defined."
            value = self.variables[var_name]
            self.stack.append(value)
        else:
            raise NotImplementedError(f"Unknown op: {str(op)}")

    def run_code(self, code: list[Op]):
        for op in code:
            self.run_op(op)
        return self.stack, self.variables
    
    def dump_state(self):
        with open("stack_and_vars.json", "w") as f:
            json.dump({"stack": stack, "variables": variables}, f)

    def load_state(self):
        with open("stack_and_vars.json", "r") as f:
            stack_and_vars = json.load(f)
        self.stack = stack_and_vars["stack"]
        self.variables = stack_and_vars["variables"]

def serialize_code(code: list[Op]) -> str:
    return "\n".join(op.text() for op in code)

def deserialize_code(code: str) -> list[Op]:
    ops = []
    for line in code.splitlines():
        args = line.split(" ")
        opcode = args[0]
        out_args = []
        for arg in args[1:]:
            if arg.isdigit():
                out_args.append(int(arg))
            else:
                out_args.append(arg)

        ops.append(Op(OpCode[opcode], *out_args))
    return ops

if __name__ == "__main__":
    vm = VM()
    code = [
        # a = 10
        # b = 20
        # c = b - a
        # --------
        # a = 10
        Op(OpCode.LOAD_CONST, 10),
        Op(OpCode.STORE_VAR, "a"),
        # b = 20
        Op(OpCode.LOAD_CONST, 20),
        Op(OpCode.STORE_VAR, "b"),
        # c = b - a
        Op(OpCode.LOAD_VAR, "a"),
        Op(OpCode.LOAD_VAR, "b"),
        Op(OpCode.SUB),
        Op(OpCode.STORE_VAR, "c"),
    ]
    s = serialize_code(code)
    code = deserialize_code(s)
    stack, variables = vm.run_code(code)
    print(stack, variables)