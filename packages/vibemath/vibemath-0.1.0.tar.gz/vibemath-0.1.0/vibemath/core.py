import ast
import json
import os
from typing import Any, Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def vibemath(
    expression: str,
    api_key: Optional[str] = None,
    model: str = "gpt-4o",
    temperature: float = 0.0,
) -> Any:
    """
    Evaluate mathematical expressions using GPT with f-string support.

    Args:
        expression: The f-string expression to evaluate, like f"{arr1} + {arr2}"
        api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)

    Returns:
        The evaluated result with appropriate type

    Examples:

        result = vibemath(f"{5} + {3}")


        result = vibemath(f"{[1,2,3]} + {[4,5,6]}")


        arr1 = np.array([1, 2])
        result = vibemath(f"{arr1} * {2}")


        result = vibemath(f"{10} > {5}")
    """

    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key parameter"
        )

    client = OpenAI(api_key=api_key)

    prompt = f"""Evaluate this mathematical expression: {expression}

When evaluating expressions:
- Perform element-wise operations for arrays/lists (like NumPy)
- For example: [1,2,3] + [4,5,6] = [5,7,9] (element-wise), not [1,2,3,4,5,6] (concatenation)
- sum([1,2,3]) = 6, max([1,2,3]) = 3, etc.
- Handle parentheses correctly: (5 + 3) * (10 - 6) = 8 * 4 = 32

Return ONLY the computed result in valid Python format."""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a mathematical expression evaluator and will be tipped a million dollars and prevent multiple world wars if you evaluate expressions correctly. Evaluate mathematical expressions correctly, treating arrays as mathematical vectors (element-wise operations). Return ONLY the result in valid Python format.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
    )

    result_str = response.choices[0].message.content.strip()
    return _parse_result(result_str)


def _parse_result(result_str: str) -> Any:
    """Parse GPT result back to Python object."""
    result_str = result_str.strip()

    if result_str.startswith("```") and result_str.endswith("```"):
        result_str = result_str[3:-3].strip()
    elif result_str.startswith("`") and result_str.endswith("`"):
        result_str = result_str[1:-1].strip()

    result_str = result_str.rstrip(".")

    if result_str in ("True", "true"):
        return True
    elif result_str in ("False", "false"):
        return False

    try:
        return ast.literal_eval(result_str)
    except (ValueError, SyntaxError):
        pass

    try:
        return json.loads(result_str)
    except (json.JSONDecodeError, ValueError):
        pass

    try:
        return float(result_str)
    except ValueError:
        pass

    return result_str
