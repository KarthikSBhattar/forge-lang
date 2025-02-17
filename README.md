# Forge Interpreter with Low-Level Memory Model, Expanded Types, and Extended Methods

This is a **Forge Interpreter** written in Python, implementing a simple stack-based programming language that uses **Reverse Polish Notation (RPN)**. The interpreter supports low-level memory management, expanded types, and extended string, list, and dictionary methods, offering flexibility for a wide range of use cases.

## Features
- **Stack Operations**: Duplicate, swap, drop, over, and rotate stack items.
- **Arithmetic Operations**: Addition, subtraction, multiplication, division, and modulo.
- **Comparison Operations**: Equality, greater than, and less than comparisons.
- **Control Flow**: Conditional (if/else), loops (times, while, for), and function definitions.
- **Memory Management**: Allocate, free, read, and write to a simulated memory block.
- **Extended Data Types**: Support for complex numbers, booleans, None, lists, tuples, sets, frozensets, dictionaries, bytes, bytearray, memoryview, ranges, and conversions for `int`, `float`, and `str`.
- **Extended String, List, and Dict Methods**: Enhanced built-ins to handle common string, list, and dictionary operations (e.g., `str_upper`, `list_append`, `dict_keys`).
- **Error Handling**: Robust command error handling to provide detailed error messages.

## Requirements
- Python 3.x

## Installation

### Clone the repository:
```bash
git clone https://github.com/KarthikSBhattar/forge-lang.git
cd forge-lang
```

### Dependencies:
This interpreter does not require any external dependencies as it uses Python's built-in libraries. Ensure you are using **Python 3**.

## Usage

### Interactive Mode:
To start the interpreter in interactive mode, run the following command:
```bash
python forge_interpreter.py
```
This will launch the interpreter where you can enter Forge code directly. Type `exit` to quit the interpreter.

Example:
```
>> 2 3 add
5
>> 4 2 sub
2
>> "hello" " " str_concat
hello 
```

### File Mode:
To run a Forge script from a file, use the following command:
```bash
python forge_interpreter.py my_forge_code.forge
```
Where `my_forge_code.forge` is a text file containing Forge code. The interpreter will execute the commands in the file.

### Example Forge Code:
```forge
# Simple arithmetic
3 4 add    # Adds 3 and 4 and pushes 7 to the stack
10 2 div   # Divides 10 by 2 and pushes 5 to the stack

# Stack operations
5 dup      # Duplicates the top stack value (5)
2 swap     # Swaps the top two stack values

# Memory management
100 alloc  # Allocates 100 bytes of memory and pushes the pointer to the stack
50 write   # Writes the value 50 at the allocated pointer

# Control Flow
5 times    # Executes the next block 5 times
  "loop" print
end
```

### Function Definitions:
You can define functions in Forge using the `def` keyword. The function will be executed when called.

Example:
```forge
def square
  dup mul
end

2 square    # Result is 4
```

## Built-in Commands:
The interpreter provides a variety of built-in commands, including:
- **Arithmetic**: `add`, `sub`, `mul`, `div`, `mod`
- **Comparison**: `eq`, `gt`, `lt`
- **Control Flow**: `if`, `else`, `times`, `while`, `for`, `end`
- **I/O**: `print`, `input`
- **Memory Management**: `alloc`, `free`, `write`, `read`
- **Types & Conversions**: `complex`, `list`, `tuple`, `set`, `dict`, `bytes`, `range`, `str`
- **Extended String Methods**: `str_upper`, `str_lower`, `str_split`, `str_join`, etc.
- **Extended List Methods**: `list_append`, `list_pop`, `list_sort`, etc.
- **Extended Dict Methods**: `dict_keys`, `dict_values`, `dict_items`, etc.

## Error Handling
The interpreter has built-in error handling for various issues such as stack underflows, invalid operations, memory errors, and more. When an error occurs, the interpreter will output a message with details about the issue.

Example of error handling:
```forge
>> 3 0 div
Error: Division by zero.
```

## Custom Commands and Functions
You can define custom commands using the `def` keyword, and your functions can include any of the built-in operations.

Example of defining a function:
```forge
def greet
  "Hello, world!" print
end

greet  # Prints: Hello, world!
```

## Contributions
Feel free to fork the repository, open issues, or submit pull requests to improve the interpreter. Contributions are always welcome!