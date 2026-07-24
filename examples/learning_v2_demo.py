"""WCore X V2 - Autonomous Learning System Demo."""

from ke.learning.v2 import KnowledgeGraph, SelfLearner, DreamMode
from ke.learning.v2.models import RelationType


def main():
    print("=" * 70)
    print("WCORE X - AUTONOMOUS LEARNING SYSTEM V2")
    print("=" * 70)

    # Initialize components
    graph = KnowledgeGraph()
    learner = SelfLearner()
    dream = DreamMode(graph)

    # ==================== PHASE 1: Knowledge Graph ====================
    print("\n" + "=" * 70)
    print("PHASE 1: Building Knowledge Graph")
    print("=" * 70)

    # Add Python concepts
    python = graph.add_node(
        concept="Python",
        definition="A high-level programming language",
        summary="Python is versatile, easy to learn, and widely used",
    )

    fastapi = graph.add_node(
        concept="FastAPI",
        definition="Modern web framework for Python",
        summary="Fast, async, automatic API docs",
        parent_id=python.id,
    )

    pydantic = graph.add_node(
        concept="Pydantic",
        definition="Data validation library for Python",
        summary="Uses Python type hints for validation",
        parent_id=python.id,
    )

    # Add relations
    graph.add_relation(fastapi.id, pydantic.id, RelationType.DEPENDS_ON)
    graph.add_relation(python.id, fastapi.id, RelationType.CHILD)

    # Add Docker concepts
    docker = graph.add_node(
        concept="Docker",
        definition="Container platform for applications",
        summary="Package apps with dependencies",
    )

    kubernetes = graph.add_node(
        concept="Kubernetes",
        definition="Container orchestration platform",
        summary="Manage containers at scale",
    )

    graph.add_relation(kubernetes.id, docker.id, RelationType.DEPENDS_ON)

    # Add database concepts
    postgres = graph.add_node(
        concept="PostgreSQL",
        definition="Advanced open-source SQL database",
        summary="Robust, extensible, ACID compliant",
    )

    sql = graph.add_node(
        concept="SQL",
        definition="Structured Query Language",
        summary="Standard language for databases",
        parent_id=postgres.id,
    )

    # Show graph stats
    stats = graph.get_stats()
    print(f"\nKnowledge Graph Stats:")
    print(f"  Nodes: {stats['total_nodes']}")
    print(f"  Relations: {stats['total_relations']}")
    print(f"  Avg Confidence: {stats['avg_confidence']:.2f}")

    # Show Mermaid diagram
    print("\nKnowledge Graph (Mermaid):")
    print(graph.to_mermaid())

    # ==================== PHASE 2: Self Learning ====================
    print("\n" + "=" * 70)
    print("PHASE 2: Self Learning")
    print("=" * 70)

    # Generate questions about FastAPI
    questions = learner.generate_questions(
        topic="FastAPI",
        content="FastAPI is a modern web framework for building APIs with Python",
        count=20,
    )

    print(f"\nGenerated {len(questions)} questions about FastAPI:")
    for i, q in enumerate(questions[:5], 1):
        print(f"  {i}. [{q['type']}] {q['question']}")

    # Create self-exam
    print("\nCreating self-exam...")
    exam = learner.create_exam(
        topic="FastAPI",
        content="FastAPI content",
        question_count=50,
    )
    print(f"  Questions: {len(exam.questions)}")

    # Simulate taking exam (answer all correctly)
    answers = [q.get("correct", 0) for q in exam.questions]
    exam = learner.grade_exam(exam, answers)
    print(f"  Score: {exam.score:.1f}%")
    print(f"  Passed: {exam.passed}")

    # Learn from error
    print("\nLearning from error...")
    error = learner.learn_error(
        error="ImportError: cannot import name 'FastAPI' from 'fastapi'",
        root_cause="FastAPI not installed",
        fix="pip install fastapi",
        lessons=["Always check dependencies", "Use virtual environments"],
        prevention=["Add to requirements.txt", "Use pyproject.toml"],
    )
    print(f"  Error: {error.error[:50]}...")
    print(f"  Fix: {error.fix}")

    # Update learning scores
    print("\nUpdating learning scores...")
    learner.update_learning_score(
        topic="Python",
        score_delta=5.0,
        entries_learned=3,
        tests_passed=1,
    )
    learner.update_learning_score(
        topic="FastAPI",
        score_delta=3.0,
        entries_learned=2,
        exercises_completed=5,
    )

    scores = learner.get_learning_scores()
    print("\nLearning Scores:")
    for topic, score in scores.items():
        print(f"  {topic}: {score.score:.1f}% ({score.level})")

    # ==================== PHASE 3: Self Reflection ====================
    print("\n" + "=" * 70)
    print("PHASE 3: Self Reflection")
    print("=" * 70)

    reflection = learner.reflect(
        topic="Python",
        weak_areas=["async programming", "type hints", "decorators"],
        reasons=["Complex syntax", "Limited practice"],
    )

    print(f"\nWeak Areas: {reflection.weak_areas}")
    print(f"Study Plan:")
    for action in reflection.study_plan[:5]:
        print(f"  - {action}")

    # ==================== PHASE 4: Dream Mode ====================
    print("\n" + "=" * 70)
    print("PHASE 4: Dream Mode (Idle Learning)")
    print("=" * 70)

    report = dream.run_dream_session()

    print(f"\nDream Session Report:")
    print(f"  Activities: {len(report.activities)}")
    for activity in report.activities:
        print(f"    - {activity}")
    print(f"  New Knowledge: {report.new_knowledge}")
    print(f"  Duplicates Merged: {report.removed_duplicates}")
    print(f"  Contradictions: {report.contradictions_found}")
    print(f"  Next Actions:")
    for action in report.next_actions:
        print(f"    - {action}")

    # ==================== PHASE 5: Final Report ====================
    print("\n" + "=" * 70)
    print("FINAL REPORT")
    print("=" * 70)

    graph_stats = graph.get_stats()
    dream_stats = dream.get_stats()
    weak_areas = learner.get_weak_areas()

    print(f"\nKnowledge Graph:")
    print(f"  Nodes: {graph_stats['total_nodes']}")
    print(f"  Relations: {graph_stats['total_relations']}")

    print(f"\nLearning Progress:")
    for topic, score in scores.items():
        bar = "█" * int(score.score / 5) + "░" * (20 - int(score.score / 5))
        print(f"  {topic:15} [{bar}] {score.score:.1f}%")

    print(f"\nWeak Areas: {weak_areas if weak_areas else 'None'}")
    print(f"\nError Memory: {len(learner.get_error_memory())} errors learned")
    print(f"Reflections: {len(learner.get_reflections())}")

    print("\n" + "=" * 70)
    print("WCORE X V2 - Learning Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
