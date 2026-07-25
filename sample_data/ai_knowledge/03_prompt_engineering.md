# Prompt Engineering - Complete Guide

## 1. Fundamentals

### What is Prompt Engineering?
- Designing inputs to guide LLM behavior
- Optimizing model outputs
- Maximizing task performance
- Controlling generation quality

### Key Principles
- Be specific and clear
- Provide context
- Use examples
- Iterate and refine
- Test edge cases

## 2. Prompt Techniques

### Zero-Shot Prompting
```
Classify the sentiment of this review:
"The product is amazing, I love it!"
```
- No examples provided
- Relies on pre-trained knowledge
- Simplest approach

### Few-Shot Prompting
```
Classify sentiment:

Review: "Great product!" → Positive
Review: "Terrible service." → Negative
Review: "It's okay." → Neutral

Review: "I love this!" → 
```
- Provides examples
- Improves accuracy
- More tokens used

### Chain-of-Thought (CoT)
```
Q: Roger has 5 tennis balls. He buys 2 more cans of 3. How many does he have now?

Let me think step by step:
1. Roger starts with 5 balls
2. He buys 2 cans of 3 balls each = 2 × 3 = 6 balls
3. Total = 5 + 6 = 11 balls

Answer: 11
```
- Shows reasoning process
- Improves math/logic tasks
- Reduces errors

### Zero-Shot CoT
```
Q: A farmer has 15 sheep. All but 8 die. How many are left?

Let's think step by step.
```
- No examples needed
- Triggers reasoning
- Works with "Let's think step by step"

### Self-Consistency
```
Generate 5 different reasoning paths for:
"If a train travels at 60 mph for 2.5 hours, how far does it go?"

Path 1: Distance = Speed × Time = 60 × 2.5 = 150 miles
Path 2: In 1 hour, 60 miles. In 2 hours, 120 miles. In 0.5 hours, 30 miles. Total = 150 miles
...

Answer: 150 miles (majority vote)
```
- Multiple reasoning paths
- Majority voting
- Higher accuracy

### Tree of Thoughts (ToT)
```
Problem: Write a poem about AI

Thought 1: Focus on technology aspect
  → Sub-thought 1.1: Neural networks
  → Sub-thought 1.2: Deep learning

Thought 2: Focus on human impact
  → Sub-thought 2.1: Job automation
  → Sub-thought 2.2: Healthcare advances

Best path: Combine technology and human aspects
```
- Explores multiple paths
- Backtracking capability
- Complex problem solving

## 3. Advanced Techniques

### ReAct (Reasoning + Acting)
```
Question: What is the tallest building in the country with the most people?

Thought 1: I need to find the country with the most people first.
Action 1: search("country with most population")
Observation 1: China has the most population.

Thought 2: Now I need to find the tallest building in China.
Action 2: search("tallest building in China")
Observation 2: Shanghai Tower is the tallest building in China.

Answer: Shanghai Tower
```
- Combines reasoning with actions
- Uses external tools
- Iterative problem solving

### Reflexion
```
Task: Write a function to find prime numbers

Attempt 1: [code]
Evaluation: Misses edge case for n=2
Reflection: Need to handle n=2 separately

Attempt 2: [improved code]
Evaluation: All test cases pass
```
- Self-reflection
- Learning from mistakes
- Iterative improvement

### Constitutional AI
```
Prompt: Generate a helpful response

Constitutional Principle 1: Is it helpful?
→ Review and revise

Constitutional Principle 2: Is it harmless?
→ Review and revise

Constitutional Principle 3: Is it honest?
→ Final revision
```
- AI self-correction
- Principle-based
- Reduces harmful outputs

## 4. Prompt Templates

### Classification Template
```
You are a text classifier. Classify the following text into one of these categories:
{categories}

Text: {text}

Category:
```

### Summarization Template
```
Summarize the following text in {length} sentences:

Text: {text}

Summary:
```

### Code Generation Template
```
Write a {language} function that {description}.

Requirements:
- Input: {input_description}
- Output: {output_description}
- Constraints: {constraints}

Function:
```

### Analysis Template
```
Analyze the following {data_type}:

{data}

Provide:
1. Key insights
2. Trends
3. Recommendations

Analysis:
```

## 5. Prompt Optimization

### A/B Testing
- Test multiple prompt versions
- Measure performance metrics
- Statistical significance
- Iterate on winners

### Prompt Chaining
```
Step 1: Extract key information
Step 2: Analyze relationships
Step 3: Generate insights
Step 4: Create recommendations
```
- Break complex tasks
- Improve reliability
- Easier debugging

### Dynamic Prompting
```python
def create_prompt(context, task, examples=None):
    prompt = f"Context: {context}\n\n"
    prompt += f"Task: {task}\n\n"
    if examples:
        prompt += "Examples:\n"
        for ex in examples:
            prompt += f"- {ex}\n"
    return prompt
```

## 6. Common Pitfalls

### Avoid
- Vague instructions
- Too many constraints
- Conflicting requirements
- Ambiguous language
- Missing context

### Best Practices
- Start simple
- Iterate incrementally
- Test edge cases
- Document prompts
- Version control

## 7. Domain-Specific Prompts

### Medical
```
As a medical AI assistant, provide information about:
- Condition: {condition}
- Symptoms: {symptoms}
- Treatment options

Disclaimer: This is for informational purposes only.
```

### Legal
```
Analyze the following legal document:
{document}

Extract:
1. Key terms
2. Obligations
3. Rights
4. Risks
```

### Financial
```
Analyze the financial data:
{data}

Provide:
1. Key metrics
2. Trends
3. Risks
4. Recommendations
```

## 8. Evaluation Metrics

### Quality Metrics
- Accuracy
- Relevance
- Coherence
- Fluency
- Completeness

### Efficiency Metrics
- Token usage
- Response time
- Cost per query

### Safety Metrics
- Harmlessness
- Truthfulness
- Fairness
- Bias detection
