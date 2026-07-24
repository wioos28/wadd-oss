"""Reasoning Pipeline full usage example."""

import asyncio
from ke.reasoning import ReasoningPipeline


async def main():
    # Note: In real usage, you would initialize with actual knowledge_pipeline and embedding_model
    # pipeline = ReasoningPipeline(
    #     knowledge_pipeline=knowledge_pipeline,
    #     embedding_model=embedding_model
    # )

    # For this example, we'll show the API structure
    print("=" * 60)
    print("Reasoning Pipeline API Example")
    print("=" * 60)

    print("""
Usage:

    from ke.reasoning import ReasoningPipeline
    
    # Initialize with dependencies
    pipeline = ReasoningPipeline(
        knowledge_pipeline=knowledge_pipeline,  # Your KnowledgePipeline instance
        embedding_model=embedding_model          # Your embedding model
    )
    
    # Process a query
    result = await pipeline.process(
        query="How does authentication work in this codebase?",
        memory_entries=[...],      # Optional: from working/long-term memory
        retrieved_entries=[...]    # Optional: from retrieval pipeline
    )
    
    # Access results
    print(result.response)                    # Final reasoned response
    print(result.intent.type.value)           # Detected intent
    print(result.plan.goal)                   # Planning goal
    print(result.chain.steps)                 # Reasoning steps
    print(result.verification.is_consistent)  # Verification result
    print(result.reflection.quality_score)    # Quality assessment
    print(result.confidence.score)            # Confidence score (0.0-1.0)
    
    # Get summary
    summary = pipeline.get_summary(result)
    print(summary)
""")

    # Example: Mock pipeline usage
    print("=" * 60)
    print("Mock Pipeline Execution")
    print("=" * 60)

    # Create a mock pipeline for demonstration
    pipeline = ReasoningPipeline()

    # Process a query (without actual knowledge pipeline)
    result = await pipeline.process(
        query="What are the best practices for Python async programming?",
        memory_entries=[
            {"content": "Used asyncio in previous project", "score": 0.7}
        ],
        retrieved_entries=[
            {"content": "async/await syntax for coroutines", "score": 0.9},
            {"content": "Event loop management", "score": 0.85},
            {"content": "Task cancellation patterns", "score": 0.8},
        ],
    )

    print(f"\nQuery: {result.query}")
    print(f"Intent: {result.intent.type.value} ({result.intent.confidence:.2f})")
    print(f"Plan Steps: {len(result.plan.steps)}")
    print(f"Reasoning Steps: {len(result.chain.steps)}")
    print(f"Verification Consistent: {result.verification.is_consistent}")
    print(f"Reflection Quality: {result.reflection.quality_score:.2f}")
    print(f"Confidence: {result.confidence.score:.2f}")
    print(f"\nResponse (first 200 chars):")
    print(f"  {result.response[:200]}...")

    # Get summary
    summary = pipeline.get_summary(result)
    print(f"\nSummary:")
    print(f"  {summary[:300]}...")


if __name__ == "__main__":
    asyncio.run(main())
