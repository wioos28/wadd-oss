"""Learning manager - Orchestrate learning sessions."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from ke.learning.models import (
    Difficulty,
    KnowledgeEntry,
    LearningConfig,
    LearningReport,
    LearningSource,
    SourceType,
)
from ke.learning.pipeline import LearningPipeline


class LearningManager:
    """Manage learning sessions and knowledge acquisition."""

    def __init__(self, config: LearningConfig | None = None):
        self.config = config or LearningConfig()
        self.pipeline = LearningPipeline()
        self._reports: list[LearningReport] = []
        self._current_report: LearningReport | None = None

    def start_session(self) -> LearningReport:
        """Start a new learning session."""
        self._current_report = LearningReport()
        return self._current_report

    def end_session(self) -> LearningReport:
        """End current learning session and generate report."""
        if self._current_report:
            self._current_report.completed_at = datetime.now(tz=UTC)
            self._reports.append(self._current_report)
            report = self._current_report
            self._current_report = None
            return report
        return LearningReport()

    def learn_topic(
        self,
        topic: str,
        content: str,
        source_url: str = "",
        difficulty: Difficulty = Difficulty.BEGINNER,
    ) -> KnowledgeEntry:
        """Learn a topic from documentation."""
        source = LearningSource(
            type=SourceType.DOCUMENTATION,
            url=source_url,
            title=topic,
        )

        entry = self.pipeline.learn_from_text(
            content=content,
            source=source,
            topic=topic,
            difficulty=difficulty,
        )

        if self._current_report:
            self._current_report.entries_created += 1
            if topic not in self._current_report.topics_learned:
                self._current_report.topics_learned.append(topic)

        return entry

    def learn_from_github(
        self,
        repo_url: str,
        content: str,
        filename: str = "",
    ) -> KnowledgeEntry:
        """Learn from GitHub repository."""
        source = LearningSource(
            type=SourceType.GITHUB,
            url=repo_url,
            title=filename or "GitHub Code",
        )

        # Determine language from filename
        language = "python"
        if filename.endswith((".js", ".jsx")):
            language = "javascript"
        elif filename.endswith((".ts", ".tsx")):
            language = "typescript"
        elif filename.endswith(".go"):
            language = "go"
        elif filename.endswith(".rs"):
            language = "rust"

        entry = self.pipeline.learn_from_code(
            code=content,
            language=language,
            source=source,
            filename=filename,
        )

        if self._current_report:
            self._current_report.entries_created += 1

        return entry

    def learn_error(
        self,
        error_message: str,
        solution: str,
        context: str = "",
    ) -> KnowledgeEntry:
        """Learn from an error."""
        entry = self.pipeline.learn_from_error(
            error_message=error_message,
            solution=solution,
            context=context,
        )

        if self._current_report:
            self._current_report.errors_learned += 1
            self._current_report.entries_created += 1

        return entry

    def learn_best_practice(
        self,
        topic: str,
        practice: str,
        reason: str,
        examples: list[str] | None = None,
    ) -> KnowledgeEntry:
        """Learn a best practice."""
        entry = self.pipeline.learn_best_practice(
            topic=topic,
            practice=practice,
            reason=reason,
            examples=examples,
        )

        if self._current_report:
            self._current_report.entries_created += 1

        return entry

    def learn_python_basics(self) -> list[KnowledgeEntry]:
        """Learn Python basics."""
        entries = []

        # Python Basics
        entries.append(self.learn_topic(
            topic="Python Variables",
            content="""
# Python Variables

Variables are containers for storing data values.

## Creating Variables
```python
x = 5
y = "Hello"
z = 3.14
```

## Variable Naming Rules
- Must start with a letter or underscore
- Can contain letters, numbers, underscores
- Case-sensitive
- Cannot be a reserved keyword

## Best Practices
- Use snake_case for variables
- Use descriptive names
- Avoid single letters except for loops
- Use UPPER_CASE for constants

## Common Mistakes
- Using reserved words as variable names
- Not initializing variables before use
- Mixing up = (assignment) and == (comparison)
""",
            difficulty=Difficulty.BEGINNER,
        ))

        entries.append(self.learn_topic(
            topic="Python Functions",
            content="""
# Python Functions

Functions are reusable blocks of code.

## Defining Functions
```python
def greet(name):
    return f"Hello, {name}!"
```

## Function Parameters
- Positional arguments
- Keyword arguments
- Default values
- *args and **kwargs

## Best Practices
- Keep functions small and focused
- Use docstrings
- Return values, don't print
- Use type hints

## Common Mistakes
- Not handling edge cases
- Too many parameters
- Side effects in pure functions
""",
            difficulty=Difficulty.BEGINNER,
        ))

        entries.append(self.learn_topic(
            topic="Python Classes",
            content="""
# Python Classes

Classes are blueprints for creating objects.

## Defining Classes
```python
class Dog:
    def __init__(self, name):
        self.name = name
    
    def bark(self):
        return "Woof!"
```

## OOP Concepts
- Encapsulation
- Inheritance
- Polymorphism
- Abstraction

## Best Practices
- Use composition over inheritance
- Keep classes small
- Use dataclasses for data containers
- Follow SOLID principles

## Common Mistakes
- Mutable default arguments
- Not calling super().__init__()
- Overusing inheritance
""",
            difficulty=Difficulty.INTERMEDIATE,
        ))

        return entries

    def learn_fastapi_basics(self) -> list[KnowledgeEntry]:
        """Learn FastAPI basics."""
        entries = []

        entries.append(self.learn_topic(
            topic="FastAPI Introduction",
            content="""
# FastAPI Introduction

FastAPI is a modern, fast web framework for building APIs with Python.

## Installation
```bash
pip install fastapi uvicorn
```

## Basic App
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
```

## Running
```bash
uvicorn main:app --reload
```

## Best Practices
- Use async/await for I/O operations
- Use dependency injection
- Use Pydantic models for validation
- Use proper HTTP status codes

## Common Mistakes
- Not using async for I/O
- Ignoring error handling
- Not validating input
""",
            difficulty=Difficulty.BEGINNER,
        ))

        entries.append(self.learn_topic(
            topic="FastAPI Path Parameters",
            content="""
# FastAPI Path Parameters

Path parameters are part of the URL path.

## Basic Usage
```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```

## Type Conversion
FastAPI automatically converts path parameters to Python types.

## Validation
```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

@app.post("/users")
def create_user(user: User):
    return user
```

## Best Practices
- Use proper type hints
- Validate with Pydantic
- Use meaningful parameter names
- Handle not found cases

## Common Mistakes
- Not validating path parameters
- Ignoring type conversion errors
- Not returning proper status codes
""",
            difficulty=Difficulty.BEGINNER,
        ))

        return entries

    def get_reports(self) -> list[LearningReport]:
        """Get all learning reports."""
        return self._reports

    def get_stats(self) -> dict[str, Any]:
        """Get learning statistics."""
        entries = self.pipeline.get_all()

        return {
            "total_entries": len(entries),
            "total_reports": len(self._reports),
            "topics_learned": list(set(tag for e in entries for tag in e.tags)),
            "avg_confidence": sum(e.confidence for e in entries) / max(len(entries), 1),
            "categories": list(set(e.category.value for e in entries)),
        }
