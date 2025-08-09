"""
Example demonstrating dynamic parser application with auto_apply_parser=False
"""

from typing import List

from pydantic import BaseModel, Field

from langchain_llm_config import create_assistant


# Define response models
class SimpleResponse(BaseModel):
    message: str = Field(..., description="Simple response message")


class DetailedResponse(BaseModel):
    summary: str = Field(..., description="Summary of the response")
    keywords: List[str] = Field(..., description="Key topics")
    confidence: float = Field(default=0.8, description="Confidence score")


def main() -> None:
    print("=== Dynamic Parser Application Example ===\n")

    # 1. Create assistant without response model for raw text output
    print("1. Creating assistant without response model (raw text mode)...")
    assistant = create_assistant(
        response_model=None,  # No response model
        auto_apply_parser=False,  # Don't apply parser
        provider="openai",  # or "vllm", "gemini"
        system_prompt="You are a helpful assistant.",
    )

    print("✓ Assistant created in raw text mode")
    print(f"   - response_model: {assistant.response_model}")
    print(f"   - parser: {assistant.parser}")
    print(f"   - chain == base_chain: {assistant.chain == assistant.base_chain}")

    # 2. Use assistant for raw text output
    print("\n2. Using assistant for raw text output...")
    try:
        # This would work in a real environment with actual LLM
        # response = assistant.ask("What is the capital of France?")
        # print(f"Raw response: {response}")
        print(
            "   (Would return raw text response: "
            "{'content': 'The capital of France is Paris.'})"
        )
    except Exception as e:
        print(f"   Note: {e} (Expected in test environment)")

    # 3. Apply parser with simple response model
    print("\n3. Applying parser with SimpleResponse model...")
    assistant.apply_parser(response_model=SimpleResponse)

    print("✓ Parser applied with SimpleResponse")
    print(f"   - response_model: {assistant.response_model}")
    print(f"   - parser: {assistant.parser is not None}")
    print(f"   - chain == base_chain: {assistant.chain == assistant.base_chain}")

    # 4. Use assistant for structured output
    print("\n4. Using assistant for structured output...")
    try:
        # This would work in a real environment with actual LLM
        # response = assistant.ask("What is the capital of France?")
        # print(f"Structured response: {response}")
        print(
            "   (Would return structured response: "
            "{'message': 'The capital of France is Paris.'})"
        )
    except Exception as e:
        print(f"   Note: {e} (Expected in test environment)")

    # 5. Change to a different response model
    print("\n5. Changing to DetailedResponse model...")
    assistant.apply_parser(response_model=DetailedResponse)

    print("✓ Parser updated with DetailedResponse")
    print(f"   - response_model: {assistant.response_model}")
    print(f"   - parser: {assistant.parser is not None}")

    # 6. Demonstrate error handling
    print("\n6. Demonstrating error handling...")

    # Create assistant without model and try to apply parser without providing one
    assistant_no_model = create_assistant(
        response_model=None,
        auto_apply_parser=False,
        provider="openai",
    )

    try:
        assistant_no_model.apply_parser()  # No response_model provided
    except ValueError as e:
        print(f"✓ Expected error: {e}")

    # Try to create assistant with auto_apply_parser=True but no response_model
    try:
        create_assistant(
            response_model=None,
            auto_apply_parser=True,  # This should fail
            provider="openai",
        )
    except ValueError as e:
        print(f"✓ Expected error: {e}")

    print("\n=== Example completed successfully! ===")


if __name__ == "__main__":
    main()
