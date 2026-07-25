# LLM Training - Complete Technical Guide

## 1. Pre-training Fundamentals

### Data Collection
```python
# Common Crawl processing
def process_common_crawl(dump_path):
    # 1. Download WARC files
    # 2. Extract text content
    # 3. Language detection
    # 4. Deduplication (MinHash)
    # 5. Quality filtering
    # 6. Tokenization
    pass
```

### Data Quality
- Language filtering (fasttext classifier)
- Perplexity filtering (KenLM)
- Toxicity filtering
- Deduplication (exact + fuzzy)
- PII removal

### Tokenization
```python
from transformers import AutoTokenizer

# BPE Tokenizer
tokenizer = AutoTokenizer.from_pretrained("gpt2")
tokens = tokenizer.encode("Hello world")

# Custom training
from tokenizers import Tokenizer, models, pre_tokenizers, trainers

tokenizer = Tokenizer(models.BPE())
tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()
trainer = trainers.BpeTrainer(vocab_size=50000)
tokenizer.train(files, trainer)
```

### Training Objectives
```python
# Next Token Prediction (GPT)
loss = -log_softmax(logits[:, :-1]) * labels[:, 1:]

# Masked Language Modeling (BERT)
# Randomly mask 15% of tokens
# Predict masked tokens

# Span Corruption (T5)
# Corrupt contiguous spans
# Predict corrupted spans
```

## 2. Training Infrastructure

### Hardware Requirements
```
Model Size    | GPU Memory | GPUs Needed
7B            | 14GB       | 1-2
13B           | 26GB       | 2-4
70B           | 140GB      | 8-16
175B          | 350GB      | 32-64
```

### Distributed Training
```python
# Data Parallel
from torch.nn.parallel import DistributedDataParallel as DDP

model = DDP(model, device_ids=[local_rank])

# Model Parallel (FSDP)
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP

model = FSDP(model)

# Pipeline Parallel
from deepspeed import initialize

model_engine, _, _, _ = deepspeed.initialize(model=model, config=ds_config)
```

### Mixed Precision Training
```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

for batch in dataloader:
    with autocast():
        outputs = model(batch)
        loss = criterion(outputs)
    
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

## 3. Optimizer and Scheduling

### AdamW Optimizer
```python
from transformers import AdamW

optimizer = AdamW(
    model.parameters(),
    lr=2e-5,
    betas=(0.9, 0.999),
    eps=1e-8,
    weight_decay=0.01
)
```

### Learning Rate Scheduling
```python
from transformers import get_cosine_schedule_with_warmup

num_training_steps = 100000
num_warmup_steps = 1000

scheduler = get_cosine_schedule_with_warmup(
    optimizer,
    num_warmup_steps=num_warmup_steps,
    num_training_steps=num_steps
)
```

### Gradient Accumulation
```python
accumulation_steps = 4
effective_batch_size = batch_size * accumulation_steps

for i, batch in enumerate(dataloader):
    loss = model(batch) / accumulation_steps
    loss.backward()
    
    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

## 4. Training Loop

### Basic Training
```python
import torch
from torch.utils.data import DataLoader
from transformers import get_linear_schedule_with_warmup

model.train()
total_loss = 0

for epoch in range(num_epochs):
    for batch in dataloader:
        outputs = model(**batch)
        loss = outputs.loss
        
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        
        optimizer.step()
        scheduler.step()
        optimizer.zero_grad()
        
        total_loss += loss.item()
```

### Checkpointing
```python
# Save checkpoint
torch.save({
    'epoch': epoch,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'scheduler_state_dict': scheduler.state_dict(),
    'loss': loss,
}, f'checkpoint-{epoch}.pt')

# Load checkpoint
checkpoint = torch.load(f'checkpoint-{epoch}.pt')
model.load_state_dict(checkpoint['model_state_dict'])
optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
```

## 5. Fine-tuning Techniques

### LoRA (Low-Rank Adaptation)
```python
from peft import LoraConfig, get_peft_model

config = LoraConfig(
    r=16,  # rank
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, config)
print(f"Trainable params: {model.print_trainable_parameters()}")
```

### QLoRA (Quantized LoRA)
```python
from transformers import BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# Quantization config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

# Load model
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto"
)

# Prepare for training
model = prepare_model_for_kbit_training(model)

# Add LoRA
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)
```

### DPO (Direct Preference Optimization)
```python
from trl import DPOTrainer, DPOConfig

training_args = DPOConfig(
    output_dir="./dpo_results",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=5e-7,
    num_train_epochs=3,
    beta=0.1,  # KL penalty
)

trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer,
)

trainer.train()
```

## 6. Evaluation

### Perplexity
```python
def compute_perplexity(model, tokenizer, text):
    encodings = tokenizer(text, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model(**encodings, labels=encodings["input_ids"])
        loss = outputs.loss
    
    return torch.exp(loss)
```

### Benchmark Evaluation
```python
# MMLU (Massive Multitask Language Understanding)
# ARC (AI2 Reasoning Challenge)
# HellaSwag
# TruthfulQA
# HumanEval (Code)
# GSM8K (Math)
```

### Human Evaluation
- Blind evaluation
- Side-by-side comparison
- Rating scales
- Preference ranking

## 7. Scaling Laws

### Chinchilla Scaling
```python
# Optimal tokens per parameter
def chinchilla_optimal(model_size):
    return model_size * 20  # 20 tokens per parameter

# Example:
# 7B model → 140B tokens
# 70B model → 1.4T tokens
```

### Compute Optimal Training
```python
def compute_optimal(model_params, tokens):
    # FLOPs ≈ 6 * model_params * tokens
    flops = 6 * model_params * tokens
    
    # GPU hours (A100 80GB)
    gpu_hours = flops / (312e12 * 0.3)  # 312 TFLOPS, 30% utilization
    
    return gpu_hours
```

## 8. Safety and Alignment

### RLHF Pipeline
```
1. SFT (Supervised Fine-Tuning)
   - Train on demonstrations
   - Learn task completion

2. Reward Model Training
   - Collect human preferences
   - Train reward model
   - Predict human judgments

3. PPO Optimization
   - Optimize policy with reward model
   - KL constraint for stability
   - Balance reward and human values
```

### Constitutional AI
```python
def constitutional_ai_pipeline(model, principles):
    # 1. Generate initial responses
    responses = model.generate(prompts)
    
    # 2. Critique and revise
    for response in responses:
        critique = model.critique(response, principles)
        revised = model.revise(response, critique)
    
    # 3. Train on revised responses
    train(model, revised_dataset)
```

## 9. Optimization Techniques

### Gradient Checkpointing
```python
from torch.utils.checkpoint import checkpoint

def forward_with_checkpointing(x):
    return checkpoint(self.forward_impl, x, use_reentrant=False)
```

### Flash Attention
```python
from flash_attn import flash_attn_func

# Replace standard attention
def flash_attention(q, k, v):
    return flash_attn_func(q, k, v, causal=True)
```

### KV Cache
```python
def generate_with_cache(model, prompt, max_length):
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    past_key_values = None
    
    for _ in range(max_length):
        outputs = model(
            input_ids,
            past_key_values=past_key_values,
            use_cache=True
        )
        
        past_key_values = outputs.past_key_values
        next_token = outputs.logits[:, -1:].argmax(dim=-1)
        input_ids = torch.cat([input_ids, next_token], dim=-1)
    
    return input_ids
```

## 10. Deployment

### Model Export
```python
# Export to ONNX
torch.onnx.export(
    model,
    dummy_input,
    "model.onnx",
    opset_version=17,
    input_names=["input_ids"],
    output_names=["logits"],
)

# Export to GGUF (llama.cpp)
python convert_hf_to_gguf.py model_dir --outfile model.gguf
```

### Quantization
```python
# GPTQ
from gptq import GPTQForCausalLM

model = GPTQForCausalLM.from_quantized(
    "model-gptq",
    device="cuda:0"
)

# AWQ
from awq import AutoAWQForCausalLM

model = AutoAWQForCausalLM.from_quantized(
    "model-awq",
    fuse_layers=True
)
```

### Serving
```python
# vLLM
from vllm import LLM, SamplingParams

llm = LLM(model="model-name")
params = SamplingParams(temperature=0.8, max_tokens=100)
outputs = llm.generate(["Hello"], params)

# TGI (Text Generation Inference)
# docker run --gpus all -p 8080:80 \
#   -v $PWD/data:/data \
#   ghcr.io/huggingface/text-generation-inference:latest \
#   --model-id model-name
```
