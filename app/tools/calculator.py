from typing import Literal
from math import prod
from langchain_core.tools import tool


@tool
def calculator(
    numbers: list[float],
    operation: Literal[
        "add",
        "subtract",
        "multiply",
        "divide",
        "average",
        "min",
        "max",
    ],
) -> str:
    """
    Perform mathematical calculations on multiple numbers.

    Args:
        numbers: List of numbers for calculation.
        operation: Mathematical operation to perform.
    """

    if not numbers:
        return "Error: At least one number is required."

    if operation == "add":
        result = sum(numbers)

    elif operation == "subtract":
        result = numbers[0] - sum(numbers[1:])

    elif operation == "multiply":
        result = prod(numbers)

    elif operation == "divide":
        result = numbers[0]

        for number in numbers[1:]:
            if number == 0:
                return "Error: Division by zero is not allowed."

            result /= number

    elif operation == "average":
        result = sum(numbers) / len(numbers)

    elif operation == "min":
        result = min(numbers)

    elif operation == "max":
        result = max(numbers)

    else:
        return "Error: Unsupported operation."

    return str(result)