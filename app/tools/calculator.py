from typing import Literal

from langchain_core.tools import tool


@tool
def calculator(
    a: float,
    b: float,
    operation: Literal["add", "subtract", "multiply", "divide"],
) -> str:
    """
    Perform basic mathematical calculations.

    Args:
        a: First number.
        b: Second number.
        operation: Mathematical operation to perform.
    """

    if operation == "add":
        result = a + b

    elif operation == "subtract":
        result = a - b

    elif operation == "multiply":
        result = a * b

    elif operation == "divide":
        if b == 0:
            return "Error: Division by zero is not allowed."

        result = a / b

    else:
        return "Error: Unsupported operation."

    return str(result)