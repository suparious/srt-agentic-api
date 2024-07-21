# Function registration

```python
def calculate_sum(a: int, b: int) -> int:
    return a + b

function_def = FunctionDefinition(
    name="calculate_sum",
    description="Calculates the sum of two numbers",
    parameters={"a": {"type": "integer"}, "b": {"type": "integer"}},
    return_type="integer",
    implementation=calculate_sum
)

function_id = await register_function(function_def)
```

## Formatting for summary

```bash
npx ai-digest
```
