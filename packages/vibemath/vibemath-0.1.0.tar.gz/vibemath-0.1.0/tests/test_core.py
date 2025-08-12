"""Test suite for vibemath f-string functionality"""

import pytest
import numpy as np
import os
from vibemath import vibemath


@pytest.fixture(scope="session")
def api_key():
    """Get API key from environment or skip tests."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        pytest.skip("OPENAI_API_KEY not set - skipping integration tests")
    return key


class TestFStringSupport:
    """Test f-string functionality with actual API calls."""

    def test_simple_arithmetic(self, api_key):
        """Test basic arithmetic with f-strings."""
        a = 5
        b = 3
        result = vibemath(f"{a} + {b}")
        assert result == 8

        result = vibemath(f"{a} * {b}")
        assert result == 15

        result = vibemath(f"{a} - {b}")
        assert result == 2

    def test_list_operations(self, api_key):
        """Test list operations with f-strings."""
        list1 = [1, 2, 3]
        list2 = [4, 5, 6]

        # Element-wise addition
        result = vibemath(f"{list1} + {list2}")
        assert result == [5, 7, 9] or result == [
            1,
            2,
            3,
            4,
            5,
            6,
        ]  # GPT might concatenate

        # List sum
        result = vibemath(f"sum({list1})")
        assert result == 6

        # List max/min
        numbers = [3, 7, 2, 9, 1, 5]
        result = vibemath(f"max({numbers})")
        assert result == 9

        result = vibemath(f"min({numbers})")
        assert result == 1

    def test_numpy_arrays(self, api_key):
        """Test NumPy array operations with f-strings."""
        arr1 = np.array([1, 2, 3])
        arr2 = np.array([4, 5, 6])

        # Array addition
        result = vibemath(f"{arr1} + {arr2}")
        assert result == [5, 7, 9]

        # Array multiplication with scalar
        arr = np.array([10, 20, 30])
        scalar = 2
        result = vibemath(f"{arr} * {scalar}")
        assert result == [20, 40, 60]

    def test_2d_arrays(self, api_key):
        """Test 2D array operations with f-strings."""
        matrix1 = np.array([[1, 2], [3, 4]])
        matrix2 = np.array([[5, 6], [7, 8]])

        result = vibemath(f"{matrix1} + {matrix2}")
        expected = [[6, 8], [10, 12]]
        assert result == expected

    def test_boolean_comparisons(self, api_key):
        """Test boolean comparisons with f-strings."""
        x = 10
        y = 20

        result = vibemath(f"{x} < {y}")
        assert result is True

        result = vibemath(f"{x} > {y}")
        assert result is False

        result = vibemath(f"{x} == {x}")
        assert result is True

        # Complex boolean
        a, b, c = 3, 4, 5
        result = vibemath(f"({a} + {b} > {c}) and ({b} + {c} > {a})")
        assert result is True

    def test_complex_expressions(self, api_key):
        """Test complex mathematical expressions with f-strings."""
        # Order of operations
        result = vibemath(f"{2} + {3} * {4}")
        assert result == 14

        # Nested operations
        result = vibemath(f"({5} + {3}) * ({10} - {6})")
        assert result == 32

        # Power operations
        result = vibemath(f"{2} ** {3}")
        assert result == 8

        # Square root (as power)
        result = vibemath(f"{9} ** 0.5")
        assert result == 3.0

    def test_floating_point(self, api_key):
        """Test floating point operations with f-strings."""
        a = 0.1
        b = 0.2
        result = vibemath(f"{a} + {b}")
        assert abs(result - 0.3) < 0.0001

        # Division
        result = vibemath(f"{10} / {3}")
        assert abs(result - 3.333333) < 0.0001

    def test_modulo_operations(self, api_key):
        """Test modulo operations with f-strings."""
        result = vibemath(f"{17} % {5}")
        assert result == 2

        result = vibemath(f"{100} % {10}")
        assert result == 0

        # Divisibility check
        result = vibemath(f"{100} % {10} == 0")
        assert result is True

    def test_list_comprehension_style(self, api_key):
        """Test list comprehension-style operations with f-strings."""
        # Sum of squares
        numbers = [1, 2, 3, 4, 5]
        result = vibemath(f"sum([x**2 for x in {numbers}])")
        assert result == 55  # 1 + 4 + 9 + 16 + 25

    def test_nested_lists(self, api_key):
        """Test nested list operations with f-strings."""
        nested = [[1, 2], [3, 4], [5, 6]]
        result = vibemath(f"sum([sum(row) for row in {nested}])")
        assert result == 21  # (1+2) + (3+4) + (5+6)

    def test_string_operations(self, api_key):
        """Test string length operations with f-strings."""
        text = "Hello, World!"
        result = vibemath(f"len('{text}')")
        assert result == 13

    def test_mixed_types(self, api_key):
        """Test mixed type operations with f-strings."""
        list_vals = [10, 20, 30]
        threshold = 25

        result = vibemath(f"max({list_vals}) > {threshold}")
        assert result is True

        result = vibemath(f"min({list_vals}) > {threshold}")
        assert result is False

    def test_array_shape(self, api_key):
        """Test array shape operations with f-strings."""
        arr = np.random.randint(0, 10, size=(3, 4))

        # Note: GPT might return shape as list or tuple
        result = vibemath(f"{arr}.shape")
        assert result == [3, 4] or result == (3, 4)

    def test_statistical_operations(self, api_key):
        """Test statistical operations with f-strings."""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        # Mean
        result = vibemath(f"sum({data}) / len({data})")
        assert result == 5.5

        # Sum
        result = vibemath(f"sum({data})")
        assert result == 55

    def test_error_handling(self):
        """Test error handling."""
        # Missing API key
        original_key = os.environ.get("OPENAI_API_KEY")
        if original_key:
            del os.environ["OPENAI_API_KEY"]

        try:
            with pytest.raises(ValueError, match="OpenAI API key required"):
                vibemath(f"{2} + {2}")
        finally:
            if original_key:
                os.environ["OPENAI_API_KEY"] = original_key


@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set - skipping integration tests",
)
class TestFStringEdgeCases:
    """Test edge cases with f-strings."""

    def test_empty_lists(self, api_key):
        """Test operations with empty lists."""
        empty = []
        result = vibemath(f"len({empty})")
        assert result == 0

    def test_single_element(self, api_key):
        """Test single element operations."""
        single = [42]
        result = vibemath(f"sum({single})")
        assert result == 42

    def test_large_numbers(self, api_key):
        """Test large number operations."""
        large1 = 1000000
        large2 = 2000000
        result = vibemath(f"{large1} + {large2}")
        assert result == 3000000

    def test_negative_numbers(self, api_key):
        """Test negative number operations."""
        result = vibemath(f"{-5} + {3}")
        assert result == -2

        result = vibemath(f"{-10} * {-2}")
        assert result == 20

    def test_zero_operations(self, api_key):
        """Test operations with zero."""
        result = vibemath(f"{0} * {100}")
        assert result == 0

        result = vibemath(f"{5} + {0}")
        assert result == 5
