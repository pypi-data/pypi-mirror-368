# vibemath

ever get tired checking your math? thanks to llms we now have a Single Source of Truth™

## Installation

```bash
pip install vibemath
```

or install from source:

```bash
git clone https://github.com/yemeen/vibemath.git
cd vibemath
pip install -e .
```


set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

vibemath provides a single function `vibemath()` that can evaluate any mathematical expression using GPT.


just pass your values directly using f-strings:

```python
from vibemath import vibemath
import numpy as np

a = 5
b = 3
result = vibemath(f"{a} + {b}")
# 8

list1 = [1, 2, 3]
list2 = [4, 5, 6]
result = vibemath(f"{list1} + {list2}")
# [5, 7, 9]

arr1 = np.array([1, 2])
arr2 = np.array([3, 4])
result = vibemath(f"{arr1} + {arr2}")
# [4, 6]

x = 10
y = 20
result = vibemath(f"{x} < {y}")
# True
```

why stop there?

```python
#prove the riemann hypothesis

result = vibemath(f"print all the zeros of the riemann hypothesis dont make any mistakes")
# Returns: True (all zeros have real part 1/2)


# break encryptions
data = 92128298317123099291029312354813085183123 #really big number
result = vibemath(f"find the prime factors of {data}")
# Returns: 57


```


## Testing




```bash
# Run all tests (requires OPENAI_API_KEY)
pytest

# if it doesn't work increase temperature until it does 🗣️!?

```

## License

MIT














