from pathlib import Path
from xvm.vm import VM, parse_string, OpCode, Op, convert_to_number

def xvm_debug():
    vm = VM()
    code = []   # список інструкцій (Op)
    labels = {}
    ip = 0      # instruction pointer (індекс у code)

    print("XVM Debugger (minimal). Type 'info' or 'exit'.")

    while True:
        try:
            line = input("xvm > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nDebug was stopped")
            return

        if not line:
            continue
        #Команда - command, Аргументи - args
        command, *args = line.split(maxsplit=1)
        arg = args[0] if args else ""
        cmd = command.lower()


        # ---- exit/quit ----
        if cmd in ("exit", "quit"):
            print("\nDebug was stopped")
            return


        # ---- info/help ----
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



        # ---- load ----
        elif cmd == "load":
            labels = {}
            for i, op in enumerate(code):
                if op.opcode == OpCode.LABEL:
                    labels[op.args[0]] = i
            
            path = Path(arg.strip("'\""))
            if not path.exists() or not path.is_file():
                print("File not found")
                continue

            try:
                text = path.read_text(encoding="utf-8")
            except Exception as e:
                print(f"Failed to read file: {e}")
                continue

            try:
                code = parse_string(text)  
            except Exception as e:
                print(f"Failed to parse: {e}")
                continue
            print("File loaded succesfully")
            # скидаємо стан, щоб все починалось "заново"
            ip = 0
            vm.stack.clear()
            vm.variables.clear()

            # print(f"Loaded {len(code)} instruction(s) from {path}")
            # # маленький прев’ю-листинг перших до 10 інструкцій
            # for i, op in enumerate(code[:10]):
            #     mark = "->" if i == ip else "  "
            #     print(f"{mark} {i:04d}: {repr(op)}")
            # continue




        # ---- run ----     
        elif cmd == "run":
            try:
                while True:
                    op = code[ip]
                    vm.run_op(op, labels)
                    ip += 1
            except StopIteration:
                print(f"Stopped at instruction {ip} (BREAKPOINT)")
            except IndexError:
                print("End of program reached.")
            continue

        
        # ---- step ----         
        elif cmd == "step":
            ip = step_instruction(vm, ip, code, labels)
            continue


        # ---- next ----   якщо поточна інструкція — CALL, то не заходиш у функцію; 
        # виконуєш її повністю і зупиняєшся на наступній інструкції після виклику
        elif cmd == "next":
            if not code:
                print("No program loaded. Use: load <path>")
                continue
            if ip >= len(code):
                print("IP at end; nothing to execute.")
                continue

            op = code[ip]
            start_depth = len(getattr(vm, "frames", []))
            start_ip = ip


            # 1) Якщо НЕ CALL → це звичайний step
            if op.opcode != OpCode.CALL:
                ip = step_instruction(vm, ip, code, labels)
                continue

            # 2) CALL: step over
            print(f"{ip:04d}: {repr(op)}  # CALL (step over)")
            try:
                vm.run_op(op, labels) 
            except StopIteration:
                print(f"Stopped at instruction {ip} (BREAKPOINT)")
                continue
            except AssertionError as e:
                print(f"Runtime error: {e}")
                continue
            else:
                # VM могла змінити власний vm.ip (JMP тощо): синхронізуємо
                ip = (vm.ip + 1) if hasattr(vm, "ip") and vm.ip != start_ip else (ip + 1)



            # 3) Виконуємо всередині функції, поки не повернемось на початкову глибину
                while len(getattr(vm, "frames", [])) > start_depth:
                    if ip >= len(code):
                        print("Program finished while stepping over call.")
                        break

                    # Стоп до BREAKPOINT всередині функції
                    if code[ip].opcode == OpCode.BREAKPOINT:
                        print(f"Stopped at BREAKPOINT @ {ip} (inside called function)")
                        break

                    prev_ip = ip
                    ip = step_instruction(vm, ip, code, labels)

                    # якщо step зупинився (брейкпоінт/помилка) і ip не зрушився — вийдемо
                    if ip == prev_ip and len(getattr(vm, "frames", [])) > start_depth:
                        break

                # Ми вже ПІСЛЯ CALL (глибина повернулась) — це й є «step over»
                continue


        # ---- list ----    
        elif cmd == "list":
            if not code:
                print("No program loaded. Use: load <path>")
                return
            start = max(0, ip - 5)
            end = min(len(code), ip + 6) # 6 - того шо 5 вперед і нинішня
            for i in range(start, end):
                mark = "->" if i == ip else "  "
                try:
                    desc = repr(code[i])
                except Exception:
                    desc = "<bad op>"
                print(f"{mark} {i:04d}: {desc}")
            continue

        # Функція getattr() повертає значення іменованого атрибута об’єкта. 
        # Якщо його не знайдено, то повертається значення за замовчуванням, надане функцією.

        # ---- print <name> (глобально, поки без локальних фреймів) ----
        elif cmd == "print":
            name = (arg.split() or [""])[0]
            if not name:
                print("Usage: print <name>")
                continue

            # визначаємо, чи ми всередині функції (так само буде в frame)
            in_function = (
                getattr(vm, "current_frame", "$entrypoint$") != "$entrypoint$"
            ) or bool(getattr(vm, "frames", []))

            if in_function:
                # ми у функції → шукати ТІЛЬКИ у локальному фреймі
                variables_map = getattr(vm, "variables", {})
                if name in variables_map:
                    print(repr(variables_map[name]))
                else:
                    print(f"{name} is not defined in local frame")
            else:
                # поза функцією → глобальний рівень
                globals_map = getattr(vm, "variables", {})
                if name in globals_map:
                    print(repr(globals_map[name]))
                else:
                    print(f"{name} is not defined")
            continue
        




        # ---- stack [N] ----
        elif cmd == "stack":
            print(vm.show_stack(arg))
            continue


        # ---- memory ----
        elif cmd == "memory":
            if not vm.variables:
                print("(The memory is empty)")
            else:
                for k, v in vm.variables.items():
                    print(f"{k} = {repr(v)}")
            continue


        # ---- exec ----
        elif cmd == "exec":
            parts = arg.split()
            if not parts:
                print("Usage: exec <OPCODE> <arg1, arg2, ..., argN>")
                continue

            try:
                opcode_name = parts[0]
                args = parts[1:]

                parsed_args = [convert_to_number(a) for a in args]

                # створюємо об'єкт Op, бо інакше всьо фігня (ми даємо текстову команду по факту, а нам треба об'єкт OP)
                opcode = OpCode[opcode_name]
                op = Op(opcode, *parsed_args)

                print(f"Executing: {repr(op)}")
                vm.run_op(op)

            except KeyError:
                print(f"Unknown opcode: {parts[0]}")

            except Exception as e:
                print(f"Execution failed: {e}")
            continue

        
        # ---- frame ----
        elif cmd == "frame":
            # активний фрейм є, якщо ми НЕ в $entrypoint$ (тоді щось можна дивитись) або стек фреймів (щось є збережене) не порожній
            in_function = (getattr(vm, "current_frame", "$entrypoint$") != "$entrypoint$") or bool(getattr(vm, "frames", []))
            if not in_function:
                print("(No active frame)")
                continue

            variables_map = getattr(vm, "variables", {})
            current_func = getattr(vm, "current_frame", "?")

            print(f"Active frame: {current_func}")
            if not variables_map:
                print("(Current frame has no variables)")
                continue

            for k, v in variables_map.items():
                print(f"  {k} = {repr(v)}")
            continue


        else:
            # Невідома команда
            print(f"Unknown command: {cmd}. Type 'info'.")



def step_instruction(vm, ip, code, labels):
    if not code:
        print("No program loaded. Use: load <path>") 
        return ip
    if ip >= len(code):
        print("IP at end; nothing to execute.")
        return ip
    
    op = code[ip]

    # 1) якщо стаємо на BREAKPOINT (саму інструкцію) — ігноруємо його, тобто нічого не робимо, але ip міняємо, бо по факту інструкція типу пройдена
    if op.opcode == OpCode.BREAKPOINT:
        print(f"{ip:04d}: {repr(op)}  # BREAKPOINT consumed")
        ip += 1
        return ip

    # 2) звичайна інструкція — виконуємо рівно одну, і якщо вона успішна теж іp+=1
    print(f"{ip:04d}: {repr(op)}")
    try:
        vm.run_op(op, labels)
        #Якщо екзепшени, то ip не руxаємо.
    except StopIteration:
        # на випадок, якщо BREAKPOINT всередині VM сигналізує виключенням
        print(f"Stopped at instruction {ip} (BREAKPOINT)")
        return ip
    except AssertionError as e:
        # типова помилка твоєї VM (наприклад, змінної немає)
        print(f"Runtime error: {e}")
        return ip
    else:
        ip += 1
        return ip
        


