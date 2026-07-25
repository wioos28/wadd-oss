# Fine-Tuning LLMs - Complete Guide

## 1. Fundamentals

### What is Fine-Tuning?
- Adapt pre-trained model to specific task
- Update model weights
- Improve domain performance
- Reduce prompt engineering needs

### When to Fine-Tune?
- Consistent task requirements
- Domain-specific terminology
- Custom output format
- Performance improvement needed
- Cost-effective at scale

## 2. Fine-Tuning Approaches

### Full Fine-Tuning
```python
from transformers import Trainer, TrainingArguments

training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    learning_rate=2e-5,
    weight_decay=0.01,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)

trainer.train()
```

### LoRA (Low-Rank Adaptation)
```python
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
```

### QLoRA (Quantized LoRA)
```python
from transformers import BitsAndBytesConfig
from peft import LoraConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto"
)

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

### Prefix Tuning
```python
from peft import PrefixTuningConfig

config = PrefixTuningConfig(
    task_type="CAUSAL_LM",
    num_virtual_tokens=20
)

model = get_peft_model(model, config)
```

### Prompt Tuning
```python
from peft import PromptTuningConfig

config = PromptTuningConfig(
    task_type="CAUSAL_LM",
    num_virtual_tokens=10,
    prompt_tuning_init="TEXT",
    prompt_tuning_init_text="Classify this text:"
)

model = get_peft_model(model, config)
```

## 3. Data Preparation

### Instruction Format
```json
{
  "instruction": "Summarize the following text:",
  "input": "The quick brown fox jumps over the lazy dog...",
  "output": "A fox jumped over a dog."
}
```

### Conversation Format
```json
{
  "conversations": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is AI?"},
    {"role": "assistant", "content": "AI is artificial intelligence..."}
  ]
}
```

### Data Processing
```python
def format_instruction(sample):
    return f"""### Instruction:
{sample['instruction']}

### Input:
{sample['input']}

### Response:
{sample['output']}"""

def tokenize_function(examples):
    return tokenizer(
        format_instruction(examples),
        truncation=True,
        max_length=512,
        padding="max_length"
    )
```

### Data Quality
- Clean and consistent
- Balanced classes
- Diverse examples
- Relevant content
- Proper formatting

## 4. Training Configuration

### Hyperparameters
```python
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    gradient_accumulation_steps=4,
    learning_rate=2e-5,
    weight_decay=0.01,
    warmup_steps=100,
    logging_steps=10,
    evaluation_strategy="steps",
    eval_steps=100,
    save_strategy="steps",
    save_steps=100,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    fp16=True,
    bf16=False,
    optim="adamw_torch",
    lr_scheduler_type="cosine",
)
```

### Learning Rate Scheduling
```python
from transformers import get_scheduler

num_training_steps = 1000
lr_scheduler = get_scheduler(
    name="cosine",
    optimizer=optimizer,
    num_warmup_steps=100,
    num_training_steps=num_training_steps
)
```

### Gradient Accumulation
```python
# Effective batch size = batch_size * gradient_accumulation_steps
training_args = TrainingArguments(
    per_device_train_batch_size=8,
    gradient_accumulation_steps=4,
    # Effective batch size = 32
)
```

## 5. Training Loop

### Basic Training
```python
from transformers import Trainer, TrainingArguments

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    accuracy = np.mean(predictions == labels)
    return {"accuracy": accuracy}

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    compute_metrics=compute_metrics,
)

trainer.train()
```

### Custom Training Loop
```python
from torch.utils.data import DataLoader
from torch.optim import AdamW

optimizer = AdamW(model.parameters(), lr=2e-5)
dataloader = DataLoader(train_dataset, batch_size=8)

model.train()
for epoch in range(3):
    for batch in dataloader:
        outputs = model(**batch)
        loss = outputs.loss
        loss.backward()
        
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        
        optimizer.step()
        optimizer.zero_grad()
```

## 6. Evaluation

### Metrics
```python
import evaluate

accuracy_metric = evaluate.load("accuracy")
f1_metric = evaluate.load("f1")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    
    accuracy = accuracy_metric.compute(
        predictions=predictions,
        references=labels
    )
    
    f1 = f1_metric.compute(
        predictions=predictions,
        references=labels,
        average="weighted"
    )
    
    return {**accuracy, **f1}
```

### Holdout Evaluation
```python
from sklearn.model_selection import train_test_split

train_texts, val_texts, train_labels, val_labels = train_test_split(
    texts, labels, test_size=0.2, random_state=42
)
```

### Cross-Validation
```python
from sklearn.model_selection import KFold

kf = KFold(n_splits=5, shuffle=True, random_state=42)
scores = []

for train_idx, val_idx in kf.split(texts):
    train_dataset = Dataset.from_dict({"text": texts[train_idx], "labels": labels[train_idx]})
    val_dataset = Dataset.from_dict({"text": texts[val_idx], "labels": labels[val_idx]})
    
    trainer = Trainer(model=model, train_dataset=train_dataset, eval_dataset=val_dataset)
    trainer.train()
    score = trainer.evaluate()
    scores.append(score)
```

## 7. Model Saving and Loading

### Save Model
```python
# Save full model
model.save_pretrained("./my_model")

# Save tokenizer
tokenizer.save_pretrained("./my_model")

# Save adapter only (LoRA)
model.save_pretrained("./my_lora_adapter")
```

### Load Model
```python
from peft import PeftModel

# Load base model
base_model = AutoModelForCausalLM.from_pretrained("base_model_name")

# Load LoRA adapter
model = PeftModel.from_pretrained(base_model, "./my_lora_adapter")

# Merge adapter (optional)
model = model.merge_and_unload()
```

### Export to GGUF
```python
# Using llama.cpp
python convert_hf_to_gguf.py ./my_model --outfile model.gguf
```

## 8. Distributed Training

### Data Parallel
```python
from torch.nn.parallel import DistributedDataParallel

model = DistributedDataParallel(model, device_ids=[local_rank])
```

### Model Parallel
```python
# Split model across GPUs
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    torch_dtype=torch.float16
)
```

### DeepSpeed
```python
import deepspeed

ds_config = {
    "fp16": {"enabled": True},
    "zero_optimization": {"stage": 2},
    "gradient_accumulation_steps": 4,
    "train_batch_size": 32,
}

model_engine, optimizer, _, _ = deepspeed.initialize(
    model=model,
    config=ds_config
)
```

## 9. Common Issues

### Overfitting
- Add dropout
- Reduce epochs
- Early stopping
- Data augmentation

### Underfitting
- Increase epochs
- Reduce regularization
- Increase model size
- More training data

### Catastrophic Forgetting
- Lower learning rate
- Mix with pre-training data
- Use LoRA instead of full fine-tuning
- Gradual unfreezing

## 10. Best Practices

### Data
- Curate high-quality data
- Balance classes
- Clean and validate
- Appropriate size (1K-100K examples)

### Training
- Start with LoRA
- Monitor validation loss
- Use early stopping
- Save checkpoints

### Evaluation
- Holdout test set
- Multiple metrics
- Human evaluation
- Edge case testing
