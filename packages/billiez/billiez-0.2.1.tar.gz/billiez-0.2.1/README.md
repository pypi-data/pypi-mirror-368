```markdown
# billiez

Python package for interacting with NVIDIA's AI API

## Installation

```bash
pip install billiez
```

## Usage

### Basic Usage
```python
import billiez

# Default usage
print(billiez.billiez())

# Generate AI response with default model
response = billiez.billiez(prompt="Tell me about AI")
print(response)
```

### Advanced Usage
```python
import billiez

# Custom model and parameters
response = billiez.billiez(
    model="meta/llama3-70b-instruct",
    prompt="Explain quantum computing",
    temperature=0.7,
    max_tokens=1024,
    stream=False
)
print(response)
```

## Parameters

- `model` (str): AI model to use (default: "deepseek-ai/deepseek-r1-distill-qwen-7b")
- `prompt` (str): Your query for the AI (returns Craftguy info if None)
- `temperature` (float): Controls randomness (0.0-1.0)
- `top_p` (float): Controls diversity (0.0-1.0) 
- `max_tokens` (int): Maximum length of response
- `stream` (bool): Stream response if True

## Requirements

- Python 3.6+
- `openai` package