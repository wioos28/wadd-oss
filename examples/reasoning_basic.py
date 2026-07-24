"""Basic Reasoning Engine usage example."""

import asyncio
from ke.reasoning import (
    IntentEngine,
    TaskPlanner,
    Reasoner,
    Verifier,
    Reflector,
    ConfidenceScorer,
    ContextBuilder,
    PromptBuilder,
    ReasoningPipeline,
    ReasoningResult,
    IntentType,
)


async def main():
    # Initialize components
    intent_engine = IntentEngine()
    planner = TaskPlanner()
    reasoner = Reasoner()
    verifier = Verifier()
    reflector = Reflector()
    confidence_scorer = ConfidenceScorer()
    context_builder = ContextBuilder()
    prompt_builder = PromptBuilder()

    # Example 1: Intent Detection
    print("=" * 60)
    print("1. Intent Detection")
    print("=" * 60)

    queries = [
        "How does authentication work?",
        "Create a new Python script",
        "Search for machine learning papers",
        "What is the difference between REST and GraphQL?",
    ]

    for query in queries:
        intent = intent_engine.detect(query)
        print(f"\nQuery: {query}")
        print(f"  Intent: {intent.type.value}")
        print(f"  Confidence: {intent.confidence:.2f}")
        print(f"  Entities: {intent.entities}")

    # Example 2: Planning
    print("\n" + "=" * 60)
    print("2. Task Planning")
    print("=" * 60)

    intent = intent_engine.detect("How does authentication work in this codebase?")
    plan = planner.create_plan(intent, "Explain authentication implementation")

    print(f"\nGoal: {plan.goal}")
    print(f"Steps ({len(plan.steps)}):")
    for i, step in enumerate(plan.steps):
        print(f"  {i + 1}. {step.description} [{step.status}]")

    # Example 3: Context Building
    print("\n" + "=" * 60)
    print("3. Context Building")
    print("=" * 60)

    context = context_builder.build(
        query="How does authentication work?",
        intent=intent,
        retrieved_entries=[
            {"content": "JWT tokens used for auth", "score": 0.9},
            {"content": "Password hashing with bcrypt", "score": 0.85},
        ],
        memory_entries=[
            {"content": "Previously implemented OAuth2", "score": 0.8},
        ],
    )

    print(f"\nQuery: {context.user_query}")
    print(f"Intent: {context.intent.type.value}")
    print(f"Retrieved entries: {len(context.retrieved_entries)}")
    print(f"Memory entries: {len(context.memory_entries)}")

    # Get context summary
    summary = context_builder.get_summary()
    print(f"Summary: {summary}")

    # Example 4: Prompt Building
    print("\n" + "=" * 60)
    print("4. Prompt Building")
    print("=" * 60)

    prompt = prompt_builder.build_reasoning_prompt(context, plan)
    print(f"\nReasoning Prompt (first 300 chars):")
    print(f"  {prompt[:300]}...")

    # Example 5: Reasoning
    print("\n" + "=" * 60)
    print("5. Reasoning")
    print("=" * 60)

    chain = reasoner.reason(context, plan)
    print(f"\nReasoning Chain:")
    print(f"  Steps: {len(chain.steps)}")
    print(f"  Conclusion: {chain.conclusion[:200]}...")
    print(f"  Confidence: {chain.confidence:.2f}")
    print(f"  Sources: {len(chain.sources)}")

    # Example 6: Verification
    print("\n" + "=" * 60)
    print("6. Verification")
    print("=" * 60)

    verification = verifier.verify(
        chain,
        "How does authentication work?",
        chain.conclusion
    )

    print(f"\nIs Consistent: {verification.is_consistent}")
    print(f"Logical Errors: {len(verification.logical_errors)}")
    print(f"Conflicting Facts: {len(verification.conflicting_facts)}")
    print(f"Missing Info: {len(verification.missing_info)}")
    print(f"Duplicates: {len(verification.duplicate_facts)}")
    print(f"Confidence Adjustment: {verification.confidence_adjustment:.2f}")
    print(f"Recommendations: {verification.recommendations}")

    # Example 7: Confidence Scoring
    print("\n" + "=" * 60)
    print("7. Confidence Scoring")
    print("=" * 60)

    confidence = confidence_scorer.calculate(
        chain,
        retrieval_score=0.9,
        knowledge_quality=0.85,
    )

    print(f"\nOverall Confidence: {confidence.overall:.2f}")
    print(f"  Knowledge Quality: {confidence.knowledge_quality:.2f}")
    print(f"  Retrieval Score: {confidence.retrieval_score:.2f}")
    print(f"  Evidence Count: {confidence.evidence_count:.2f}")
    print(f"  Reasoning Quality: {confidence.reasoning_quality:.2f}")
    print(f"  Factors: {confidence.factors}")

    # Example 8: Full Pipeline
    print("\n" + "=" * 60)
    print("8. Full Pipeline")
    print("=" * 60)

    pipeline = ReasoningPipeline()
    result = pipeline.reason(
        "What are the best practices for Python async programming?",
        conversation_history=[
            {"role": "user", "content": "Tell me about async"},
            {"role": "assistant", "content": "Async is great for I/O bound tasks"},
        ],
    )

    print(f"\nQuery: {result.query}")
    print(f"Answer: {result.answer[:200]}...")
    print(f"Confidence: {result.confidence.overall:.2f}")
    print(f"Processing Time: {result.processing_time_ms:.2f}ms")
    print(f"Sources Used: {len(result.sources_used)}")

    if result.reflection:
        print(f"\nReflection:")
        print(f"  Quality Score: {result.reflection.answer_quality:.2f}")
        print(f"  Lessons Learned: {result.reflection.lessons_learned}")
        print(f"  Reusable Knowledge: {result.reflection.reusable_knowledge}")


if __name__ == "__main__":
    asyncio.run(main())
