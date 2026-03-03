"""
OpenRouter API integration for AI chat.
"""
import os
import json
import httpx


async def call_openrouter(prompt: str, conversation_history: list[dict] | None = None) -> str:
    """
    Call OpenRouter API with the given prompt and optional conversation history.
    
    Args:
        prompt: The user's message to send to the AI
        conversation_history: Optional list of {role, content} messages for context
        
    Returns:
        The AI's response text
        
    Raises:
        ValueError: If API key is not set
        httpx.HTTPError: If the API call fails
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")
    
    # Build message list: use conversation history if provided, otherwise just the prompt
    messages = conversation_history or []
    if not messages or messages[-1]["role"] != "user":
        messages = [*messages, {"role": "user", "content": prompt}]
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "http://localhost:8000",  # Identification
                "X-Title": "Kanban Studio",
            },
            json={
                "model": "openai/gpt-oss-120b",
                "messages": messages,
                "temperature": 0.7,
            },
        )
        response.raise_for_status()
        data = response.json()
        
        # Extract the assistant's response
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        else:
            raise ValueError(f"Unexpected OpenRouter response structure: {data}")
