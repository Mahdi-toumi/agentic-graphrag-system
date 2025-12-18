from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import math

class CalculatorInput(BaseModel):
    """Input for calculator tool"""
    expression: str = Field(description="Mathematical expression to evaluate")

class CalculatorTool(BaseTool):
    name: str = "calculator"
    description: str = """
    Perform mathematical calculations.
    Use this for arithmetic, comparisons, or computing metrics.
    Example: "125000000 / 50000000" for ROI calculations
    """
    args_schema: Type[BaseModel] = CalculatorInput
    
    def _run(self, expression: str) -> str:
        """Evaluate mathematical expression"""
        try:
            # Safe evaluation with limited scope
            safe_dict = {
                'abs': abs, 'round': round, 'min': min, 'max': max,
                'sum': sum, 'pow': pow, 'sqrt': math.sqrt
            }
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            return f"Result: {result}"
        except Exception as e:
            return f"Calculation error: {str(e)}"
