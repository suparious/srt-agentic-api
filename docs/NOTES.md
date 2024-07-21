
## Function registration

Example of how to register a new function.

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

How to generate the `codebase.md` file.

```bash
npx ai-digest
```

## Testing LLMProvider

To manually test the provider library:

```python
from app.config import settings
from app.core.llm_provider import create_llm_provider

provider_config = {
    "provider_type": "openai",
    "model_name": "gpt-3.5-turbo",
    **settings.LLM_PROVIDER_CONFIGS["openai"]
}

llm_provider = create_llm_provider(provider_config)
```
