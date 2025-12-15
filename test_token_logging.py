"""Test script to demonstrate token usage logging."""
import asyncio
import logging
from app.services.llm_service import LLMService
from app.schemas.chat import ChatRequest, ChatMessage
from app.core.logging import setup_logging

# Setup logging to see token usage
setup_logging(level="INFO")

async def test_token_logging():
    """Test token usage logging with a simple chat request."""
    service = LLMService()

    # Create a simple chat request
    request = ChatRequest(
        messages=[
            ChatMessage(role="user", content="What is 2+2?")
        ],
        provider="ollama",  # Use ollama as it doesn't require API key
        model="gemma3:4b",
        temperature=0.7
    )

    try:
        print("\n" + "="*80)
        print("Testing token usage logging...")
        print("="*80 + "\n")

        response = await service.chat(request)

        print("\n" + "="*80)
        print("Response received:")
        print(f"Success: {response.success}")
        print(f"Message: {response.message.content}")
        print(f"Provider: {response.provider}")
        print(f"Model: {response.model}")
        print(f"\nToken Usage:")
        print(f"  Prompt tokens: {response.usage.get('prompt_tokens', 0)}")
        print(f"  Completion tokens: {response.usage.get('completion_tokens', 0)}")
        print(f"  Total tokens: {response.usage.get('total_tokens', 0)}")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\nError: {e}")
        print("Note: This test requires Ollama to be running locally.")
        print("Check the logs above to see token usage logging structure.")

if __name__ == "__main__":
    asyncio.run(test_token_logging())

