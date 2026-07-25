#!/usr/bin/env python3
"""
Mimo AI Trains Wcore X - Meta-Learning Orchestrator Script

This script orchestrates the learning process where:
- Mimo AI (Teacher) uses a powerful LLM to evaluate and guide
- Wcore X (Student) uses a faster LLM to learn and improve

Usage:
    python scripts/mimo_trains_wcore.py

Environment Variables:
    ANTHROPIC_API_KEY: API key for Claude (Teacher)
    OPENAI_API_KEY: API key for GPT (Student)
    REDIS_URL: Redis URL for caching (optional)
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ke.meta_learning.trainer import MimoAITrainer, TrainingConfig


async def main():
    """Run the Mimo AI training session."""
    print("=" * 60)
    print("🚀 MIMO AI TRAINER - Meta-Learning System")
    print("=" * 60)
    print()
    print("This system uses Mimo AI (Teacher) to train Wcore X (Student)")
    print("on how to learn effectively from data.")
    print()

    # Check API keys
    if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: No API keys found!")
        print("Set ANTHROPIC_API_KEY or OPENAI_API_KEY to use the trainer.")
        print()
        print("Example:")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        print("  export OPENAI_API_KEY=sk-...")
        print()

    # Configure training
    config = TrainingConfig(
        # Teacher uses the most capable model
        teacher_provider="anthropic" if os.getenv("ANTHROPIC_API_KEY") else "openai",
        teacher_model=None,  # Use default for provider

        # Student uses a faster model
        student_provider="openai" if os.getenv("OPENAI_API_KEY") else "ollama",
        student_model=None,  # Use default for provider

        # Dataset configuration
        dataset_name="teknium/OpenHermes-2.5",
        max_lessons=10,  # Start small for testing
    )

    print(f"📚 Teacher: {config.teacher_provider}")
    print(f"🎓 Student: {config.student_provider}")
    print(f"📊 Dataset: {config.dataset_name}")
    print(f"📝 Max Lessons: {config.max_lessons}")
    print()

    # Create trainer
    trainer = MimoAITrainer(config)

    # Run training with progress updates
    print("Starting training...")
    print("-" * 60)

    async for event in trainer.train():
        event_type = event.get("type")
        data = event.get("data", {})

        if event_type == "start":
            print(f"🎯 Training started with {data.get('max_lessons', 0)} lessons")

        elif event_type == "lesson_start":
            lesson = data.get("lesson", 0)
            preview = data.get("material_preview", "")[:80]
            print(f"\n📖 Lesson {lesson}: {preview}...")

        elif event_type == "lesson_complete":
            lesson = data.get("lesson", 0)
            score_before = data.get("score_before", 0)
            score_after = data.get("score_after", 0)
            gain = data.get("learning_gain", 0)
            print(f"   ✅ Score: {score_before:.2f} → {score_after:.2f} (+{gain:.2f})")

        elif event_type == "progress":
            total = data.get("total_lessons", 0)
            avg_gain = data.get("average_learning_gain", 0)
            improvement = data.get("improvement_rate", 0)
            print(f"\n📊 Progress: {total} lessons, +{improvement:.1f}% improvement")

        elif event_type == "complete":
            total = data.get("total_lessons", 0)
            report = data.get("report", "")
            print("\n" + "=" * 60)
            print("✅ TRAINING COMPLETE!")
            print("=" * 60)
            print(f"\nTotal lessons completed: {total}")
            print("\nLearning Report:")
            print("-" * 60)
            print(report)

        elif event_type == "error":
            error = data.get("error", "Unknown error")
            print(f"\n❌ Error: {error}")

    print("\n" + "=" * 60)
    print("🎉 MIMO AI TRAINING SESSION ENDED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
