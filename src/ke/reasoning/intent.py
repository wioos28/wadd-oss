"""Intent Engine - Detect user intent from input."""

from __future__ import annotations

import re
from typing import Any

from ke.reasoning.models import Intent, IntentType


class IntentEngine:
    """Detect and classify user intent from natural language input."""

    # Pattern definitions for intent detection
    PATTERNS: dict[IntentType, list[str]] = {
        IntentType.QUESTION: [
            r"\b(what|how|why|when|where|who|which|can you|could you|is|are|do|does)\b.*\?",
            r"\b(explain|describe|tell me|show me|define)\b",
            r"^\w+.*\?$",
        ],
        IntentType.COMMAND: [
            r"\b(run|execute|start|stop|create|delete|update|set|get|list|show|hide|open|close|send|make)\b",
            r"\b(install|configure|enable|disable|add|remove|import|export)\b",
        ],
        IntentType.SEARCH_REQUEST: [
            r"\b(search|find|look up|query|lookup|retrieve|fetch|scan)\b",
            r"\b(where is|locate|discover)\b",
        ],
        IntentType.CODE_REQUEST: [
            r"\b(code|function|class|method|script|program|implement|write code|debug|fix code)\b",
            r"\b(python|javascript|typescript|java|go|rust|c\+\+|html|css)\b",
            r"```",
        ],
        IntentType.VISION_REQUEST: [
            r"\b(image|picture|photo|visual|diagram|chart|graph|screenshot|see|view|show image)\b",
        ],
        IntentType.OCR_REQUEST: [
            r"\b(ocr|extract text from|read text from|scan text|text recognition)\b",
        ],
        IntentType.TRAINING_REQUEST: [
            r"\b(train|teach|learn|study|practice|quiz|test me|flashcard)\b",
            r"\b(course|tutorial|lesson|exercise)\b",
        ],
        IntentType.MEMORY_REQUEST: [
            r"\b(remember|recall|memory|saved|stored|previous|last time|before)\b",
            r"\b(what did|do you remember|have I|did we)\b",
        ],
        IntentType.API_REQUEST: [
            r"\b(api|endpoint|rest|graphql|webhook|http|request|response)\b",
            r"\b(get|post|put|delete|patch)\s+(from|to)\b",
        ],
        IntentType.PLUGIN_REQUEST: [
            r"\b(plugin|extension|add-on|module|package|install)\b",
            r"\b(mcp|tool|integration)\b",
        ],
    }

    # Keyword weighting for confidence scoring
    KEYWORD_WEIGHTS: dict[str, float] = {
        "what": 0.8,
        "how": 0.9,
        "why": 0.9,
        "explain": 0.85,
        "search": 0.8,
        "find": 0.8,
        "code": 0.85,
        "function": 0.8,
        "train": 0.75,
        "remember": 0.9,
        "recall": 0.9,
        "api": 0.8,
        "plugin": 0.75,
    }

    # Specific phrase boosts for disambiguation
    PHRASE_BOOSTS: dict[IntentType, list[tuple[str, float]]] = {
        IntentType.MEMORY_REQUEST: [
            (r"\bdo you remember\b", 0.4),
            (r"\bhave I\b", 0.4),
            (r"\bdid we\b", 0.4),
            (r"\blast time\b", 0.3),
            (r"\bprevious conversation\b", 0.4),
        ],
    }

    def detect(self, text: str) -> Intent:
        """Detect intent from user input text."""
        text_lower = text.lower().strip()

        # Score each intent type
        scores: dict[IntentType, float] = {}
        detected_keywords: dict[IntentType, list[str]] = {}

        for intent_type, patterns in self.PATTERNS.items():
            score = 0.0
            keywords = []

            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                if matches:
                    # Base score for pattern match
                    score += 0.3
                    keywords.extend(matches if isinstance(matches[0], str) else [m[0] for m in matches])

            # Boost score based on keyword weights
            for keyword, weight in self.KEYWORD_WEIGHTS.items():
                if keyword in text_lower:
                    score += weight * 0.1
                    keywords.append(keyword)

            # Apply phrase boosts for specific intent types
            if intent_type in self.PHRASE_BOOSTS:
                for phrase_pattern, boost in self.PHRASE_BOOSTS[intent_type]:
                    if re.search(phrase_pattern, text_lower, re.IGNORECASE):
                        score += boost

            # Normalize
            scores[intent_type] = min(1.0, score)
            detected_keywords[intent_type] = list(set(keywords))

        # Find best intent
        if not scores or max(scores.values()) == 0:
            return Intent(
                type=IntentType.UNKNOWN,
                confidence=0.3,
                raw_input=text,
                keywords=[],
            )

        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]

        # Extract entities
        entities = self._extract_entities(text)

        return Intent(
            type=best_type,
            confidence=best_score,
            raw_input=text,
            entities=entities,
            keywords=detected_keywords.get(best_type, []),
        )

    def detect_batch(self, texts: list[str]) -> list[Intent]:
        """Detect intents for multiple inputs."""
        return [self.detect(text) for text in texts]

    def _extract_entities(self, text: str) -> dict[str, Any]:
        """Extract named entities from text."""
        entities: dict[str, Any] = {}

        # Extract file paths
        path_pattern = r"[\w/\\.-]+\.\w+"
        paths = re.findall(path_pattern, text)
        if paths:
            entities["file_paths"] = paths

        # Extract URLs
        url_pattern = r"https?://\S+"
        urls = re.findall(url_pattern, text)
        if urls:
            entities["urls"] = urls

        # Extract numbers
        num_pattern = r"\b\d+(?:\.\d+)?\b"
        numbers = re.findall(num_pattern, text)
        if numbers:
            entities["numbers"] = numbers

        # Extract quoted strings
        quote_pattern = r'"([^"]+)"'
        quoted = re.findall(quote_pattern, text)
        if quoted:
            entities["quoted_strings"] = quoted

        return entities

    def get_intent_label(self, intent: Intent) -> str:
        """Get a human-readable label for an intent."""
        labels = {
            IntentType.QUESTION: "Question",
            IntentType.COMMAND: "Command",
            IntentType.CONVERSATION: "Conversation",
            IntentType.VISION_REQUEST: "Vision Request",
            IntentType.OCR_REQUEST: "OCR Request",
            IntentType.TRAINING_REQUEST: "Training Request",
            IntentType.SEARCH_REQUEST: "Search Request",
            IntentType.CODE_REQUEST: "Code Request",
            IntentType.MEMORY_REQUEST: "Memory Request",
            IntentType.API_REQUEST: "API Request",
            IntentType.PLUGIN_REQUEST: "Plugin Request",
            IntentType.UNKNOWN: "Unknown",
        }
        return labels.get(intent.type, "Unknown")
