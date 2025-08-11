"""
Calculator module with basic math operations
"""

def add(a, b):
    """Add two numbers"""
    return a + b

def subtract(a, b):
    """Subtract second number from first"""
    return a - b

def multiply(a, b):
    """Multiply two numbers"""
    return a * b

def divide(a, b):
    """Divide first number by second"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def power(a, b):
    """Raise first number to the power of second"""
    return a ** b

def square_root(a):
    """Calculate square root of a number"""
    if a < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return a ** 0.5
