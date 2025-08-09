"""
Basic usage example for langchain-llm-config package
"""

import asyncio
from typing import List

from pydantic import BaseModel, Field

from langchain_llm_config import create_assistant, create_embedding_provider


# Example response model
class ArticleAnalysis(BaseModel):
    """Article analysis response model"""

    summary: str = Field(..., description="Brief summary of the article")
    keywords: List[str] = Field(..., description="Key topics and concepts")
    sentiment: str = Field(
        ..., description="Overall sentiment (positive/negative/neutral)"
    )
    word_count: int = Field(..., description="Approximate word count")


async def assistant_example() -> None:
    """Example of using the assistant"""
    print("🤖 Creating assistant...")

    # Create an assistant with structured output
    assistant = create_assistant(
        response_model=ArticleAnalysis,
        system_prompt=(
            "You are a professional article analyzer. "
            "Provide accurate and concise analysis."
        ),
        provider="openai",  # Can be "openai", "vllm", or "gemini"
    )

    # Sample article
    article = (
        "Artificial Intelligence (AI) has emerged as one of the most transformative "
        "technologies of the 21st century. From virtual assistants like Siri and Alexa "
        "to advanced machine learning algorithms that power recommendation "
        "systems, AI is reshaping how we live and work. Recent breakthroughs in large "
        "language models have demonstrated remarkable capabilities in natural language "
        "processing, enabling more sophisticated human-computer interactions. "
        "\n"
        "However, the rapid advancement of AI also raises important questions about "
        "privacy, job displacement, and ethical considerations. As AI systems become "
        "more capable, society must grapple with how to ensure these technologies "
        "benefit humanity while minimizing potential risks. The future of AI depends "
        "not just on technological innovation, but also on thoughtful governance and "
        "responsible development practices."
    )

    print("📝 Analyzing article...")
    result = await assistant.ask(f"Please analyze this article: {article}")

    print("\n📊 Analysis Results:")
    print(f"Summary: {result.summary}")
    print(f"Keywords: {', '.join(result.keywords)}")
    print(f"Sentiment: {result.sentiment}")
    print(f"Word Count: {result.word_count}")


async def embedding_example() -> None:
    """Example of using embeddings"""
    print("\n🔗 Creating embedding provider...")

    # Create an embedding provider
    embedding_provider = create_embedding_provider(provider="openai")

    # Sample texts
    texts = [
        "Artificial Intelligence is transforming the world",
        "Machine learning algorithms are becoming more sophisticated",
        "The weather is sunny today",
        "I love programming in Python",
    ]

    print("📝 Generating embeddings...")
    embeddings = await embedding_provider.embed_texts_async(texts)

    print("\n📊 Embedding Results:")
    print(f"Generated {len(embeddings)} embeddings")
    print(f"Each embedding has {len(embeddings[0])} dimensions")

    # Show similarity between first two texts (should be high)
    try:
        from numpy import dot  # type: ignore[import-not-found]
        from numpy.linalg import norm  # type: ignore[import-not-found]

        similarity = dot(embeddings[0], embeddings[1]) / (
            norm(embeddings[0]) * norm(embeddings[1])
        )
        print(f"Similarity between texts 1 and 2: {similarity:.3f}")
    except ImportError:
        print("NumPy not available - skipping similarity calculation")


async def streaming_example() -> None:
    """Example of streaming chat"""
    print("\n🌊 Creating streaming assistant...")

    from langchain_llm_config import create_assistant

    # Create an assistant instance
    assistant = create_assistant(
        provider="openai",
        system_prompt="You are a helpful assistant that provides concise answers.",
        auto_apply_parser=False,  # For streaming, we don't use structured output
    )

    print("💬 Streaming response...")
    print("Response: ", end="", flush=True)

    # Stream the response using the chat method
    async for chunk in assistant.achat("Explain quantum computing in simple terms"):
        print(chunk, end="", flush=True)

    print("\n")


async def main() -> None:
    """Main example function"""
    print("🚀 Langchain LLM Config - Basic Usage Examples")
    print("=" * 50)

    try:
        # Run examples
        await assistant_example()
        await embedding_example()
        await streaming_example()

        print("\n✅ All examples completed successfully!")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("\n💡 Make sure you have:")
        print("1. Installed the package: pip install langchain-llm-config")
        print("2. Created a config file: llm-config init")
        print("3. Set up your API keys in the config file")
        print("4. Set environment variables (e.g., OPENAI_API_KEY)")


if __name__ == "__main__":
    asyncio.run(main())
