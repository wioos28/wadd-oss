# Large Language Model Architectures - Complete Guide

## 1. GPT (Generative Pre-trained Transformer)

### GPT-1 (2018)
- 117M parameters
- 12 transformer layers
- 768 hidden dimensions
- 12 attention heads
- Pre-trained on BookCorpus (5GB)
- Fine-tuning approach for downstream tasks

### GPT-2 (2019)
- 1.5B parameters
- 48 transformer layers
- 1600 hidden dimensions
- 25 attention heads
- Pre-trained on WebText (40GB)
- Zero-shot learning capability
- Layer normalization moved to input

### GPT-3 (2020)
- 175B parameters
- 96 transformer layers
- 12288 hidden dimensions
- 96 attention heads
- Pre-trained on Common Crawl (570GB)
- In-context learning (few-shot)
- Sparse attention patterns

### GPT-4 (2023)
- Estimated 1.8T parameters (MoE)
- Multimodal (text + images)
- Improved reasoning capabilities
- Better alignment with human preferences
- Reduced hallucinations

## 2. Claude (Anthropic)

### Claude 1 (2023)
- Constitutional AI approach
- RLHF with human feedback
- 100K context window
- Focus on safety and helpfulness

### Claude 2 (2023)
- Improved reasoning
- 200K context window
- Better code generation
- Reduced harmful outputs

### Claude 3 (2024)
- Opus: Most capable, complex tasks
- Sonnet: Balanced performance/speed
- Haiku: Fastest, lightweight
- Multimodal capabilities
- 200K context window
- Tool use support

### Claude Architecture
- Transformer-based decoder
- Constitutional AI training
- RLHF + RLAIF
- Harmlessness training
- Helpfulness optimization

## 3. Gemini (Google)

### Gemini 1.0 (2023)
- Ultra: Most capable
- Pro: Balanced
- Nano: On-device
- Multimodal from ground up
- 32K context window

### Gemini 1.5 (2024)
- 1M context window
- MoE architecture
- Improved long-context understanding
- Better code generation
- Multi-turn reasoning

### Gemini Architecture
- Multi-modal transformer
- MoE (Mixture of Experts)
- TPU-optimized
- Efficient attention mechanisms
- Cross-modal understanding

## 4. Llama (Meta)

### Llama 1 (2023)
- 7B, 13B, 33B, 65B parameters
- Open source
- Pre-trained on 1T tokens
- Efficient inference
- Grouped Query Attention (GQA)

### Llama 2 (2023)
- 7B, 13B, 70B parameters
- 40% more training data
- 2K context window
- RLHF alignment
- Ghost Attention (GAtt)

### Llama 3 (2024)
- 8B, 70B parameters
- 128K context window
- Improved reasoning
- Better code generation
- Multilingual support

### Llama Architecture
- Pre-norm transformer
- SwiGLU activation
- RoPE positional encoding
- GQA (Grouped Query Attention)
- RMSNorm normalization

## 5. Mistral

### Mistral 7B (2023)
- 7.3B parameters
- 32K context window
- Sliding Window Attention (SWA)
- Mixed precision training
- Outperforms Llama 2 13B

### Mixtral 8x7B (2024)
- 8 experts, 2 active per token
- 46.7B total parameters
- 32K context window
- MoE architecture
- Outperforms Llama 2 70B

### Mistral Architecture
- Sliding Window Attention
- GQA (Grouped Query Attention)
- Byte-fallback BPE tokenizer
- Rolling buffer KV cache
- Pre-chunked attention

## 6. Other Major Models

### BLOOM (BigScience)
- 176B parameters
- 46 languages
- Open source
- BLOOM architecture (transformer)

### Falcon (TII)
- 7B, 40B, 180B parameters
- Multi-query attention
- Pre-trained on RefinedWeb
- Commercially usable

### Qwen (Alibaba)
- 7B, 14B, 72B parameters
- Multilingual
- Long context support
- Tool use capabilities

### DeepSeek
- DeepSeek-V2: 236B MoE
- DeepSeek-Coder: Code generation
- DeepSeek-Math: Math reasoning
- MLA (Multi-head Latent Attention)

### Yi (01.AI)
- 6B, 34B parameters
- 200K context window
- Multilingual
- Open source

## 7. Model Comparison

| Model | Params | Context | License |
|-------|--------|---------|---------|
| GPT-4 | ~1.8T | 128K | Proprietary |
| Claude 3 | Unknown | 200K | Proprietary |
| Gemini 1.5 | Unknown | 1M | Proprietary |
| Llama 3 | 8B/70B | 128K | Open |
| Mixtral | 46.7B | 32K | Apache 2.0 |
| Falcon | 180B | 2K | Apache 2.0 |
| Qwen 2 | 72B | 128K | Apache 2.0 |

## 8. Training Techniques

### Pre-training
- Next token prediction
- Masked language modeling
- Causal language modeling
- Denoising objectives

### Fine-tuning
- Supervised Fine-Tuning (SFT)
- Instruction tuning
- Domain adaptation
- Multi-task learning

### Alignment
- RLHF (Reinforcement Learning from Human Feedback)
- DPO (Direct Preference Optimization)
- Constitutional AI
- RLAIF (AI Feedback)

### Efficiency
- LoRA (Low-Rank Adaptation)
- QLoRA (Quantized LoRA)
- PEFT (Parameter-Efficient Fine-Tuning)
- Gradient checkpointing
