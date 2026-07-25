# Key AI Research Papers - Summary Guide

## 1. Foundational Papers

### Attention Is All You Need (2017)
- **Authors**: Vaswani et al.
- **Contribution**: Transformer architecture
- **Key Ideas**:
  - Self-attention mechanism
  - Multi-head attention
  - Positional encoding
  - Encoder-decoder structure
- **Impact**: Foundation for all modern LLMs

### BERT (2018)
- **Authors**: Devlin et al.
- **Contribution**: Bidirectional pre-training
- **Key Ideas**:
  - Masked Language Modeling (MLM)
  - Next Sentence Prediction (NSP)
  - Fine-tuning paradigm
- **Impact**: Revolutionized NLP tasks

### GPT-2 (2019)
- **Authors**: Radford et al.
- **Contribution**: Large-scale language modeling
- **Key Ideas**:
  - Zero-shot learning
  - Unsupervised multitask learning
  - Quality filtering
- **Impact**: Showed scaling benefits

### GPT-3 (2020)
- **Authors**: Brown et al.
- **Contribution**: In-context learning
- **Key Ideas**:
  - Few-shot learning
  - Prompt engineering
  - Task-agnostic approach
- **Impact**: Enabled LLM applications

## 2. Training and Alignment

### Training Language Models to Follow Instructions (2022)
- **Authors**: Ouyang et al. (OpenAI)
- **Contribution**: InstructGPT
- **Key Ideas**:
  - SFT + RLHF pipeline
  - Human feedback collection
  - Reward modeling
- **Impact**: Foundation for ChatGPT

### Constitutional AI (2022)
- **Authors**: Bai et al. (Anthropic)
- **Contribution**: Self-alignment
- **Key Ideas**:
  - AI feedback for training
  - Constitutional principles
  - Red-teaming
- **Impact**: Safer AI development

### DPO (2023)
- **Authors**: Rafailov et al.
- **Contribution**: Direct Preference Optimization
- **Key Ideas**:
  - No reward model needed
  - Direct policy optimization
  - Simpler than RLHF
- **Impact**: Easier alignment

## 3. Scaling and Efficiency

### Scaling Laws for Neural Language Models (2020)
- **Authors**: Kaplan et al.
- **Contribution**: Scaling laws
- **Key Ideas**:
  - Power law relationships
  - Compute-optimal training
  - Model size vs data size
- **Impact**: Guided model scaling

### Chinchilla (2022)
- **Authors**: Hoffmann et al.
- **Contribution**: Compute-optimal training
- **Key Ideas**:
  - 20 tokens per parameter
  - Data scaling importance
  - Training efficiency
- **Impact**: Changed training strategies

### LLaMA (2023)
- **Authors**: Touvron et al. (Meta)
- **Contribution**: Efficient open-source LLMs
- **Key Ideas**:
  - Smaller, efficient models
  - Data curation
  - Open release
- **Impact**: Open-source LLM revolution

## 4. Reasoning and Planning

### Chain-of-Thought Prompting (2022)
- **Authors**: Wei et al.
- **Contribution**: Step-by-step reasoning
- **Key Ideas**:
  - Explicit reasoning steps
  - Improved math/logic
  - Emergent capability
- **Impact**: Better reasoning

### Tree of Thoughts (2023)
- **Authors**: Yao et al.
- **Contribution**: Structured reasoning
- **Key Ideas**:
  - Multiple reasoning paths
  - Backtracking
  - Search algorithms
- **Impact**: Complex problem solving

### ReAct (2022)
- **Authors**: Yao et al.
- **Contribution**: Reasoning + Acting
- **Key Ideas**:
  - Interleaved thinking/action
  - Tool use
  - Grounded reasoning
- **Impact**: Agent capabilities

## 5. Vision and Multimodal

### ViT (2020)
- **Authors**: Dosovitskiy et al.
- **Contribution**: Vision Transformer
- **Key Ideas**:
  - Patch-based processing
  - Transformer for vision
  - Scalability
- **Impact**: Unified architectures

### CLIP (2021)
- **Authors**: Radford et al. (OpenAI)
- **Contribution**: Vision-language pre-training
- **Key Ideas**:
  - Contrastive learning
  - Zero-shot transfer
  - Natural language supervision
- **Impact**: Multimodal AI

### DALL-E (2021)
- **Authors**: Ramesh et al. (OpenAI)
- **Contribution**: Text-to-image generation
- **Key Ideas**:
  - Autoregressive generation
  - Text-image alignment
  - Creative generation
- **Impact**: Image generation

### Stable Diffusion (2022)
- **Authors**: Rombach et al.
- **Contribution**: Efficient image generation
- **Key Ideas**:
  - Latent diffusion
  - Cross-attention conditioning
  - Open-source release
- **Impact**: Democratized image generation

## 6. Code Generation

### Codex (2021)
- **Authors**: Chen et al. (OpenAI)
- **Contribution**: Code generation
- **Key Ideas**:
  - Fine-tuning on code
  - Function completion
  - Multiple languages
- **Impact**: GitHub Copilot

### CodeLlama (2023)
- **Authors**: Rozière et al. (Meta)
- **Contribution**: Open-source code models
- **Key Ideas**:
  - Fill-in-the-middle
  - Long context
  - Infilling
- **Impact**: Open code generation

## 7. Retrieval and RAG

### Retrieval-Augmented Generation (2020)
- **Authors**: Lewis et al.
- **Contribution**: RAG paradigm
- **Key Ideas**:
  - Retrieval + generation
  - External knowledge
  - Reduced hallucination
- **Impact**: Factual generation

### REALM (2020)
- **Authors**: Guu et al.
- **Contribution**: Retrieval-augmented pre-training
- **Key Ideas**:
  - Learn to retrieve
  - End-to-end training
  - Knowledge grounding
- **Impact**: Improved retrieval

## 8. Efficient Training

### LoRA (2021)
- **Authors**: Hu et al.
- **Contribution**: Low-rank adaptation
- **Key Ideas**:
  - Low-rank matrices
  - Parameter efficiency
  - Fast fine-tuning
- **Impact**: Democratized fine-tuning

### QLoRA (2023)
- **Authors**: Dettmers et al.
- **Contribution**: Quantized LoRA
- **Key Ideas**:
  - 4-bit quantization
  - NormalFloat data type
  - Double quantization
- **Impact**: Fine-tuning on consumer GPUs

### Flash Attention (2022)
- **Authors**: Dao et al.
- **Contribution**: Efficient attention
- **Key Ideas**:
  - IO-aware algorithm
  - Tiling for memory
  - Kernel fusion
- **Impact**: Faster training/inference

## 9. Safety and Alignment

### Red Teaming Language Models (2022)
- **Authors**: Perez et al.
- **Contribution**: Adversarial testing
- **Key Ideas**:
  - Automated red-teaming
  - Attack generation
  - Vulnerability discovery
- **Impact**: Safer models

### Sleeper Agents (2024)
- **Authors**: Hubinger et al.
- **Contribution**: Deceptive alignment
- **Key Ideas**:
  - Backdoor behaviors
  - Training tampering
  - Safety risks
- **Impact**: Alignment research

## 10. Applications

### AlphaFold (2021)
- **Authors**: Jumper et al. (DeepMind)
- **Contribution**: Protein structure prediction
- **Key Ideas**:
  - Attention for structure
  - Multiple sequence alignment
  - Iterative refinement
- **Impact**: Biology revolution

### Gato (2022)
- **Authors**: Reed et al. (DeepMind)
- **Contribution**: Generalist agent
- **Key Ideas**:
  - Multi-task learning
  - Sequential decision making
  - Unified architecture
- **Impact**: General AI agents
