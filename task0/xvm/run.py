import copy
import sys
import traceback
from pathlib import Path
from vm import VM, parse_string, OpCode, Op, convert_to_number

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
    
def from_stdin_number():
    inputs = input().split()
    numbers = []

    for s in inputs:
        try:
            numbers.append(int(s))
        except ValueError:
            try:
                numbers.append(float(s))
            except Exception: 
                #print("Input must be a number!")
                raise ValueError("Incorrect debugger input")

    return numbers

#parser helper
def parse_text(text):

    functions = {}
    pos = 0

    while True:
        #find start of func definition
        start_func = text.find('function "', pos)
        if start_func == -1:
            break

        #find start and end of func name
        start_quote = start_func + len('function "')
        end_quote = text.find('"', start_quote)
        func_name = text[start_quote:end_quote]

        #find start of next func
        next_func = text.find('function "', end_quote)
        if next_func == -1:
            func_code = text[end_quote+1:].strip()
        else:
            func_code = text[end_quote+1:next_func].strip()

        functions[func_name] = func_code
        pos = next_func

    return functions

#debugger
def xvm_debug():
    fl = 0 #flag for VM errors 
    vm = VM()
    code = dict()   

    print("XVM Debugger. Type 'info' or 'exit'.")

    while True:
        try:
            line = input("xvm > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nDebug was stopped")
            return

        if not line:
            continue

        command, *args = line.split(maxsplit=1)
        arg = args[0] if args else ""
        cmd = command.lower()

        #exit or quit
        if cmd in ("exit", "quit"):
            print("\nDebug was stopped")
            return

        #info or help
        elif cmd in ("info", "help"):
            print("Commands:")
            print("  1) Operations: ")
            print("    load path   - load program from file (input 'load <path>')")
            print("    run         - run program to the end (input 'run')")
            print("    step        - run 1 instruction (input 'step')")
            print("    next        - run one next line from loaded code, if the next function is a function call (input 'next')")
            print("    exec        - do instruction OpCode (input 'exec <OpCode> <arg1, arg2, ..., argN>')")
            print("  2) Information: ")
            print("    list        - show up to 5 instructions before and after current instruction (input 'list')")
            print("    stack[N]    - show top N items (input 'stack N') or whole stack (input 'stack')")
            print("    memory      - dump all VM variables (input 'memory')")
            print("    print sth   - show variable value (input 'print <name>')")  
            print("    frame       - dump all variables in current frame (input 'frame')")
            print("  Exit")
            continue

        #load
        elif cmd == "load":
            #if new file was loaded, error flag is refreshed
            fl = 0

            if not arg:
                print("Usage: load <path>")
                continue
            
            path = Path(arg.strip().strip("'\""))

            if not path.exists() or not path.is_file():
                print("File not found")
                continue

            try:
                text = path.read_text(encoding="utf-8")
            except Exception as e:
                print(f"Failed to read file: {e}")
                continue

            try:
                parsed_text = parse_text(text)
            except Exception as e:
                print(f"Failed to parse: {e}")
                continue
            print("File loaded succesfully")

            code = dict()
            for func in parsed_text:
                func_code = parse_string(parsed_text[func])
                code[func] = func_code

            #reset VM state
            vm.stack.clear()
            vm.variables.clear()

            vm.ip = 0                     
            vm.current_frame = '$entrypoint$'
            vm.frames.clear()
            vm.saved_ips.clear()

        #run
        elif cmd == "run":
            if fl == 1:
                print("XVM has crashed, instruction execution is forbidden. Please reload your program file.")
                continue

            if not code:
                print("No program loaded. Use: load <path>")
                continue
            if vm.ip >= len(code[vm.current_frame]['instructions']):
                print("IP at end; nothing to execute.")
                continue

            try:
                while vm.ip < len(code[vm.current_frame]['instructions']): 
            
                    #vm.run_code(code)
                    op = code[vm.current_frame]['instructions'][vm.ip]

                    #handle input ops 
                    if op.opcode == OpCode.INPUT_NUMBER:
                        print("Input for INPUT_NUMBER (one arg): ")
                        try:
                            inp = from_stdin_number()
                        except ValueError:
                            print("Input must be a number!")
                            continue
                        io = MyIO(inp)
                        vm.input_fn = io.input_fn
                        vm.print_fn = io.print_fn
                    elif op.opcode == OpCode.INPUT_STRING:
                        print("Input for INPUT_STRING (one arg): ")
                        inp = input()
                        io = MyIO(inp)
                        vm.input_fn = io.input_fn
                        vm.print_fn = io.print_fn

                    vm.run_op(op, code[vm.current_frame]['labels'])
                    vm.ip += 1
            except StopIteration:
                print(f"Stopped at instruction {vm.ip} (BREAKPOINT)")
                vm.ip += 1 
            except Exception:
                #check if the error came from VM
                e_type, e_value, e_traceback = sys.exc_info()
                e_stack = traceback.extract_tb(e_traceback)
                e_frame = e_stack[-1]
        
                if 'vm.py' in e_frame.filename:
                    print(f"Runtime error at instruction {vm.ip}: {repr(op)}")
                    print(f"Error: {e_value}")
                    fl = 1
                else:
                    print(f"Debugger error: {e_value}")

            if vm.ip >= len(code[vm.current_frame]['instructions']):
                print("End of program reached.")
            continue
        
        #step        
        elif cmd == "step":
            if fl == 1:
                print("XVM has crashed, instruction execution is forbidden. Please reload your program file.")
                continue

            if not code:
                print("No program loaded. Use: load <path>")
                continue
            if vm.ip >= len(code[vm.current_frame]['instructions']):
                print("IP at end; nothing to execute.")
                continue

            op = code[vm.current_frame]['instructions'][vm.ip]
            
            if op.opcode == OpCode.BREAKPOINT:
                print(f"{vm.ip:04d}: {repr(op)}  # BREAKPOINT consumed")
                #update ip and op
                vm.ip += 1

            else:
                print(f"{vm.ip:04d}: {repr(op)}")

                #handle input ops 
                if op.opcode == OpCode.INPUT_NUMBER:
                    print("Input for INPUT_NUMBER (one arg): ")
                    try:
                        inp = from_stdin_number()
                    except ValueError:
                        print("Input must be a number!")
                        continue
                    io = MyIO(inp)
                    vm.input_fn = io.input_fn
                    vm.print_fn = io.print_fn
                elif op.opcode == OpCode.INPUT_STRING:
                    print("Input for INPUT_STRING (one arg): ")
                    inp = input()
                    io = MyIO(inp)
                    vm.input_fn = io.input_fn
                    vm.print_fn = io.print_fn

                #try executing
                try:
                    vm.run_op(op, code[vm.current_frame]['labels'])
                #dont change ip if exception
                except Exception:
                    #check if the error came from VM
                    e_type, e_value, e_traceback = sys.exc_info()
                    e_stack = traceback.extract_tb(e_traceback)
                    e_frame = e_stack[-1]
        
                    if 'vm.py' in e_frame.filename:
                        print(f"Runtime error at instruction {vm.ip}: {repr(op)}")
                        print(f"Error: {e_value}")
                        fl = 1
                    else:
                        print(f"Debugger error: {e_value}")
                else:
                    vm.ip += 1

            if vm.ip >= len(code[vm.current_frame]['instructions']):
                print("End of program reached.")        
            continue

        #next
        elif cmd == "next":
            if fl == 1:
                print("XVM has crashed, instruction execution is forbidden. Please reload your program file.")
                continue

            if not code:
                print("No program loaded. Use: load <path>")
                continue
            if vm.ip >= len(code[vm.current_frame]['instructions']):
                print("IP at end; nothing to execute.")
                continue

            op = code[vm.current_frame]['instructions'][vm.ip]

            #if not call, just execute step
            if op.opcode != OpCode.CALL:           
                if op.opcode == OpCode.BREAKPOINT:
                    print(f"{vm.ip:04d}: {repr(op)}  # BREAKPOINT consumed")
                    #update ip and op
                    vm.ip += 1

                else:
                    print(f"{vm.ip:04d}: {repr(op)}")

                    #handle input ops 
                    if op.opcode == OpCode.INPUT_NUMBER:
                        print("Input for INPUT_NUMBER (one arg): ")
                        try:
                            inp = from_stdin_number()
                        except ValueError:
                            print("Input must be a number!")
                            continue
                        io = MyIO(inp)
                        vm.input_fn = io.input_fn
                        vm.print_fn = io.print_fn
                    elif op.opcode == OpCode.INPUT_STRING:
                        print("Input for INPUT_STRING (one arg): ")
                        inp = input()
                        io = MyIO(inp)
                        vm.input_fn = io.input_fn
                        vm.print_fn = io.print_fn

                    #try executing
                    try:
                        vm.run_op(op, code[vm.current_frame]['labels'])
                    #dont change ip if exception
                    except Exception:
                        #check if the error came from VM
                        e_type, e_value, e_traceback = sys.exc_info()
                        e_stack = traceback.extract_tb(e_traceback)
                        e_frame = e_stack[-1]
        
                        if 'vm.py' in e_frame.filename:
                            print(f"Runtime error at instruction {vm.ip}: {repr(op)}")
                            print(f"Error: {e_value}")
                            fl = 1
                        else:
                            print(f"Debugger error: {e_value}")
                    else:
                        vm.ip += 1

                    if vm.ip >= len(code[vm.current_frame]['instructions']):
                        print("End of program reached.")
                    continue

            #if call, step over
            #we need to execute call to change frame
            #and then run full function code
            else:
                #execute call
                print(f"{vm.ip:04d}: {repr(op)}  # CALL (step over)")
                vm.run_op(op, code[vm.current_frame]['labels'])
                vm.ip += 1
                
                #if num of calls and rets is equal
                #then func has finished calling sub-funcs (if any)
                #and func has returned back
                num_calls = 1
                num_rets = 0

                #simulate run_code 
                #but only until this func returns 
                try:
                    while vm.ip < len(code[vm.current_frame]['instructions']): 
                        op = code[vm.current_frame]['instructions'][vm.ip]

                        #handle input ops 
                        if op.opcode == OpCode.INPUT_NUMBER:
                            print("Input for INPUT_NUMBER (one arg): ")
                            try:
                                inp = from_stdin_number()
                            except ValueError:
                                print("Input must be a number!")
                                continue
                            io = MyIO(inp)
                            vm.input_fn = io.input_fn
                            vm.print_fn = io.print_fn
                            print(inp)
                        elif op.opcode == OpCode.INPUT_STRING:
                            print("Input for INPUT_STRING (one arg): ")
                            inp = input()
                            io = MyIO(inp)
                            vm.input_fn = io.input_fn
                            vm.print_fn = io.print_fn

                        #count number of calls and rets
                        if op.opcode == OpCode.CALL:
                            num_calls += 1
                        elif op.opcode == OpCode.RET:
                            num_rets += 1

                        #run op (ret included)                        
                        vm.run_op(op, code[vm.current_frame]['labels'])
                        vm.ip += 1

                        #func returned, stop running code
                        if num_calls == num_rets:
                            break
                except StopIteration:
                    print(f"Stopped at instruction {vm.ip} (BREAKPOINT)")
                    vm.ip += 1 
                except IndexError:
                    print("End of program reached.")
                except Exception:
                    #check if the error came from VM
                    e_type, e_value, e_traceback = sys.exc_info()
                    e_stack = traceback.extract_tb(e_traceback)
                    e_frame = e_stack[-1]
        
                    if 'vm.py' in e_frame.filename:
                        print(f"Runtime error at instruction {vm.ip}: {repr(op)}")
                        print(f"Error: {e_value}")
                        fl = 1
                    else:
                        print(f"Debugger error: {e_value}")

                if vm.ip >= len(code[vm.current_frame]['instructions']):
                    print("End of program reached.")
                continue

        #list    
        elif cmd == "list":
            if not code:
                print("No program loaded. Use: load <path>")
                return
            start = max(0, vm.ip - 5)
            end = min(len(code[vm.current_frame]['instructions']), vm.ip + 6) 
            for i in range(start, end):
                mark = "->" if i == vm.ip else "  "
                try:
                    desc = repr(code[vm.current_frame]['instructions'][i])
                except Exception:
                    #check if the error came from VM
                    e_type, e_value, e_traceback = sys.exc_info()
                    e_stack = traceback.extract_tb(e_traceback)
                    e_frame = e_stack[-1]
        
                    if 'vm.py' in e_frame.filename:
                        print(f"Runtime error at instruction {vm.ip}: {repr(op)}")
                        print(f"Error: {e_value}")
                        fl = 1
                    else:
                        desc = "<bad op>"
                print(f"{mark} {i:04d}: {desc}")
            continue

        #print
        elif cmd == "print":
            if not code:
                print("No program loaded. Use: load <path>")
                continue
            
            name = (arg.split() or [""])[0]
            if not name:
                print("Usage: print <name>")
                continue

            if name in vm.variables:
                print(repr(vm.variables[name]))
            else:
                print(f"{name} is not defined")
            continue
        
        #stack (n)
        elif cmd == "stack":
            if not code:
                print("No program loaded. Use: load <path>")
                continue

            if not vm.stack:
                print("Stack: []")
                continue

            #to show stack in LIFO format
            list_stack = list(reversed(vm.stack))

            #if no args, print entire stack
            if arg is None or arg == "":
                print("Stack (top is [0]):")
                for i, v in enumerate(list_stack):
                    print(f"[{i}] {repr(v)}")
                continue

            #check if multiple
            parts = str(arg).split()
            try:
                if(len(parts) == 1):
                    last = int(parts[0])
                    if last < 0 or last > len(list_stack):
                        print(f"Index out of range (0..{len(list_stack)})")
                        continue
                
                    slice_ = list_stack[0:last]
                    if not slice_:
                        print("There are no elements")
                        continue
                    print("Stack slice (top is [0]):")
                    for i, v in enumerate(slice_, start=0):
                        print(f"[{i}] {repr(v)}")               
                else:
                    print("Incorrect input. Usage: stack [N]")
            except ValueError:
                    print("Arguments must be numbers!")
            except AssertionError:
                #check if the error came from VM
                e_type, e_value, e_traceback = sys.exc_info()
                e_stack = traceback.extract_tb(e_traceback)
                e_frame = e_stack[-1]
        
                if 'vm.py' in e_frame.filename:
                    print(f"Runtime error at instruction {vm.ip}: {repr(op)}")
                    print(f"Error: {e_value}")
                    fl = 1
                else:
                    print(f"Debugger error: {e_value}")
            
            continue

        #memory
        elif cmd == "memory":
            if not code:
                print("No program loaded. Use: load <path>")
                continue

            variables_map = getattr(vm, "variables", {})
            if not variables_map:
                print(f"(Frame {vm.current_frame} has no variables)")
            else:
                print(f"Frame {vm.current_frame} variables\n")
                for k, v in variables_map.items():
                    print(f"  {k} = {repr(v)}")
                print("\n")

            if vm.frames:
                if len(vm.frames) != len(vm.saved_ips):
                    raise Exception(f"Frames are handled incorrectly!")
                for i in range(len(vm.frames)):
                    if not vm.frames[i].items():
                        print(f"Frame {vm.saved_ips[i][0]}' memory is empty\n")
                        continue
                    print(f"Frame {vm.saved_ips[i][0]} variables")
                    for key, value in vm.frames[i].items():
                        print(f"  {key} = {repr(value)}")
                    print("\n")
            continue

        #exec
        elif cmd == "exec":
            if fl == 1:
                print("XVM has crashed, instruction execution is forbidden. Please reload your program file.")
                continue
            
            if not code:
                print("No program loaded. Use: load <path>")
                continue

            parts = arg.split()
            if not parts:
                print("Usage: exec <OPCODE> <arg1, arg2, ..., argN>")
                continue

            try:
                opcode_name =  OpCode[parts[0]]
                args = parts[1:]
                parsed_args = [convert_to_number(a) for a in args]

                op = Op(opcode_name, *parsed_args)

                print(f"Executing: {repr(op)}")

                vm.run_op(op, code[vm.current_frame]['labels'])

            except KeyError:
                print(f"Unknown opcode: {parts[0]}")

            except Exception:
                #check if the error came from VM
                e_type, e_value, e_traceback = sys.exc_info()
                e_stack = traceback.extract_tb(e_traceback)
                e_frame = e_stack[-1]
        
                if 'vm.py' in e_frame.filename:
                    print(f"VM error: {e_value}")
                else:
                    print(f"Execution failed: {e_value}")
            continue
        
        #frame
        elif cmd == "frame":
            if not code:
                print("No program loaded. Use: load <path>")
                continue

            variables_map = getattr(vm, "variables", {})
            current_func = getattr(vm, "current_frame", "?")

            if(len(current_func) == 0): 
                print("There are no active frames")
                continue

            print(f"Active frame: {current_func}")
            if not variables_map:
                print("(Current frame has no variables)")
                continue

            for k, v in variables_map.items():
                print(f"  {k} = {repr(v)}")
            continue

        else:
            print(f"Unknown command: {cmd}. Type 'info'.")

