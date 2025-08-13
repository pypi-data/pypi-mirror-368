import os
from openai import OpenAI

def billiez(
    api_key: str = None,
    model: str = "deepseek-ai/deepseek-r1-0528",
    prompt: str = "generate a rhyme about 'billiez'",
    temperature: float = 0.6,
    top_p: float = 0.7,
    max_tokens: int = 4096,
    stream: bool = True
) -> str:
    """
    Generates AI response using NVIDIA API
    
    Args:
        api_key: NVIDIA API key (default: NVIDIA_API_KEY environment variable)
        model: Model ID
        prompt: User prompt
        temperature: Creativity control (0-1)
        top_p: Diversity control (0-1)
        max_tokens: Max response length
        stream: Stream response
    
    Returns:
        Full generated text
    """
    api_key = api_key or os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise ValueError("Missing API key. Provide or set NVIDIA_API_KEY environment variable")

    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key
    )

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        stream=stream
    )

    full_response = ""
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta:
            content = chunk.choices[0].delta.content or ""
            reasoning = getattr(chunk.choices[0].delta, "reasoning_content", "") or ""
            part = reasoning + content
            
            if part:
                print(part, end="", flush=True)
                full_response += part

    return full_response