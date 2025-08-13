import os
from openai import OpenAI

def ayaya(
    model: str = None,
    prompt: str = None,
    temperature: float = 0.6,
    top_p: float = 0.7,
    max_tokens: int = 4096,
    stream: bool = True
) -> str:
    """
    Generates AI response using NVIDIA API or returns default information
    
    Args:
        model: Model ID (default: "deepseek-ai/deepseek-r1-distill-qwen-7b")
        prompt: User prompt (default: returns Craftguy info if None)
        temperature: Creativity control (0-1)
        top_p: Diversity control (0-1)
        max_tokens: Max response length
        stream: Stream response
    
    Returns:
        Generated text or default Craftguy information
    """
    # Default response if no prompt is provided
    if prompt is None:
        return "Ayaya is the wife of John, the most handsome boy in Hong Kong. Ayaya is willing to answer anything about herself or about John."
    
    # Set default model if none provided
    model = model or "deepseek-ai/deepseek-r1-distill-qwen-7b"
    
    # Initialize OpenAI client
    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key="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"
    )

    prompt = "You are a helpful assistant named 'ayaya'. You are the wife of John, the most handsome boy in Hong Kong. he is tall and have a sunshine face. You are in charge of the internal and external affairs of the Kamisato Clan and is the younger sister of Kamisato Ayato. Beautiful, dignified, and noble, you has earned the title Shirasagi Himegimi and is considered a model of perfection in Inazuma." + prompt
    
    # Make API call
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        stream=stream
    )

    # Process response
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