import re
import time
import math
import random
import json
import os
from typing import List

# Persistent storage setup
storage_path = "aether_storage.json"
if not os.path.exists(storage_path):
    with open(storage_path, "w") as f:
        json.dump({}, f)

# Allowed math and utility functions for safe eval
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
    'randomInt': lambda a, b: random.randint(int(a), int(b)),
    'solve': lambda expr: eval(expr, {"__builtins__": None}, {}),
    'simplify': lambda expr: eval(expr, {"__builtins__": None}, {}),
}

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

def evaluate(expr, variables):
    expr = expr.strip()
    expr = re.sub(r'\btrue\b', 'True', expr, flags=re.IGNORECASE)
    expr = re.sub(r'\bfalse\b', 'False', expr, flags=re.IGNORECASE)

    # Replace variables in expression (longest first)
    for var in sorted(variables, key=lambda x: -len(x)):
        # Use word boundaries for exact matches
        expr = re.sub(rf'\b{re.escape(var)}\b', repr(variables[var]), expr)

    # Replace custom syntax for int, bool, random
    expr = re.sub(r'int\(([^()]*)\)', r'int(\1)', expr)
    expr = re.sub(r'boo\(([^()]*)\)', r'bool(\1)', expr)
    expr = re.sub(r'random\(([^,]+),([^)]+)\)', r'randomInt(\1, \2)', expr)

    try:
        env = dict(allowed_funcs)
        env.update(variables)
        return eval(expr, {"__builtins__": None}, env)
    except Exception as e:
        return f"[Error in expression: {e}]"

class AetherLangInterpreter:
    def __init__(self):
        self.variables = {}
        self.groups = {}
        self.key_states = {}

    def text(self, message: str):
        print(message)

    def image(self, path: str):
        return f"Image({path})"

    def key(self, key_name: str):
        return self.key_states.get(key_name, False)

    def set_key_state(self, key_name: str, state: bool):
        self.key_states[key_name] = state

    def change_position_board(self, direction_distance: str):
        print(f"Moving: {direction_distance}")

    def parse_and_execute(self, code: str):
        lines = code.strip().split('\n')
        self.execute_lines(lines)

    def execute_lines(self, lines: List[str], indent_level: int = 0):
        i = 0
        while i < len(lines):
            line = lines[i].rstrip()
            if not line.strip():
                i += 1
                continue

            current_indent = len(line) - len(line.lstrip())
            if current_indent < indent_level and line.strip():
                break
            elif current_indent > indent_level:
                i += 1
                continue

            line = line.strip()

            # Handle extended commands first
            if line.startswith('text('):
                self.handle_text(line)
            elif line.startswith('store('):
                self.handle_store(line)
            elif line.startswith('recall('):
                self.handle_recall(line)
            elif line.startswith('input('):
                self.handle_input(line)
            elif '=' in line and not line.startswith(('if', 'text', 'input', 'store', 'recall')):
                self.handle_assignment(line)
            elif line.startswith('repeat for'):
                i = self.handle_time_repeat(lines, i, indent_level)
            elif line.startswith('repeat '):
                i = self.handle_count_repeat(lines, i, indent_level)
            elif line.startswith('group '):
                i = self.handle_group(lines, i, indent_level)
            elif line.startswith('if '):
                i = self.handle_if(lines, i, indent_level)
            elif line.startswith('change.position.board('):
                self.handle_position_change(line)
            else:
                print(f"[Unknown command] → {line}")

            i += 1

    # Basic handlers:
    def handle_text(self, line: str):
        match = re.match(r'text\("([^"]*)"\)', line)
        if match:
            self.text(match.group(1))

    def handle_store(self, line: str):
        args = line[6:-1].split(',', 1)
        if len(args) == 2:
            key = evaluate(args[0].strip(), self.variables)
            value = evaluate(args[1].strip(), self.variables)
            store(key, value)

    def handle_recall(self, line: str):
        key = evaluate(line[7:-1].strip(), self.variables)
        val = recall(key)
        print(val)

    def handle_input(self, line: str):
        prompt = line[6:-1].strip()
        if (prompt.startswith('"') and prompt.endswith('"')) or (prompt.startswith("'") and prompt.endswith("'")):
            prompt = prompt[1:-1]
        user_input = input(prompt)
        self.variables['_input'] = user_input

    def handle_assignment(self, line: str):
        var_name, expr = line.split('=', 1)
        val = evaluate(expr, self.variables)
        self.variables[var_name.strip()] = val

    # Control structures:
    def handle_time_repeat(self, lines: List[str], start_idx: int, indent_level: int):
        line = lines[start_idx].rstrip()
        match = re.match(r'repeat for (\d+)s:', line)
        if not match:
            return start_idx

        duration = int(match.group(1))
        repeat_indent = len(line) - len(line.lstrip())

        body_lines = []
        i = start_idx + 1
        while i < len(lines):
            body_line = lines[i].rstrip('\n')
            if not body_line.strip():
                i += 1
                continue
            body_indent = len(body_line) - len(body_line.lstrip())
            if body_indent <= repeat_indent:
                break
            body_lines.append(body_line)
            i += 1

        if not body_lines:
            return i - 1

        start_time = time.time()
        end_time = start_time + duration

        while time.time() < end_time:
            self.execute_lines(body_lines, indent_level=repeat_indent + 1)
            time.sleep(0.05)

        return i - 1

    def handle_count_repeat(self, lines: List[str], start_idx: int, indent_level: int):
        line = lines[start_idx].rstrip()
        match = re.match(r'repeat (\d+):', line)
        if not match:
            return start_idx

        count = int(match.group(1))
        repeat_indent = len(line) - len(line.lstrip())

        body_lines = []
        i = start_idx + 1
        while i < len(lines):
            body_line = lines[i].rstrip('\n')
            if not body_line.strip():
                i += 1
                continue
            body_indent = len(body_line) - len(body_line.lstrip())
            if body_indent <= repeat_indent:
                break
            body_lines.append(body_line)
            i += 1

        for _ in range(count):
            self.execute_lines(body_lines, indent_level=repeat_indent + 1)

        return i - 1

    def handle_group(self, lines: List[str], start_idx: int, indent_level: int):
        line = lines[start_idx].rstrip()
        match = re.match(r'group ([^:]+):', line)
        if not match:
            return start_idx

        group_name = match.group(1).strip()
        group_indent = len(line) - len(line.lstrip())

        body_lines = []
        i = start_idx + 1
        while i < len(lines):
            body_line = lines[i].rstrip('\n')
            if not body_line.strip():
                i += 1
                continue
            body_indent = len(body_line) - len(body_line.lstrip())
            if body_indent <= group_indent:
                break
            body_lines.append(body_line)
            i += 1

        self.groups[group_name] = body_lines
        self.execute_lines(body_lines, indent_level=group_indent + 1)

        return i - 1

    def handle_if(self, lines: List[str], start_idx: int, indent_level: int):
        line = lines[start_idx].rstrip()
        match = re.match(r'if ([^:]+):', line)
        if not match:
            return start_idx

        condition = match.group(1).strip()
        if_indent = len(line) - len(line.lstrip())

        body_lines = []
        i = start_idx + 1
        while i < len(lines):
            body_line = lines[i].rstrip('\n')
            if not body_line.strip():
                i += 1
                continue
            body_indent = len(body_line) - len(body_line.lstrip())
            if body_indent <= if_indent:
                break
            body_lines.append(body_line)
            i += 1

        if self.evaluate_condition(condition):
            self.execute_lines(body_lines, indent_level=if_indent + 1)

        return i - 1

    def evaluate_condition(self, condition: str) -> bool:
        if ' is True' in condition:
            var_name = condition.replace(' is True', '').strip()
            return bool(self.variables.get(var_name, False))
        elif ' is False' in condition:
            var_name = condition.replace(' is False', '').strip()
            return not bool(self.variables.get(var_name, False))
        else:
            # Try evaluating condition as expression
            result = evaluate(condition, self.variables)
            return bool(result)

    def handle_position_change(self, line: str):
        match = re.match(r'change\.position\.board\(([^)]+)\)', line)
        if match:
            direction_distance = match.group(1)
            self.change_position_board(direction_distance)

def run_custom_code():
    interpreter = AetherLangInterpreter()

    print("+---------------------------------------------------------------+")
    print("|             ☀️ AetherLang v2.0 ☀️                            |")
    print("|        "The best way out is always through." -Robert Frost    |")
    print("+---------------------------------------------------------------+")
    print()

    print("Write your AetherLang code below. Type 'END' on a new line when finished.")
    print("Type 'QUIT' to exit.\n")

    while True:
        try:
            print("Enter your AetherLang code:")
            lines = []
            while True:
                try:
                    line = input(">> ")
                    if line.strip().upper() == 'END':
                        break
                    elif line.strip().upper() == 'QUIT':
                        print("Goodbye!")
                        return
                    lines.append(line)
                except (EOFError, KeyboardInterrupt):
                    print("\nGoodbye!")
                    return

            if lines:
                code = '\n'.join(lines)
                print("\n--- Executing ---")
                try:
                    interpreter.parse_and_execute(code)
                except Exception as e:
                    print(f"Error: {e}")
                print("--- Done ---\n")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    run_custom_code()
