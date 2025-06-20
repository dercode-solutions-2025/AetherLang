import re
import random
import json
import time
import math
import os

variables = {}
storage_path = "aether_storage.json"

# Ensure persistent storage exists
if not os.path.exists(storage_path):
    with open(storage_path, "w") as f:
        json.dump({}, f)

def store(key, value):
    try:
        with open(storage_path, "r+") as f:
            data = json.load(f)
            data[str(key)] = value
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()
    except Exception as e:
        print(f"[Store error: {e}]")

def recall(key):
    try:
        with open(storage_path, "r") as f:
            data = json.load(f)
            return data.get(str(key), "[null]")
    except Exception as e:
        return f"[Recall error: {e}]"

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
    expr = re.sub(r'randomDecimal\(([^,]+),([^)]+)\)', r'random.uniform(\1, \2)', expr)
    expr = re.sub(r'solve\(([^()]*)\)', r'eval(\1)', expr)
    expr = re.sub(r'simplify\(([^()]*)\)', r'eval(\1)', expr)

    expr = expr.replace("pi", "math.pi").replace("e", "math.e")

    try:
        return eval(expr, {"math": math, "random": random})
    except Exception as e:
        return f"[Error in expression: {e}]"

def parse_block(lines):
    for line in lines:
        parse_line(line)

def parse_line(line):
    line = line.strip()
    if not line or line.startswith('#'):
        return

    if '=' in line and not line.startswith(('text', 'input', 'store', 'recall')):
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
        if (prompt.startswith("\"") and prompt.endswith("\"")) or (prompt.startswith("'") and prompt.endswith("'")):
            prompt = prompt[1:-1]
        user_input = input(prompt)
        variables['_input'] = user_input

    elif line.startswith('store(') and line.endswith(')'):
        try:
            args = line[6:-1].split(',', 1)
            key = evaluate(args[0].strip())
            val = evaluate(args[1].strip())
            store(key, val)
        except Exception as e:
            print(f"[Store error: {e}]")

    elif line.startswith('recall(') and line.endswith(')'):
        try:
            key = evaluate(line[7:-1].strip())
            result = recall(key)
            print(result)
        except Exception as e:
            print(f"[Recall error: {e}]")

    else:
        print(f"[Unknown command] → {line}")

def start_repl():
    print(r"""
╔════════════════════════════════════════════════════╗
║              🌟 AetherLang v1.2 🌟                ║
║    Built on Python. Replaced Python. Fully Yours.  ║
╚════════════════════════════════════════════════════╝
Type 'exit' to quit. Use empty line to end blocks.
""")

    while True:
        try:
            line = input('>>> ')
            if line.lower() in ('exit', 'quit'):
                print("Goodbye!")
                break
            parse_line(line)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == '__main__':
    start_repl()
