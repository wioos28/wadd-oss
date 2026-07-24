"""Example learning session - Learn Python and FastAPI basics."""

from ke.learning import LearningManager
from ke.learning.models import Difficulty


def main():
    # Initialize learning manager
    manager = LearningManager()

    # Start learning session
    print("=" * 60)
    print("Starting Learning Session")
    print("=" * 60)

    report = manager.start_session()

    # Learn Python basics
    print("\n[1/3] Learning Python Basics...")
    python_entries = manager.learn_python_basics()
    print(f"  Created {len(python_entries)} entries")

    # Learn FastAPI basics
    print("\n[2/3] Learning FastAPI Basics...")
    fastapi_entries = manager.learn_fastapi_basics()
    print(f"  Created {len(fastapi_entries)} entries")

    # Learn from error
    print("\n[3/3] Learning from Errors...")
    error_entry = manager.learn_error(
        error_message="TypeError: can't compare offset-naive and offset-aware datetimes",
        solution="Use datetime.now(tz=UTC) instead of datetime.utcnow()",
        context="Python 3.12 deprecates datetime.utcnow()",
    )
    print(f"  Created error entry: {error_entry.title}")

    # Learn best practices
    print("\n[+] Learning Best Practices...")
    bp_entry = manager.learn_best_practice(
        topic="Python Type Hints",
        practice="Always use type hints for function parameters and return values",
        reason="Improves code readability, enables IDE support, catches errors early",
        examples=[
            "def greet(name: str) -> str: ...",
            "def process(items: list[int]) -> dict[str, int]: ...",
        ],
    )
    print(f"  Created best practice: {bp_entry.title}")

    # End session
    report = manager.end_session()

    # Print report
    print("\n" + "=" * 60)
    print("Learning Report")
    print("=" * 60)
    print(f"Topics Learned: {report.topics_learned}")
    print(f"Entries Created: {report.entries_created}")
    print(f"Examples Generated: {report.examples_generated}")
    print(f"Errors Learned: {report.errors_learned}")
    print(f"Knowledge Score: {report.knowledge_score:.2f}")

    # Show all entries
    print("\n" + "=" * 60)
    print("Knowledge Base Entries")
    print("=" * 60)
    for entry in manager.pipeline.get_all():
        print(f"\n  [{entry.difficulty.value}] {entry.title}")
        print(f"    Summary: {entry.summary[:80]}...")
        print(f"    Tags: {entry.tags}")
        print(f"    Confidence: {entry.confidence:.2f}")

    # Show stats
    stats = manager.get_stats()
    print("\n" + "=" * 60)
    print("Statistics")
    print("=" * 60)
    print(f"Total Entries: {stats['total_entries']}")
    print(f"Topics: {stats['topics_learned']}")
    print(f"Avg Confidence: {stats['avg_confidence']:.2f}")


if __name__ == "__main__":
    main()
