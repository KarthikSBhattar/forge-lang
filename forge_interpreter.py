#!/usr/bin/env python3
"""
Forge Interpreter with Low-Level Memory Model, Expanded Types,
and Extended String, List, and Dict Methods
-----------------------------------------------------------------

Forge is a simple, stack-based programming language using Reverse Polish Notation.
This forge interpreter supports:
  • Stack operations (dup, swap, drop, over, rot)
  • Arithmetic (add, sub, mul, div, mod)
  • Comparisons (eq, gt, lt)
  • Control flow (if/else, times, while, for)
  • Function definitions (def … end)
  • Variables (store, load)
  • I/O (print, input)
  • Low-level memory management (alloc, free, read, write)
  • Support for many of Python's built-in types including:
      - complex numbers, booleans, None,
      - list, tuple, set, frozenset, dict,
      - bytes, bytearray, memoryview,
      - range, and conversion commands for int, float, and str.
  • Extended built-ins for common string, list, and dict methods.

Blocks are delimited by the token end and control-flow structures use the keywords:
  • if  … [else …] end
  • times … end
  • while … end
  • for   … end
"""

import sys
import argparse

# -------------------------
# Error Classes
# -------------------------
class ForgeError(Exception):
    """Base exception for Forge errors."""
    pass

class StackUnderflow(ForgeError):
    """Raised when an operation needs more items on the stack."""
    pass

class InvalidOperation(ForgeError):
    """Raised when an unknown or invalid operation is encountered."""
    pass

class DivisionByZero(ForgeError):
    """Raised when a division by zero occurs."""
    pass

# -------------------------
# Robust Command Decorator
# -------------------------
def robust_command(func):
    """
    Decorator for built-in command handlers to catch any unexpected errors
    and wrap them in an InvalidOperation error with additional context.
    """
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except ForgeError:
            raise
        except Exception as e:
            raise InvalidOperation(f"{func.__name__} error: {e}")
    return wrapper

# -------------------------
# Memory Manager Class
# -------------------------
class MemoryManager:
    def __init__(self, size=1024):
        # Simulated memory as a bytearray.
        self.memory = bytearray(size)
        self.size = size
        # Free list: a list of tuples (start, size)
        self.free_list = [(0, size)]
        # Allocations: maps pointer (start index) to allocated size.
        self.allocations = {}

    def malloc(self, alloc_size: int) -> int:
        """Allocate a block of memory of given size (in bytes) and return its pointer."""
        if alloc_size <= 0:
            raise MemoryError("Allocation size must be positive.")
        for i, (start, free_size) in enumerate(self.free_list):
            if free_size >= alloc_size:
                ptr = start
                self.allocations[ptr] = alloc_size
                # Update free list.
                if free_size == alloc_size:
                    self.free_list.pop(i)
                else:
                    self.free_list[i] = (start + alloc_size, free_size - alloc_size)
                return ptr
        raise MemoryError("Not enough memory to allocate.")

    def free(self, ptr: int):
        """Free the block of memory starting at pointer."""
        if ptr not in self.allocations:
            raise MemoryError("Invalid free: pointer not allocated.")
        size = self.allocations.pop(ptr)
        self.free_list.append((ptr, size))
        self.free_list = self._merge_free_list()

    def _merge_free_list(self):
        """Merge contiguous free memory blocks."""
        free = sorted(self.free_list, key=lambda x: x[0])
        merged = []
        for start, size in free:
            if merged and merged[-1][0] + merged[-1][1] == start:
                merged[-1] = (merged[-1][0], merged[-1][1] + size)
            else:
                merged.append((start, size))
        return merged

    def write(self, ptr: int, value: int):
        """Write a byte value (0-255) to memory at pointer."""
        if ptr < 0 or ptr >= self.size:
            raise MemoryError("Write error: pointer out of bounds.")
        if not (0 <= value <= 255):
            raise InvalidOperation("Write error: value must be between 0 and 255.")
        self.memory[ptr] = value

    def read(self, ptr: int) -> int:
        """Read a byte value (0-255) from memory at pointer."""
        if ptr < 0 or ptr >= self.size:
            raise MemoryError("Read error: pointer out of bounds.")
        return self.memory[ptr]

# -------------------------
# Forge Interpreter Class
# -------------------------
class ForgeInterpreter:
    def __init__(self):
        # The main data stack.
        self.stack = []
        # User-defined functions: {name: [tokens, ...]}.
        self.functions = {}
        # Named variables (memory storage).
        self.variables = {}
        # Initialize memory manager.
        self.memory_manager = MemoryManager(size=1024)
        # Built-in commands mapping to their handler methods.
        self.builtins = {
            # Stack and arithmetic operations.
            "dup":   self.cmd_dup,
            "swap":  self.cmd_swap,
            "drop":  self.cmd_drop,
            "over":  self.cmd_over,
            "rot":   self.cmd_rot,
            "add":   self.cmd_add,
            "sub":   self.cmd_sub,
            "mul":   self.cmd_mul,
            "div":   self.cmd_div,
            "mod":   self.cmd_mod,
            "eq":    self.cmd_eq,
            "gt":    self.cmd_gt,
            "lt":    self.cmd_lt,
            "print": self.cmd_print,
            "input": self.cmd_input,
            "store": self.cmd_store,
            "load":  self.cmd_load,
            
            # Memory management commands.
            "alloc": self.cmd_alloc,
            "free":  self.cmd_free,
            "write": self.cmd_write,
            "read":  self.cmd_read,
            
            # Type and conversion commands.
            "complex":     self.cmd_complex,
            "list":        self.cmd_list,
            "tuple":       self.cmd_tuple,
            "set":         self.cmd_set,
            "frozenset":   self.cmd_frozenset,
            "dict":        self.cmd_dict,
            "bytes":       self.cmd_bytes,
            "bytearray":   self.cmd_bytearray,
            "memoryview":  self.cmd_memoryview,
            "range":       self.cmd_range,
            "bool":        self.cmd_bool,
            "int":         self.cmd_int,
            "float":       self.cmd_float,
            "str":         self.cmd_str,
            
            # Constants.
            "push_true":   self.cmd_push_true,
            "push_false":  self.cmd_push_false,
            "push_none":   self.cmd_push_none,
            
            # --- Extended String Methods ---
            "str_upper":      self.cmd_str_upper,
            "str_lower":      self.cmd_str_lower,
            "str_split":      self.cmd_str_split,
            "str_split_on":   self.cmd_str_split_on,
            "str_join":       self.cmd_str_join,
            "str_replace":    self.cmd_str_replace,
            "str_find":       self.cmd_str_find,
            "str_strip":      self.cmd_str_strip,
            "str_startswith": self.cmd_str_startswith,
            "str_endswith":   self.cmd_str_endswith,
            "str_capitalize": self.cmd_str_capitalize,
            "str_isdigit":    self.cmd_str_isdigit,
            "str_isalpha":    self.cmd_str_isalpha,
            
            # --- Extended List Methods ---
            "list_append":    self.cmd_list_append,
            "list_pop":       self.cmd_list_pop,
            "list_pop_at":    self.cmd_list_pop_at,
            "list_insert":    self.cmd_list_insert,
            "list_remove":    self.cmd_list_remove,
            "list_extend":    self.cmd_list_extend,
            "list_index":     self.cmd_list_index,
            "list_count":     self.cmd_list_count,
            "list_sort":      self.cmd_list_sort,
            "list_reverse":   self.cmd_list_reverse,
            "list_copy":      self.cmd_list_copy,
            "list_clear":     self.cmd_list_clear,
            "list_len":       self.cmd_list_len,
            "list_get":       self.cmd_list_get,
            "list_set":       self.cmd_list_set,
            "list_slice":     self.cmd_list_slice,
            
            # --- Extended Dict Methods ---
            "dict_keys":      self.cmd_dict_keys,
            "dict_values":    self.cmd_dict_values,
            "dict_items":     self.cmd_dict_items,
            "dict_get":       self.cmd_dict_get,
            "dict_set":       self.cmd_dict_set,
            "dict_pop":       self.cmd_dict_pop,
        }

    # -------------------------
    # Running and Tokenizing
    # -------------------------
    def run(self, code: str):
        """Tokenize and execute the provided Forge source code."""
        tokens = self.tokenize(code)
        self.execute(tokens)

    def tokenize(self, code: str) -> list:
        """
        Convert source code into a list of tokens.
        Comments (starting with '#') are removed.
        Handles quoted string literals.
        """
        tokens = []
        for line in code.splitlines():
            line = line.split('#', 1)[0].strip()  # remove comments and trim
            if not line:
                continue
            tokens.extend(self.split_line(line))
        return tokens

    def split_line(self, line: str) -> list:
        """
        Split a single line into tokens.
        Respects quoted strings (delimited by double quotes).
        Handles escape sequences like \" \\ \n \t.
        """
        result = []
        token = ""
        in_string = False
        escape = False
        for ch in line:
            if in_string:
                if escape:
                    if ch == "n":
                        token += "\n"
                    elif ch == "t":
                        token += "\t"
                    elif ch == "r":
                        token += "\r"
                    elif ch == "b":
                        token += "\b"
                    elif ch == "f":
                        token += "\f"
                    elif ch == "\\":
                        token += "\\"
                    elif ch == "\"":
                        token += "\""
                    else:
                        token += ch  # If the escape character is unrecognized, just add it
                    escape = False
                elif ch == '\\':
                    escape = True
                elif ch == '"':
                    token += ch
                    in_string = False
                    result.append(token)
                    token = ""
                else:
                    token += ch
            else:
                if ch.isspace():
                    if token:
                        result.append(token)
                        token = ""
                elif ch == '"':
                    if token:
                        result.append(token)
                        token = ""
                    token += ch
                    in_string = True
                else:
                    token += ch
        if token:
            result.append(token)
        return result

    # -------------------------
    # Main Execution Loop
    # -------------------------
    def execute(self, tokens: list):
        """Execute a list of tokens; the core interpreter loop."""
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token == "def":
                i = self.handle_def(tokens, i)
            elif token in ("if", "times", "while", "for"):
                i = self.handle_control_flow(tokens, i)
            elif token == "end":
                raise InvalidOperation("Unexpected 'end' encountered.")
            else:
                self.execute_token(token)
                i += 1

    def execute_token(self, token: str):
        """
        Execute a single token. It tries to interpret the token as:
          - An integer literal,
          - A float literal,
          - A string literal (if quoted),
          - A boolean/None literal,
          - A built-in command,
          - Or a user-defined function.
        """
        try:
            # Try integer literal.
            value = int(token)
            self.stack.append(value)
            return
        except ValueError:
            pass

        try:
            # Try float literal.
            value = float(token)
            self.stack.append(value)
            return
        except ValueError:
            pass

        # String literal check.
        if token.startswith('"') and token.endswith('"'):
            self.stack.append(token[1:-1])
            return

        # Boolean and None literals.
        if token == "true":
            self.stack.append(True)
            return
        elif token == "false":
            self.stack.append(False)
            return
        elif token == "none":
            self.stack.append(None)
            return

        # Built-in command?
        if token in self.builtins:
            self.builtins[token]()
        # User-defined function?
        elif token in self.functions:
            func_tokens = self.functions[token]
            self.execute(func_tokens)
        else:
            raise InvalidOperation(f"Unknown token: {token}")

    # -------------------------
    # Control Flow & Function Definitions
    # -------------------------
    def handle_def(self, tokens: list, index: int) -> int:
        """
        Handle a function definition.
        Syntax: def function_name ... end
        """
        if index + 1 >= len(tokens):
            raise InvalidOperation("Expected function name after 'def'.")
        func_name = tokens[index + 1]
        block_tokens, new_index = self.collect_block(tokens, index + 2)
        self.functions[func_name] = block_tokens
        return new_index

    def handle_control_flow(self, tokens: list, index: int) -> int:
        """
        Handle control-flow structures (if, times, while, for).
        Each control structure is terminated by 'end' (with optional 'else' for if).
        """
        token = tokens[index]
        if token == "if":
            cond = self.pop_stack()
            true_block, new_index = self.collect_block(tokens, index + 1, stop_tokens=["else", "end"])
            if cond:
                self.execute(true_block)
                if new_index < len(tokens) and tokens[new_index] == "else":
                    _, new_index = self.collect_block(tokens, new_index + 1)
            else:
                if new_index < len(tokens) and tokens[new_index] == "else":
                    else_block, new_index = self.collect_block(tokens, new_index + 1)
                    self.execute(else_block)
            return new_index

        elif token == "times":
            count = self.pop_stack()
            if not isinstance(count, int):
                raise InvalidOperation("'times' expects an integer count.")
            loop_block, new_index = self.collect_block(tokens, index + 1)
            for _ in range(count):
                self.execute(loop_block)
            return new_index

        elif token == "while":
            loop_block, new_index = self.collect_block(tokens, index + 1)
            cond = self.pop_stack()  # initial condition
            while cond:
                self.execute(loop_block)
                cond = self.pop_stack()
            return new_index

        elif token == "for":
            if len(self.stack) < 2:
                raise StackUnderflow("'for' expects two integer bounds on the stack.")
            end_val = self.pop_stack()
            start_val = self.pop_stack()
            if not (isinstance(start_val, int) and isinstance(end_val, int)):
                raise InvalidOperation("'for' loop bounds must be integers.")
            loop_block, new_index = self.collect_block(tokens, index + 1)
            step = 1 if start_val <= end_val else -1
            for i in range(start_val, end_val + step, step):
                self.stack.append(i)
                self.execute(loop_block)
                self.pop_stack()  # remove loop variable after iteration
            return new_index

        else:
            raise InvalidOperation(f"Unknown control-flow token: {token}")

    def collect_block(self, tokens: list, index: int, stop_tokens: list = None) -> (list, int):
        """
        Collect tokens for a block until a matching 'end' is found.
        If stop_tokens is provided (e.g., for if/else), then stop when one is encountered
        at the base nesting level.
        Returns (block_tokens, new_index) where new_index is right after the block.
        """
        block_tokens = []
        nested = 0
        i = index
        while i < len(tokens):
            token = tokens[i]
            if token in ("if", "times", "while", "for", "def"):
                nested += 1
                block_tokens.append(token)
            elif token == "end":
                if nested == 0:
                    return block_tokens, i + 1
                else:
                    nested -= 1
                    block_tokens.append(token)
            elif stop_tokens and nested == 0 and token in stop_tokens:
                return block_tokens, i
            else:
                block_tokens.append(token)
            i += 1
        raise InvalidOperation("Block not terminated with 'end'.")

    def pop_stack(self):
        """Pop a value from the stack; if empty, raise an error."""
        if not self.stack:
            raise StackUnderflow("Attempted to pop from an empty stack.")
        return self.stack.pop()

    # -------------------------
    # Built-in Command Handlers (Decorated for Robustness)
    # -------------------------
    @robust_command
    def cmd_dup(self):
        if not self.stack:
            raise StackUnderflow("Cannot duplicate: stack is empty.")
        self.stack.append(self.stack[-1])

    @robust_command
    def cmd_swap(self):
        if len(self.stack) < 2:
            raise StackUnderflow("Swap requires at least two stack items.")
        self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]

    @robust_command
    def cmd_drop(self):
        if not self.stack:
            raise StackUnderflow("Drop on empty stack.")
        self.stack.pop()

    @robust_command
    def cmd_over(self):
        if len(self.stack) < 2:
            raise StackUnderflow("Over requires at least two stack items.")
        self.stack.append(self.stack[-2])

    @robust_command
    def cmd_rot(self):
        if len(self.stack) < 3:
            raise StackUnderflow("Rot requires at least three stack items.")
        self.stack[-3], self.stack[-2], self.stack[-1] = self.stack[-2], self.stack[-1], self.stack[-3]

    @robust_command
    def cmd_add(self):
        b = self.pop_stack()
        a = self.pop_stack()
        self.stack.append(a + b)

    @robust_command
    def cmd_sub(self):
        b = self.pop_stack()
        a = self.pop_stack()
        self.stack.append(a - b)

    @robust_command
    def cmd_mul(self):
        b = self.pop_stack()
        a = self.pop_stack()
        self.stack.append(a * b)

    @robust_command
    def cmd_div(self):
        b = self.pop_stack()
        a = self.pop_stack()
        if b == 0:
            raise DivisionByZero("Division by zero.")
        self.stack.append(a // b)

    @robust_command
    def cmd_mod(self):
        b = self.pop_stack()
        a = self.pop_stack()
        self.stack.append(a % b)

    @robust_command
    def cmd_eq(self):
        b = self.pop_stack()
        a = self.pop_stack()
        self.stack.append(True if a == b else False)

    @robust_command
    def cmd_gt(self):
        b = self.pop_stack()
        a = self.pop_stack()
        self.stack.append(True if a > b else False)

    @robust_command
    def cmd_lt(self):
        b = self.pop_stack()
        a = self.pop_stack()
        self.stack.append(True if a < b else False)

    @robust_command
    def cmd_print(self):
        if not self.stack:
            raise StackUnderflow("Print on empty stack.")
        value = self.pop_stack()
        
        # if True, False, or None print in lowercase
        if value is True:
            value = "true"
        elif value is False:
            value = "false"
        elif value is None:
            value = "none"

        print(value)

    @robust_command
    def cmd_input(self):
        user_input = input()
        try:
            val = int(user_input)
        except ValueError:
            try:
                val = float(user_input)
            except ValueError:
                val = user_input
        self.stack.append(val)

    @robust_command
    def cmd_store(self):
        var_name = self.pop_stack()
        value = self.pop_stack()
        if not isinstance(var_name, str):
            raise InvalidOperation("Variable name must be a string.")
        self.variables[var_name] = value

    @robust_command
    def cmd_load(self):
        var_name = self.pop_stack()
        if not isinstance(var_name, str):
            raise InvalidOperation("Variable name must be a string.")
        if var_name not in self.variables:
            raise InvalidOperation(f"Undefined variable '{var_name}'.")
        self.stack.append(self.variables[var_name])

    @robust_command
    def cmd_alloc(self):
        size = self.pop_stack()
        if not isinstance(size, int):
            raise InvalidOperation("alloc expects an integer size.")
        ptr = self.memory_manager.malloc(size)
        self.stack.append(ptr)

    @robust_command
    def cmd_free(self):
        ptr = self.pop_stack()
        if not isinstance(ptr, int):
            raise InvalidOperation("free expects an integer pointer.")
        self.memory_manager.free(ptr)

    @robust_command
    def cmd_write(self):
        value = self.pop_stack()
        ptr = self.pop_stack()
        if not (isinstance(ptr, int) and isinstance(value, int)):
            raise InvalidOperation("write expects integer pointer and value.")
        self.memory_manager.write(ptr, value)

    @robust_command
    def cmd_read(self):
        ptr = self.pop_stack()
        if not isinstance(ptr, int):
            raise InvalidOperation("read expects an integer pointer.")
        value = self.memory_manager.read(ptr)
        self.stack.append(value)

    @robust_command
    def cmd_complex(self):
        imag = self.pop_stack()
        real = self.pop_stack()
        self.stack.append(complex(real, imag))

    @robust_command
    def cmd_list(self):
        count = self.pop_stack()
        if not isinstance(count, int):
            raise InvalidOperation("list expects an integer count.")
        if count < 0:
            raise InvalidOperation("list count must be non-negative.")
        items = [self.pop_stack() for _ in range(count)]
        items.reverse()
        self.stack.append(items)

    @robust_command
    def cmd_tuple(self):
        count = self.pop_stack()
        if not isinstance(count, int):
            raise InvalidOperation("tuple expects an integer count.")
        if count < 0:
            raise InvalidOperation("tuple count must be non-negative.")
        items = [self.pop_stack() for _ in range(count)]
        items.reverse()
        self.stack.append(tuple(items))

    @robust_command
    def cmd_set(self):
        count = self.pop_stack()
        if not isinstance(count, int):
            raise InvalidOperation("set expects an integer count.")
        if count < 0:
            raise InvalidOperation("set count must be non-negative.")
        items = [self.pop_stack() for _ in range(count)]
        self.stack.append(set(items))

    @robust_command
    def cmd_frozenset(self):
        count = self.pop_stack()
        if not isinstance(count, int):
            raise InvalidOperation("frozenset expects an integer count.")
        if count < 0:
            raise InvalidOperation("frozenset count must be non-negative.")
        items = [self.pop_stack() for _ in range(count)]
        self.stack.append(frozenset(items))

    @robust_command
    def cmd_dict(self):
        count = self.pop_stack()
        if not isinstance(count, int):
            raise InvalidOperation("dict expects an integer count (number of key-value pairs).")
        if count < 0:
            raise InvalidOperation("dict count must be non-negative.")
        d = {}
        for _ in range(count):
            value = self.pop_stack()
            key = self.pop_stack()
            d[key] = value
        self.stack.append(d)

    @robust_command
    def cmd_bytes(self):
        count = self.pop_stack()
        if not isinstance(count, int):
            raise InvalidOperation("bytes expects an integer count.")
        if count < 0:
            raise InvalidOperation("bytes count must be non-negative.")
        lst = [self.pop_stack() for _ in range(count)]
        lst.reverse()
        for val in lst:
            if not (isinstance(val, int) and 0 <= val <= 255):
                raise InvalidOperation("bytes expects integer values between 0 and 255.")
        self.stack.append(bytes(lst))

    @robust_command
    def cmd_bytearray(self):
        count = self.pop_stack()
        if not isinstance(count, int):
            raise InvalidOperation("bytearray expects an integer count.")
        if count < 0:
            raise InvalidOperation("bytearray count must be non-negative.")
        lst = [self.pop_stack() for _ in range(count)]
        lst.reverse()
        for val in lst:
            if not (isinstance(val, int) and 0 <= val <= 255):
                raise InvalidOperation("bytearray expects integer values between 0 and 255.")
        self.stack.append(bytearray(lst))

    @robust_command
    def cmd_memoryview(self):
        obj = self.pop_stack()
        try:
            mv = memoryview(obj)
        except TypeError:
            raise InvalidOperation("memoryview expects a bytes-like object.")
        self.stack.append(mv)

    @robust_command
    def cmd_range(self):
        step = self.pop_stack()
        stop = self.pop_stack()
        start = self.pop_stack()
        if not (isinstance(start, int) and isinstance(stop, int) and isinstance(step, int)):
            raise InvalidOperation("range expects three integer arguments: start, stop, step.")
        self.stack.append(range(start, stop, step))

    @robust_command
    def cmd_bool(self):
        val = self.pop_stack()
        self.stack.append(bool(val))

    @robust_command
    def cmd_int(self):
        val = self.pop_stack()
        self.stack.append(int(val))

    @robust_command
    def cmd_float(self):
        val = self.pop_stack()
        self.stack.append(float(val))

    @robust_command
    def cmd_str(self):
        val = self.pop_stack()
        self.stack.append(str(val))

    @robust_command
    def cmd_push_true(self):
        self.stack.append(True)

    @robust_command
    def cmd_push_false(self):
        self.stack.append(False)

    @robust_command
    def cmd_push_none(self):
        self.stack.append(None)

    # -------------------------
    # Extended String Methods
    # -------------------------
    @robust_command
    def cmd_str_upper(self):
        s = self.pop_stack()
        if not isinstance(s, str):
            raise InvalidOperation("str_upper expects a string.")
        self.stack.append(s.upper())

    @robust_command
    def cmd_str_lower(self):
        s = self.pop_stack()
        if not isinstance(s, str):
            raise InvalidOperation("str_lower expects a string.")
        self.stack.append(s.lower())

    @robust_command
    def cmd_str_split(self):
        s = self.pop_stack()
        if not isinstance(s, str):
            raise InvalidOperation("str_split expects a string.")
        self.stack.append(s.split())

    @robust_command
    def cmd_str_split_on(self):
        sep = self.pop_stack()
        s = self.pop_stack()
        if not (isinstance(s, str) and isinstance(sep, str)):
            raise InvalidOperation("str_split_on expects a string and a separator string.")
        self.stack.append(s.split(sep))

    @robust_command
    def cmd_str_join(self):
        sep = self.pop_stack()
        lst = self.pop_stack()
        if not isinstance(sep, str):
            raise InvalidOperation("str_join expects a separator string.")
        if not (isinstance(lst, list) and all(isinstance(x, str) for x in lst)):
            raise InvalidOperation("str_join expects a list of strings.")
        self.stack.append(sep.join(lst))

    @robust_command
    def cmd_str_replace(self):
        new = self.pop_stack()
        old = self.pop_stack()
        s = self.pop_stack()
        if not isinstance(s, str):
            raise InvalidOperation("str_replace expects a string.")
        self.stack.append(s.replace(old, new))

    @robust_command
    def cmd_str_find(self):
        substr = self.pop_stack()
        s = self.pop_stack()
        if not isinstance(s, str):
            raise InvalidOperation("str_find expects a string.")
        self.stack.append(s.find(substr))

    @robust_command
    def cmd_str_strip(self):
        s = self.pop_stack()
        if not isinstance(s, str):
            raise InvalidOperation("str_strip expects a string.")
        self.stack.append(s.strip())

    @robust_command
    def cmd_str_startswith(self):
        prefix = self.pop_stack()
        s = self.pop_stack()
        if not isinstance(s, str):
            raise InvalidOperation("str_startswith expects a string.")
        self.stack.append(s.startswith(prefix))

    @robust_command
    def cmd_str_endswith(self):
        suffix = self.pop_stack()
        s = self.pop_stack()
        if not isinstance(s, str):
            raise InvalidOperation("str_endswith expects a string.")
        self.stack.append(s.endswith(suffix))

    @robust_command
    def cmd_str_capitalize(self):
        s = self.pop_stack()
        if not isinstance(s, str):
            raise InvalidOperation("str_capitalize expects a string.")
        self.stack.append(s.capitalize())

    @robust_command
    def cmd_str_isdigit(self):
        s = self.pop_stack()
        if not isinstance(s, str):
            raise InvalidOperation("str_isdigit expects a string.")
        self.stack.append(s.isdigit())

    @robust_command
    def cmd_str_isalpha(self):
        s = self.pop_stack()
        if not isinstance(s, str):
            raise InvalidOperation("str_isalpha expects a string.")
        self.stack.append(s.isalpha())

    # -------------------------
    # Extended List Methods
    # -------------------------
    @robust_command
    def cmd_list_append(self):
        elem = self.pop_stack()
        lst = self.pop_stack()
        if not isinstance(lst, list):
            raise InvalidOperation("list_append expects a list.")
        lst.append(elem)
        self.stack.append(lst)

    @robust_command
    def cmd_list_pop(self):
        lst = self.pop_stack()
        if not isinstance(lst, list):
            raise InvalidOperation("list_pop expects a list.")
        if not lst:
            raise InvalidOperation("list_pop on empty list.")
        elem = lst.pop()
        self.stack.append(elem)

    @robust_command
    def cmd_list_pop_at(self):
        index = self.pop_stack()
        lst = self.pop_stack()
        if not isinstance(lst, list):
            raise InvalidOperation("list_pop_at expects a list.")
        try:
            elem = lst.pop(index)
        except Exception as e:
            raise InvalidOperation(f"list_pop_at error: {e}")
        self.stack.append(elem)

    @robust_command
    def cmd_list_insert(self):
        elem = self.pop_stack()
        index = self.pop_stack()
        lst = self.pop_stack()
        if not isinstance(lst, list):
            raise InvalidOperation("list_insert expects a list.")
        lst.insert(index, elem)
        self.stack.append(lst)

    @robust_command
    def cmd_list_remove(self):
        elem = self.pop_stack()
        lst = self.pop_stack()
        if not isinstance(lst, list):
            raise InvalidOperation("list_remove expects a list.")
        try:
            lst.remove(elem)
        except ValueError:
            raise InvalidOperation("list_remove: element not found.")
        self.stack.append(lst)

    @robust_command
    def cmd_list_extend(self):
        lst2 = self.pop_stack()
        lst1 = self.pop_stack()
        if not (isinstance(lst1, list) and isinstance(lst2, list)):
            raise InvalidOperation("list_extend expects two lists.")
        lst1.extend(lst2)
        self.stack.append(lst1)

    @robust_command
    def cmd_list_index(self):
        elem = self.pop_stack()
        lst = self.pop_stack()
        if not isinstance(lst, list):
            raise InvalidOperation("list_index expects a list.")
        try:
            idx = lst.index(elem)
        except ValueError:
            raise InvalidOperation("list_index: element not found.")
        self.stack.append(idx)

    @robust_command
    def cmd_list_count(self):
        elem = self.pop_stack()
        lst = self.pop_stack()
        if not isinstance(lst, list):
            raise InvalidOperation("list_count expects a list.")
        self.stack.append(lst.count(elem))

    @robust_command
    def cmd_list_sort(self):
        lst = self.pop_stack()
        if not isinstance(lst, list):
            raise InvalidOperation("list_sort expects a list.")
        try:
            lst.sort()
        except Exception as e:
            raise InvalidOperation(f"list_sort error: {e}")
        self.stack.append(lst)

    @robust_command
    def cmd_list_reverse(self):
        lst = self.pop_stack()
        if not isinstance(lst, list):
            raise InvalidOperation("list_reverse expects a list.")
        lst.reverse()
        self.stack.append(lst)

    @robust_command
    def cmd_list_copy(self):
        lst = self.pop_stack()
        if not isinstance(lst, list):
            raise InvalidOperation("list_copy expects a list.")
        self.stack.append(lst.copy())

    @robust_command
    def cmd_list_clear(self):
        lst = self.pop_stack()
        if not isinstance(lst, list):
            raise InvalidOperation("list_clear expects a list.")
        lst.clear()
        self.stack.append(lst)

    @robust_command
    def cmd_list_len(self):
        lst = self.pop_stack()
        if not isinstance(lst, list):
            raise InvalidOperation("list_len expects a list.")
        self.stack.append(len(lst))

    @robust_command
    def cmd_list_get(self):
        index = self.pop_stack()
        lst = self.pop_stack()
        if not isinstance(lst, list):
            raise InvalidOperation("list_get expects a list.")
        try:
            elem = lst[index]
        except Exception as e:
            raise InvalidOperation(f"list_get error: {e}")
        self.stack.append(elem)

    @robust_command
    def cmd_list_set(self):
        value = self.pop_stack()
        index = self.pop_stack()
        lst = self.pop_stack()
        if not isinstance(lst, list):
            raise InvalidOperation("list_set expects a list.")
        try:
            lst[index] = value
        except Exception as e:
            raise InvalidOperation(f"list_set error: {e}")
        self.stack.append(lst)

    @robust_command
    def cmd_list_slice(self):
        end = self.pop_stack()
        start = self.pop_stack()
        lst = self.pop_stack()
        if not isinstance(lst, list):
            raise InvalidOperation("list_slice expects a list.")
        self.stack.append(lst[start:end])

    # -------------------------
    # Extended Dict Methods
    # -------------------------
    @robust_command
    def cmd_dict_keys(self):
        d = self.pop_stack()
        if not isinstance(d, dict):
            raise InvalidOperation("dict_keys expects a dict.")
        self.stack.append(list(d.keys()))

    @robust_command
    def cmd_dict_values(self):
        d = self.pop_stack()
        if not isinstance(d, dict):
            raise InvalidOperation("dict_values expects a dict.")
        self.stack.append(list(d.values()))

    @robust_command
    def cmd_dict_items(self):
        d = self.pop_stack()
        if not isinstance(d, dict):
            raise InvalidOperation("dict_items expects a dict.")
        self.stack.append(list(d.items()))

    @robust_command
    def cmd_dict_get(self):
        key = self.pop_stack()
        d = self.pop_stack()
        if not isinstance(d, dict):
            raise InvalidOperation("dict_get expects a dict.")
        self.stack.append(d.get(key))

    @robust_command
    def cmd_dict_set(self):
        value = self.pop_stack()
        key = self.pop_stack()
        d = self.pop_stack()
        if not isinstance(d, dict):
            raise InvalidOperation("dict_set expects a dict.")
        d[key] = value
        self.stack.append(d)

    @robust_command
    def cmd_dict_pop(self):
        key = self.pop_stack()
        d = self.pop_stack()
        if not isinstance(d, dict):
            raise InvalidOperation("dict_pop expects a dict.")
        try:
            val = d.pop(key)
        except KeyError:
            raise InvalidOperation("dict_pop: key not found.")
        self.stack.append(val)

# -------------------------
# Main Entry Point
# -------------------------
def main():
    parser = argparse.ArgumentParser(description="Forge Interpreter with Memory Model, Expanded Types, and Extended Methods")
    parser.add_argument("file", nargs="?", help="Path to a Forge source file")
    args = parser.parse_args()

    interpreter = ForgeInterpreter()

    if args.file:
        try:
            with open(args.file, "r") as f:
                code = f.read()
            interpreter.run(code)
        except Exception as e:
            print("Error:", e)
    else:
        print("Forge Interpreter with Extended Methods (type 'exit' to quit)")
        while True:
            try:
                line = input(">> ")
                if line.strip() == "exit":
                    break
                interpreter.run(line)
            except Exception as e:
                print("Error:", e)

if __name__ == "__main__":
    main()