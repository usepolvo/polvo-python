# tentacles/compute/math.py
import math
import re
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from usepolvo.arms.tentacles.base import BaseTentacle, TentacleDefinition


class MathInput(BaseModel):
    """Input schema for math operations."""

    operation: str = Field(
        ...,
        description="The mathematical operation to perform",
        enum=[
            "add",
            "multiply",
            "subtract",
            "divide",
            "mean",
            "median",
            "min",
            "max",
            "sum",
            "sqrt",
            "power",
            "log",
            "factorial",
        ],
    )
    numbers: str = Field(
        ...,
        description="""
        Comma-separated list of numbers.
        Example: "1.5, 2, 3.7" or "10"
        For operations like power: first number is base, second is exponent
        For log: first number is argument, optional second is base (defaults to e)
        """,
    )
    precision: Optional[int] = Field(
        default=6, description="Number of decimal places for the result", ge=0, le=15
    )


class MathOutput(BaseModel):
    """Output schema for math operations."""

    result: Any = Field(..., description="Calculation result (number or list of numbers)")
    operation: str = Field(..., description="Operation that was performed")
    input_numbers: List[Decimal] = Field(..., description="Input numbers that were used")
    precision: int = Field(..., description="Precision used for calculation")


class MathTentacle(BaseTentacle[MathInput, MathOutput]):
    """A tentacle for performing mathematical operations with precise decimal handling."""

    def _setup(self) -> None:
        """Set up the math tentacle definition."""
        self._definition = TentacleDefinition(
            name="math",
            description="""
            Perform mathematical calculations with precise decimal handling.

            Available operations:
            - Basic: add, subtract, multiply, divide
            - Statistical: mean, median, min, max, sum
            - Advanced: sqrt, power, log, factorial

            Input numbers should be provided as a comma-separated string.
            Examples:
            - Add numbers: {"operation": "add", "numbers": "1.5, 2.3, 3"}
            - Calculate mean: {"operation": "mean", "numbers": "10, 20, 30"}
            - Power calculation: {"operation": "power", "numbers": "2, 3"} (2^3)
            - Square root: {"operation": "sqrt", "numbers": "16"}
            - Natural log: {"operation": "log", "numbers": "2.718"}
            - Log with base: {"operation": "log", "numbers": "100, 10"} (log base 10 of 100)
            """,
            input_schema=MathInput.model_json_schema(),
            output_schema=MathOutput.model_json_schema(),
        )

        # Operation aliases for more natural language matching
        self._operation_aliases = {
            "multiply": ["multiply", "multiplication", "times", "product"],
            "add": ["add", "sum", "plus", "addition"],
            "subtract": ["subtract", "minus", "difference"],
            "divide": ["divide", "division", "divided by"],
            "mean": ["mean", "average", "avg"],
            "median": ["median", "middle"],
            "min": ["min", "minimum", "smallest"],
            "max": ["max", "maximum", "largest"],
            "sum": ["sum", "total"],
            "sqrt": ["sqrt", "square root", "root"],
            "power": ["power", "pow", "exponent"],
            "log": ["log", "logarithm"],
            "factorial": ["factorial", "fact"],
        }

    async def execute(self, input: Union[MathInput, Dict[str, Any]]) -> MathOutput:
        """
        Execute the mathematical operation.

        Args:
            input: Either a MathInput model or a dict with operation, numbers, and optional precision

        Returns:
            MathOutput containing the calculation result and metadata

        Raises:
            ValueError: If input numbers are invalid or operation requirements aren't met
        """
        # Convert dict to model if needed
        if isinstance(input, dict):
            input = MathInput(**input)

        try:
            # Normalize operation name
            operation = self._normalize_operation(input.operation)

            # Parse numbers
            numbers = self._parse_numbers(input.numbers)

            # Validate number requirements
            self._validate_number_requirements(operation, numbers)

            # Calculate result
            result = self._calculate(operation, numbers)

            # Format result to specified precision
            if isinstance(result, (list, tuple)):
                formatted_result = [self._round_decimal(n, input.precision) for n in result]
            else:
                formatted_result = self._round_decimal(result, input.precision)

            return MathOutput(
                result=formatted_result,
                operation=operation,
                input_numbers=numbers,
                precision=input.precision,
            )

        except (ValueError, ZeroDivisionError, InvalidOperation) as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"Calculation failed: {str(e)}")

    def _normalize_operation(self, operation: str) -> str:
        """Convert operation aliases to canonical operation names."""
        operation = operation.lower().strip()
        for canonical, aliases in self._operation_aliases.items():
            if operation in aliases:
                return canonical
        return operation

    def _parse_numbers(self, numbers_str: str) -> List[Decimal]:
        """Parse a comma-separated string of numbers into Decimals."""
        number_strings = numbers_str.split(",")
        parsed_numbers = []

        for num_str in number_strings:
            clean_str = re.sub(r"[^0-9.\-]", "", num_str.strip())
            try:
                parsed_numbers.append(Decimal(clean_str))
            except InvalidOperation:
                raise ValueError(f"Invalid number format: {num_str}")

        if not parsed_numbers:
            raise ValueError("No valid numbers provided")

        return parsed_numbers

    def _validate_number_requirements(self, operation: str, numbers: List[Decimal]) -> None:
        """Validate that the provided numbers meet operation requirements."""
        if operation in ["factorial"]:
            if len(numbers) != 1:
                raise ValueError(f"{operation} requires exactly one number")
            if not float(numbers[0]).is_integer() or numbers[0] < 0:
                raise ValueError(f"{operation} requires a non-negative integer")

        elif operation in ["power", "log"]:
            if operation == "power" and len(numbers) != 2:
                raise ValueError("power operation requires exactly two numbers (base and exponent)")
            elif operation == "log" and len(numbers) not in [1, 2]:
                raise ValueError(
                    "log operation requires one or two numbers (argument and optional base)"
                )

        elif operation in ["divide"]:
            if len(numbers) < 2:
                raise ValueError(f"{operation} requires at least two numbers")
            if any(n == 0 for n in numbers[1:]):
                raise ValueError("Division by zero is not allowed")

    def _calculate(self, operation: str, numbers: List[Decimal]) -> Union[Decimal, List[Decimal]]:
        """Perform the actual calculation."""
        operations = {
            "multiply": math.prod,
            "add": sum,
            "subtract": lambda nums: nums[0] - sum(nums[1:]),
            "divide": lambda nums: nums[0] / math.prod(nums[1:]),
            "mean": lambda nums: sum(nums) / len(nums),
            "median": self._calculate_median,
            "min": min,
            "max": max,
            "sum": sum,
            "sqrt": lambda nums: [Decimal(str(math.sqrt(float(n)))) for n in nums],
            "power": lambda nums: Decimal(str(math.pow(float(nums[0]), float(nums[1])))),
            "log": lambda nums: (
                Decimal(str(math.log(float(nums[0]))))
                if len(nums) == 1
                else Decimal(str(math.log(float(nums[0]), float(nums[1]))))
            ),
            "factorial": lambda nums: Decimal(str(math.factorial(int(nums[0])))),
        }

        if operation not in operations:
            raise ValueError(f"Unsupported operation: {operation}")

        return operations[operation](numbers)

    def _calculate_median(self, numbers: List[Decimal]) -> Decimal:
        """Calculate the median of a list of numbers."""
        sorted_nums = sorted(numbers)
        length = len(sorted_nums)
        mid = length // 2

        if length % 2 == 0:
            return (sorted_nums[mid - 1] + sorted_nums[mid]) / 2
        return sorted_nums[mid]

    def _round_decimal(self, value: Decimal, precision: int) -> Decimal:
        """Round a Decimal to the specified precision."""
        return round(value, precision)
