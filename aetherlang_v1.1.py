import re
import random
import math
import time

variables = {}

allowed_funcs = {
    'abs': abs,
    'round': round,
    'pow': pow,
    'sqrt': math.sqrt,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'log': math.log,
    'log10': math.log10,
    'floor': math.floor,
    'ceil': math.ceil,
    'pi': math.pi,
    'e': math.e,
    'randomDecimal': lambda a, b: random.uniform(float(a), float(b)),
    'solve': lambda expr: eval(expr, {"__builtins__": None}, {}),
    'simplify': lambda expr: eval(expr, {"__builtins__": None}, {})
}

def evaluate(expr):
    expr = expr.strip()
    expr = re.sub(r'\btrue\b', 'True', expr)
    expr = re.sub(r'\bfalse\b', 'False', expr)
    expr = re.sub(r'\(([^()]*)\)', r'[\1]', expr)

    for var in sorted(variables, key=lambda x: -len(x)):
        expr = re.sub(rf'\b{re.escape(var)}\b', repr(variables[var]), expr)

    expr = re.sub(r'int\(([^()]*)\)', r'int(\1)', expr)
    expr = re.sub(r'boo\(([^()]*)\)', r'bool(\1)', expr)
    expr = re.sub(r'random\(([^,]+),([^)]+)\)', r'random.randint(\1, \2)', expr)

    try:
        env = dict(allowed_funcs)
        env.update(variables)
        return eval(expr, {"__builtins__": None}, env)
    except Exception as e:
        return f"[Error in expression: {e}]"

def parse_block(lines):
    for line in lines:
        parse_line(line)

def parse_line(line):
    line = line.strip()
    if not line or line.startswith('#'):
        return

    if '=' in line and not line.startswith(('text', 'input')):
        var_name, expr = line.split('=', 1)
        var_name = var_name.strip()
        value = evaluate(expr)
        variables[var_name] = value

    elif line.startswith('text(') and line.endswith(')'):
        content = line[5:-1]
        result = evaluate(content)
        print(result)

    elif line.startswith('input(') and line.endswith(')'):
        prompt = line[6:-1].strip()
        if (prompt.startswith('"') and prompt.endswith('"')) or (prompt.startswith("'") and prompt.endswith("'")):
            prompt = prompt[1:-1]
        user_input = input(prompt)
        variables['_input'] = user_input

    else:
        print(f"[Unknown command] → {line}")

def start_repl():
    print("""
🌟 Welcome to AetherLang v1.1 🌟
Type 'exit' to quit. Use empty line to end blocks.
""")

    buffer = []
    repeating = False
    time_repeat = False
    repeat_limit = 0
    conditional = False
    true_block = []
    false_block = []
    elif_block = []
    if_condition = False
    in_else = False
    in_elif = False

    while True:
        try:
            line = input('>>> ' if not (repeating or conditional) else '... ')
            if line.lower() in ('exit', 'quit'):
                print("Goodbye!")
                break

            if line.strip().startswith('repeat ') and line.strip().endswith(':') and not (repeating or conditional):
                match_time = re.match(r'repeat ([0-9.]+)s:', line.strip())
                match_count = re.match(r'repeat ([0-9.]+):', line.strip())

                buffer = []
                if match_time:
                    repeat_limit = float(match_time.group(1))
                    time_repeat = True
                    repeating = True
                elif match_count:
                    repeat_limit = math.ceil(float(match_count.group(1)))
                    time_repeat = False
                    repeating = True
                continue

            if line.strip().startswith('if ') and line.strip().endswith(':') and not (repeating or conditional):
                cond_expr = line.strip()[3:-1].strip()
                if_condition = bool(evaluate(cond_expr))
                conditional = True
                true_block = []
                false_block = []
                elif_block = []
                in_else = False
                in_elif = False
                continue

            if line.strip() == 'other:' and conditional:
                in_else = True
                in_elif = False
                continue

            if line.strip() == 'otherwise:' and conditional:
                in_elif = True
                in_else = False
                continue

            if repeating:
                if line.strip() == '':
                    if time_repeat:
                        start = time.time()
                        while time.time() - start < repeat_limit:
                            for repeat_line in buffer:
                                parse_line(repeat_line)
                    else:
                        for _ in range(repeat_limit):
                            for repeat_line in buffer:
                                parse_line(repeat_line)
                    repeating = False
                    repeat_limit = 0
                    buffer = []
                else:
                    buffer.append(line)
                continue

            if conditional:
                if line.strip() == '':
                    if if_condition:
                        parse_block(true_block)
                    elif elif_block:
                        parse_block(elif_block)
                    else:
                        parse_block(false_block)
                    conditional = False
                    true_block = []
                    false_block = []
                    elif_block = []
                elif in_else:
                    false_block.append(line)
                elif in_elif:
                    elif_block.append(line)
                else:
                    true_block.append(line)
                continue

            parse_line(line)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == '__main__':
    start_repl()