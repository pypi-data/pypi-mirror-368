from g4f.client import Client
from huggingface_hub import InferenceClient

# ===== G4F Client =====
_g4f_client = Client()

def np(prompt: str, model: str = "gpt-4o-mini", web_search: bool = False) -> None:
    """
    Send a prompt to the chat client and print the response (using g4f).
    
    Args:
        prompt (str): The user prompt to send.
        model (str): Model name (default: 'gpt-4o-mini').
        web_search (bool): Whether to enable web search (default: False).
    """
    response = _g4f_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        web_search=web_search
    )
    print(response.choices[0].message.content)


# ===== HuggingFace Client =====
_hf_client = InferenceClient(
    "mistralai/Mistral-7B-Instruct-v0.2",
    token="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"
)

def pd(prompt: str, max_tokens: int = 2000) -> str:
    """
    Send a prompt to HuggingFace model and return the response text.

    Args:
        prompt (str): The user prompt to send.
        max_tokens (int): Maximum tokens in the reply (default: 100).

    Returns:
        str: The generated response text.
    """
    messages = [{"role": "user", "content": prompt}]
    response = _hf_client.chat_completion(
        messages=messages,
        max_tokens=max_tokens
    )
    return response.choices[0].message["content"]
