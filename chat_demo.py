#!/usr/bin/env python3
"""Interactive chat demo for the Knowledge Engine."""

import sys
sys.path.insert(0, "src")

from ke.reasoning.pipeline import ReasoningPipeline
from ke.reasoning.context import ContextBuilder
from ke.memory.memory_manager import MemoryManager
from ke.memory.models import MemoryType


class ChatBot:
    def __init__(self):
        self.pipeline = ReasoningPipeline()
        self.memory = MemoryManager(project_id="chat_demo")
        self.context = ContextBuilder()
        self.context.build(query="")
        
        # Pre-load some knowledge
        self._load_knowledge()
    
    def _load_knowledge(self):
        """Load some base knowledge."""
        facts = [
            ("Python is a high-level programming language created by Guido van Rossum in 1991", ["python", "language"]),
            ("Python is known for its simple, readable syntax", ["python", "syntax"]),
            ("JavaScript is the language of the web, running in browsers and Node.js", ["javascript", "web"]),
            ("Python is widely used in data science, machine learning, and AI", ["python", "ai"]),
            ("FastAPI is a modern Python web framework for building APIs", ["python", "web", "fastapi"]),
            ("Django is a high-level Python web framework", ["python", "web", "django"]),
        ]
        
        for content, tags in facts:
            self.memory.semantic.store_fact(content, confidence=0.9, tags=tags)
    
    def chat(self, user_input: str) -> str:
        """Process user input and return response."""
        # Store user message
        self.memory.conversation.add_message("user", user_input)
        
        # Detect intent
        intent = self.pipeline.detect_intent(user_input)
        
        # Search semantic memory for relevant facts
        memories = self.memory.search(
            user_input,
            memory_types=[MemoryType.SEMANTIC, MemoryType.LONG],
            limit=3,
        )
        
        # Build context
        self.context.build(
            query=user_input,
            intent=intent,
            retrieved_entries=memories,
        )
        
        # Generate response based on intent
        response = self._generate_response(user_input, intent, memories)
        
        # Store response
        self.memory.conversation.add_message("assistant", response)
        
        # Learn from interaction
        self.memory.learn_from_interaction(user_input, response, importance=0.6)
        
        return response
    
    def _generate_response(self, query: str, intent, memories) -> str:
        """Generate a response based on intent and context."""
        query_lower = query.lower()
        
        # Handle different intents
        if intent.type.value == "memory":
            return self._handle_memory_query(query)
        
        if intent.type.value == "code":
            return self._handle_code_request(query)
        
        if intent.type.value == "search":
            return self._handle_search(query)
        
        # Default: use knowledge from memory
        if memories:
            facts = [m.content for m in memories[:2]]
            return f"Based on my knowledge:\n\n" + "\n".join(f"• {f}" for f in facts)
        
        # No knowledge found
        return f"I understand you're asking about: {query}\n\nI'm a demo chatbot with limited knowledge. Try asking about Python, JavaScript, or web frameworks!"
    
    def _handle_memory_query(self, query: str) -> str:
        """Handle memory-related queries."""
        if "what did" in query.lower() or "remember" in query.lower():
            history = self.memory.conversation.get_recent_messages(5)
            if len(history) > 1:
                return f"Yes! Earlier in our conversation:\n\n" + "\n".join(
                    f"• {m.content[:80]}..." if len(m.content) > 80 else f"• {m.content}"
                    for m in history[-3:]
                )
        
        stats = self.memory.get_stats()
        return f"I have {stats.total_entries} memories stored across {len(stats.by_type)} types."
    
    def _handle_code_request(self, query: str) -> str:
        """Handle code-related queries."""
        if "hello world" in query.lower() and "python" in query.lower():
            return '''Here's a hello world in Python:

```python
def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
```

Simple and clean - that's the Python way!'''
        
        return "I can help with code! Try asking for a specific function or language."
    
    def _handle_search(self, query: str) -> str:
        """Handle search queries."""
        results = self.memory.semantic.get_facts(min_confidence=0.7)
        if results:
            return "Here's what I found:\n\n" + "\n".join(
                f"• {r.content[:100]}" for r in results[:3]
            )
        return "No results found for your search."


def main():
    bot = ChatBot()
    
    print("=" * 50)
    print("  Knowledge Engine Chat Demo")
    print("=" * 50)
    print("Commands: 'quit' to exit, 'memory' to see stats")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "quit":
                print("\nGoodbye!")
                break
            
            if user_input.lower() == "memory":
                stats = bot.memory.get_stats()
                print(f"\nMemory Stats:")
                print(f"  Total: {stats.total_entries}")
                for t, c in stats.by_type.items():
                    if c > 0:
                        print(f"  {t}: {c}")
                continue
            
            response = bot.chat(user_input)
            print(f"\nAssistant: {response}")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            break


if __name__ == "__main__":
    main()
