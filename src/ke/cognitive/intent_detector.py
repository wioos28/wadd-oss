"""Intent Detection - Understand user intent from messages."""

from __future__ import annotations

import re
from enum import Enum
from dataclasses import dataclass, field


class IntentType(str, Enum):
    """Types of user intents."""
    QUESTION = "question"
    COMMAND = "command"
    SEARCH_REQUEST = "search"
    CODE_REQUEST = "code"
    MEMORY_REQUEST = "memory"
    CONVERSATION = "conversation"
    UNKNOWN = "unknown"


@dataclass
class Intent:
    """Detected intent with metadata."""
    type: IntentType
    confidence: float
    entities: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)


class IntentDetector:
    """
    Detects user intent from messages using pattern matching.

    Intent Types:
    - QUESTION: User is asking a question
    - COMMAND: User wants to execute an action
    - SEARCH_REQUEST: User wants to search for something
    - CODE_REQUEST: User wants code-related help
    - MEMORY_REQUEST: User wants to recall something
    - CONVERSATION: Casual conversation
    """

    # Pattern definitions
    PATTERNS = {
        IntentType.QUESTION: [
            r'\b(how|what|why|when|where|who|which|can you|could you|tell me|explain)\b',
            r'\?$',
            r'\b(is|are|was|were|do|does|did)\b.*\?',
        ],
        IntentType.COMMAND: [
            r'\b(run|execute|start|stop|create|delete|update|add|remove|show|list|set)\b',
            r'\b(please|help me|I want to|I need to)\b',
        ],
        IntentType.SEARCH_REQUEST: [
            r'\b(search|find|look for|locate|search for|query)\b',
            r'\b(where|what).*(located|stored|found)\b',
        ],
        IntentType.CODE_REQUEST: [
            r'\b(code|function|class|method|implement|write|debug|fix|error)\b',
            r'\b(python|javascript|typescript|java|cpp|rust|go|swift)\b',
            r'\b(import|export|def|class|function|const|let|var)\b',
        ],
        IntentType.MEMORY_REQUEST: [
            r'\b(remember|recall|memory|what did|previous|last time|before)\b',
            r'\b(did I|have I|was there)\b',
        ],
        IntentType.CONVERSATION: [
            r'\b(hi|hello|hey|thanks|thank you|ok|okay|yes|no|good|great)\b',
            r'^(hi|hello|hey|sup|yo)\b',
        ],
    }

    # Entity extraction patterns
    ENTITY_PATTERNS = {
        'file_path': r'[\/\\]?[\w\/\\.-]+\.\w+',
        'url': r'https?://[^\s]+',
        'email': r'[\w.-]+@[\w.-]+\.\w+',
        'number': r'\b\d+(\.\d+)?\b',
        'quoted': r'"([^"]+)"',
    }

    def detect(self, message: str) -> Intent:
        """
        Detect intent from a message.

        Args:
            message: User message

        Returns:
            Intent with type, confidence, and entities
        """
        message_lower = message.lower().strip()

        # Calculate scores for each intent type
        scores = {}
        for intent_type, patterns in self.PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    score += 1
            scores[intent_type] = score

        # Get the highest scoring intent
        if not scores or max(scores.values()) == 0:
            return Intent(
                type=IntentType.CONVERSATION,
                confidence=0.5,
                entities=self._extract_entities(message),
                keywords=self._extract_keywords(message),
            )

        best_intent = max(scores, key=scores.get)
        confidence = min(0.9, scores[best_intent] / 3)  # Normalize confidence

        return Intent(
            type=best_intent,
            confidence=confidence,
            entities=self._extract_entities(message),
            keywords=self._extract_keywords(message),
        )

    def _extract_entities(self, message: str) -> list[str]:
        """Extract entities from the message."""
        entities = []

        for entity_type, pattern in self.ENTITY_PATTERNS.items():
            matches = re.findall(pattern, message)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                entities.append(match)

        return list(set(entities))

    def _extract_keywords(self, message: str) -> list[str]:
        """Extract important keywords from the message."""
        # Common stop words
        stop_words = {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
            'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him',
            'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its',
            'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what',
            'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
            'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the',
            'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while',
            'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
            'through', 'during', 'before', 'after', 'above', 'below', 'to',
            'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under',
            'again', 'further', 'then', 'once', 'here', 'there', 'when',
            'where', 'why', 'how', 'all', 'both', 'each', 'few', 'more',
            'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can',
            'will', 'just', 'don', 'should', 'now',
        }

        words = re.findall(r'\b\w+\b', message.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]

        return list(set(keywords))[:10]  # Return top 10 unique keywords
