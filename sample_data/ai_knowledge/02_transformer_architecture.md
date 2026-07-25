# Transformer Architecture - Complete Guide

## 1. Original Transformer (2017)

### Architecture
- Encoder-Decoder structure
- Self-attention mechanism
- Position-wise feed-forward networks
- Residual connections
- Layer normalization

### Key Components

#### Self-Attention
```
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) * V
```
- Q (Query): What am I looking for?
- K (Key): What do I contain?
- V (Value): What information do I provide?

#### Multi-Head Attention
```
MultiHead(Q, K, V) = Concat(head_1, ..., head_h) * W^O
where head_i = Attention(QW_i^Q, KW_i^K, VW_i^V)
```
- Multiple attention heads
- Different representation subspaces
- Parallel computation

#### Position-wise Feed-Forward
```
FFN(x) = max(0, xW_1 + b_1)W_2 + b_2
```
- Two linear transformations
- ReLU activation
- Applied independently to each position

#### Positional Encoding
```
PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```
- Sinusoidal functions
- Relative position information
- No learned parameters

## 2. Encoder-Only (BERT Family)

### BERT
- Bidirectional encoding
- Masked Language Model (MLM)
- Next Sentence Prediction (NSP)
- 12/24 layers
- 768/1024 hidden dimensions

### BERT Variants
- RoBERTa: No NSP, more data
- ALBERT: Parameter sharing
- DistilBERT: Knowledge distillation
- DeBERTa: Disentangled attention

## 3. Decoder-Only (GPT Family)

### GPT Architecture
- Causal (autoregressive) generation
- Masked self-attention
- Next token prediction
- Left-to-right processing

### Key Features
- In-context learning
- Few-shot prompting
- Zero-shot generalization
- Chain-of-thought reasoning

## 4. Encoder-Decoder (T5 Family)

### T5
- Text-to-Text framework
- Span corruption objective
- Multi-task learning
- Encoder-decoder attention

### T5 Variants
- mT5: Multilingual
- Flan-T5: Instruction-tuned
- UL2: Unified Language Learning

## 5. Attention Mechanisms

### Scaled Dot-Product
```python
def scaled_dot_product_attention(Q, K, V, mask=None):
    d_k = Q.size(-1)
    scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(d_k)
    if mask is not None:
        scores = scores.masked_fill(mask == 0, -1e9)
    p_attn = F.softmax(scores, dim=-1)
    return torch.matmul(p_attn, V), p_attn
```

### Multi-Head Attention
```python
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
    
    def forward(self, Q, K, V, mask=None):
        batch_size = Q.size(0)
        
        Q = self.W_q(Q).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.W_k(K).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.W_v(V).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        
        output, attn = scaled_dot_product_attention(Q, K, V, mask)
        output = output.transpose(1, 2).contiguous().view(batch_size, -1, self.num_heads * self.d_k)
        
        return self.W_o(output)
```

### Grouped Query Attention (GQA)
- Key-Value heads shared across Query heads
- Reduces memory usage
- Used in Llama 2, Mistral

### Multi-Head Latent Attention (MLA)
- Compressed KV cache
- Low-rank projection
- Used in DeepSeek-V2

### Sliding Window Attention (SWA)
- Limited attention window
- Linear complexity
- Used in Mistral

## 6. Positional Encodings

### Absolute Positional Encoding
- Sinusoidal (original Transformer)
- Learned (GPT, BERT)

### Relative Positional Encoding
- ALiBi (Attention with Linear Biases)
- Relative position biases
- Used in BLOOM, MPT

### Rotary Positional Encoding (RoPE)
```python
def apply_rotary_emb(x, freqs):
    x_rot = torch.stack([x[..., ::2], x[..., 1::2]], dim=-1)
    x_rot = x_rot * torch.cat([freqs, freqs], dim=-1)
    return torch.cat([x_rot[..., 0], x_rot[..., 1]], dim=-1)
```
- Relative position information
- Rotation in complex space
- Used in Llama, Mistral, Qwen

## 7. Normalization

### Layer Normalization
```python
class LayerNorm(nn.Module):
    def __init__(self, d_model, eps=1e-6):
        super().__init__()
        self.gamma = nn.Parameter(torch.ones(d_model))
        self.beta = nn.Parameter(torch.zeros(d_model))
        self.eps = eps
    
    def forward(self, x):
        mean = x.mean(-1, keepdim=True)
        std = x.std(-1, keepdim=True)
        return self.gamma * (x - mean) / (std + self.eps) + self.beta
```

### RMSNorm
```python
class RMSNorm(nn.Module):
    def __init__(self, d_model, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(d_model))
        self.eps = eps
    
    def forward(self, x):
        norm = torch.sqrt(torch.mean(x ** 2, dim=-1, keepdim=True) + self.eps)
        return x / norm * self.weight
```
- Used in Llama, Mistral, Qwen

## 8. Activation Functions

### ReLU
```python
def relu(x):
    return max(0, x)
```

### GELU
```python
def gelu(x):
    return 0.5 * x * (1 + torch.tanh(math.sqrt(2/math.pi) * (x + 0.044715 * x**3)))
```
- Used in BERT, GPT-2

### SwiGLU
```python
def swiglu(x, W1, W2, W3):
    return (F.silu(x @ W1) * (x @ W3)) @ W2
```
- Used in Llama, Mistral, PaLM

## 9. Optimization Techniques

### Gradient Checkpointing
- Trade compute for memory
- Recompute activations during backward pass
- Reduces memory usage by 50-70%

### Mixed Precision Training
- FP16/BF16 for forward pass
- FP32 for master weights
- 2x speedup, 50% memory reduction

### Flash Attention
- IO-aware attention algorithm
- Tiling for memory efficiency
- 2-4x speedup
- Used in most modern LLMs

### KV Cache
- Cache key-value pairs
- Avoid recomputation
- Reduces inference latency

## 10. Scaling Laws

### Chinchilla Scaling
- Optimal model size vs training data
- ~20 tokens per parameter
- Compute-optimal training

### Scaling Benefits
- Emergent capabilities
- In-context learning
- Chain-of-thought reasoning
- Few-shot generalization
