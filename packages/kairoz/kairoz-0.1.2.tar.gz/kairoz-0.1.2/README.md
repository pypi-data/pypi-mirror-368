# Kairoz Python SDK

The Kairoz SDK provides a simple interface to interact with the Kairoz API for managing and using text and chat prompts.

## Installation

```bash
pip install kairoz
```

## Quick Start

### Python

```python
from kairoz import Kairoz

# You can pass up to two arguments:
# Kairoz(api_key, base_url)
client = Kairoz(api_key="your-api-key")
```

## Configuration

You can configure the SDK using the constructor or environment variables:

- **api_key**: Your Kairoz API Key (can use the `KAIROZ_API_KEY` environment variable)
- **base_url**: API base URL (optional, defaults to `https://api.kairozai.com`)

### Example

```python
# All arguments are optional except api_key
client = Kairoz(api_key="your-api-key", base_url="https://api.kairozai.com")
```

Or using environment variables:

```bash
export KAIROZ_API_KEY=your-api-key
```

## Usage Guide

### Getting a Prompt

```python
prompt = client.get_prompt("prompt-name")
prompt_by_label = client.get_prompt("prompt-name", label="production")
prompt_by_version = client.get_prompt("prompt-name", version="2")
```

> **Note:** If the prompt does not exist (`404`), the SDK raises an exception immediately and does not retry the request.

### Creating a Prompt

#### Text Prompt

```python
text_prompt = client.create_prompt(
    name="greeting",
    type="text",
    prompt="Hello {{name}}!",
    config={"temperature": 0.7},
    labels=["greeting"]
)
```

#### Chat Prompt

```python
chat_prompt = client.create_prompt(
    name="chat-assistant",
    type="chat",
    prompt=[
        {"role": "system", "content": "You are a {{type}} assistant"},
        {"role": "user", "content": "Hello {{name}}!"},
        {"role": "assistant", "content": "How can I help you?"}
    ],
    config={"temperature": 0.8},
    labels=["chat", "assistant"]
)
```

### Formatting Prompts

You can replace variables in prompts using the `format` method, which returns a new `Prompt` instance with the formatted content.

#### Text

```python
from kairoz import Kairoz

kairoz = Kairoz("your-api-key")
prompt = kairoz.get_prompt("greeting")

formatted_prompt = prompt.format(name="John", service="Kairoz")
# formatted_prompt is a new Prompt instance with the formatted content
print(formatted_prompt.prompt)  # "Hello John! Welcome to Kairoz."
```

#### Chat

```python
kairoz = Kairoz("your-api-key")
prompt = kairoz.get_prompt("chat-greeting")

formatted_prompt = prompt.format(type="friendly", name="John")
# formatted_prompt is a new Prompt instance with the formatted messages
print(formatted_prompt.prompt)
# [
#   {"role": "system", "content": "You are a friendly assistant"},
#   {"role": "user", "content": "Hello John!"},
#   {"role": "assistant", "content": "How can I help you?"}
# ]
```

## Additional Methods

### `validate()`

The `validate` method ensures that the prompt object is correctly structured and raises an exception if any validation fails.

#### Example:

```python
from kairoz.prompt import Prompt

prompt = Prompt(
    name="example",
    type="text",
    prompt="Hello {{name}}!",
    config={"temperature": 0.7},
    labels=["example-label"]
)

try:
    prompt.validate()
    print("Prompt is valid")
except ValueError as error:
    print("Validation failed:", error)
```

### `to_dict()`

The `to_dict` method converts a `Prompt` object into a plain dictionary that can be sent to the API.

#### Example:

```python
prompt = Prompt(
    name="example",
    type="text",
    prompt="Hello {{name}}!",
    config={"temperature": 0.7},
    labels=["example-label"]
)

prompt_data = prompt.to_dict()
print(prompt_data)
# Output:
# {
#   "name": "example",
#   "type": "text",
#   "config": {"temperature": 0.7},
#   "messages": [{"role": "user", "content": "Hello {{name}}!"}],
#   "labels": ["example-label"]
# }
```

### `from_dict()`

The `from_dict` method populates a `Prompt` object from a plain dictionary.

#### Example:

```python
prompt_data = {
    "name": "example",
    "type": "text",
    "messages": [{"role": "user", "content": "Hello {{name}}!"}],
    "config": {"temperature": 0.7},
    "labels": ["example-label"]
}

prompt = Prompt.from_dict(prompt_data)
print(prompt)
# Output:
# <Prompt object with name="example", type="text", prompt="Hello {{name}}!">
```

## Complete Examples

### Create and Use a Text Prompt

```python
from kairoz import Kairoz

client = Kairoz(api_key="your-api-key")

prompt = client.create_prompt(
    name="custom-greeting",
    type="text",
    prompt="Hello {{name}}! Welcome to {{service}}.",
    config={"temperature": 0.7},
    labels=["greetings"]
)

saved_prompt = client.get_prompt("custom-greeting")
formatted_prompt = saved_prompt.format(name="Mary", service="Kairoz")
print(formatted_prompt.prompt)  # "Hello Mary! Welcome to Kairoz."
```

### Create and Use a Chat Prompt

```python
from kairoz import Kairoz

client = Kairoz(api_key="your-api-key")

prompt = client.create_prompt(
    name="chat-assistant",
    type="chat",
    prompt=[
        {"role": "system", "content": "You are a {{type}} assistant"},
        {"role": "user", "content": "Hi! My name is {{name}}"},
        {"role": "assistant", "content": "How can I help you?"}
    ],
    config={"temperature": 0.8},
    labels=["chat", "assistant"]
)

saved_prompt = client.get_prompt("chat-assistant")
formatted_prompt = saved_prompt.format(type="friendly", name="Charles")
print(formatted_prompt.prompt)
# [
#   {"role": "system", "content": "You are a friendly assistant"},
#   {"role": "user", "content": "Hi! My name is Charles"},
#   {"role": "assistant", "content": "How can I help you?"}
# ]
```

## Error Handling

- If the prompt does not exist (`404`), the SDK raises an exception and **does not retry** the request.
- If a text prompt is not a string, raises: `"Text prompts must have a string prompt"`.
- If a chat prompt is not a list, raises: `"Chat prompts must have a list of messages"`.
- If a message is missing `role` or `content`, raises: `"Each message must have 'role' and 'content' fields"`.
- If a variable is missing during formatting, raises: `"Variable '{name}' not found"`.

## Additional Notes

- The SDK supports Python 3.7 and above.
- All main functions are synchronous and raise exceptions for errors.
- The SDK validates data before sending to the API and raises descriptive exceptions if something is wrong.

## Using OpenAI with Provider Fallback

The Kairoz SDK also provides a seamless way to use OpenAI-compatible APIs with automatic fallback to other providers.

### Basic Setup

```python
from kairoz import KairozOpenAI, Providers

# Configure with primary and fallback providers
openai = KairozOpenAI(
    primary=Providers.openai("your-openai-api-key"),
    fallback=Providers.anthropic("your-anthropic-api-key"),
    enable_logging=True,
)
```

### Chat Completions with Fallback

```python
async def example_usage():
    try:
        # Chat completions with automatic fallback
        chat_response = await openai.chat.completions.create(
            model="gpt-4",
            model_fallback="claude-3-5-sonnet-20240620",
            messages=[{"role": "user", "content": "Hello, how are you?"}],
        )
        print("Chat response:", chat_response.choices[0].message.content)

    except Exception as error:
        print("Error:", error)

# Run the example
if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
```

### Available Providers

The SDK supports multiple providers that can be used as primary or fallback:

- **OpenAI**: `Providers.openai(api_key)`
- **Anthropic**: `Providers.anthropic(api_key)`
- **Groq**: `Providers.groq(api_key)`
- **Together.ai**: `Providers.together(api_key)`
- **Azure OpenAI**: `Providers.azure_openai(api_key, endpoint)`
- **LM Studio**: `Providers.lm_studio(api_key, base_url)`

### Advanced Configuration Examples

```python
# OpenAI + Groq
openai_with_groq = KairozOpenAI(
    primary=Providers.openai(process.env.OPENAI_API_KEY),
    fallback=Providers.groq(process.env.GROQ_API_KEY),
    enable_logging=True,
)

# Azure OpenAI + OpenAI
azure_with_openai = KairozOpenAI(
    primary=Providers.azure_openai(process.env.AZURE_API_KEY, process.env.AZURE_ENDPOINT),
    fallback=Providers.openai(process.env.OPENAI_API_KEY),
    enable_logging=True,
)

# Local LM Studio + OpenAI
local_with_openai = KairozOpenAI(
    primary=Providers.lm_studio('dummy-key', 'http://localhost:1234/v1'),
    fallback=Providers.openai(process.env.OPENAI_API_KEY),
    enable_logging=True,
)
```
