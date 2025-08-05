def compute_operation(operation: str, operand: int) -> float:
    if operation == "pow":
        return float(operand ** 2)
    elif operation == "fibonacci":
        return float(_fibonacci(operand))
    elif operation == "factorial":
        return float(_factorial(operand))
    else:
        raise ValueError("Unsupported operation")

def _fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("Fibonacci is undefined for negative numbers")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def _factorial(n: int) -> int:
    if n < 0:
        raise ValueError("Factorial is undefined for negative numbers")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result