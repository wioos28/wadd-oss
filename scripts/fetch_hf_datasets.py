#!/usr/bin/env python3
"""Fetch and process datasets from HuggingFace."""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from datasets import load_dataset

# Popular datasets to fetch (using full namespace)
DATASETS = [
    # Instruction Following
    "databricks/databricks-dolly-15k",
    
    # Knowledge & QA
    "squad_v2",
    
    # Code
    "codeparrot/apps",
    
    # Reasoning
    "gsm8k",
    
    # Sentiment
    "imdb",
    
    # Conversations
    "Open-Orca/OpenOrca",
]

OUTPUT_DIR = Path(__file__).parent.parent / "sample_data" / "hf_knowledge"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def format_qa(example, dataset_name):
    """Format QA example as knowledge entry."""
    question = example.get("question", "")
    context = example.get("context", "")
    answer = example.get("answers", {})
    
    if isinstance(answer, dict):
        if "text" in answer:
            answer_text = answer["text"][0] if answer["text"] else ""
        elif "answer" in answer:
            answer_text = str(answer["answer"])
        else:
            answer_text = str(answer)
    else:
        answer_text = str(answer)
    
    content = f"## {dataset_name}\n\n"
    content += f"**Question:** {question}\n\n"
    if context:
        content += f"**Context:** {context[:500]}\n\n"
    content += f"**Answer:** {answer_text}\n"
    
    return {
        "content": content,
        "source_type": "qa",
        "source_path": f"huggingface/{dataset_name}",
        "tags": ["qa", dataset_name, "huggingface"],
        "metadata": {"dataset": dataset_name, "type": "qa"}
    }

def format_code(example, dataset_name):
    """Format code example as knowledge entry."""
    code = example.get("code", example.get("func_code_string", ""))
    repo = example.get("repository_name", "")
    path = example.get("file_path", "")
    lang = example.get("language", "unknown")
    
    if not code:
        return None
    
    content = f"## {dataset_name}: {lang}\n\n"
    content += f"**Repository:** {repo}\n"
    content += f"**File:** {path}\n\n"
    content += f"```{lang}\n{code[:1000]}\n```\n"
    
    return {
        "content": content,
        "source_type": "code",
        "source_path": f"huggingface/{dataset_name}/{repo}/{path}",
        "tags": ["code", lang, dataset_name, "huggingface"],
        "metadata": {"dataset": dataset_name, "language": lang, "type": "code"}
    }

def format_instruction(example, dataset_name):
    """Format instruction example as knowledge entry."""
    instruction = example.get("instruction", example.get("question", ""))
    input_text = example.get("input", "")
    output_text = example.get("output", example.get("response", ""))
    
    content = f"## {dataset_name}\n\n"
    content += f"**Instruction:** {instruction}\n\n"
    if input_text:
        content += f"**Input:** {input_text}\n\n"
    content += f"**Output:** {output_text}\n"
    
    return {
        "content": content,
        "source_type": "instruction",
        "source_path": f"huggingface/{dataset_name}",
        "tags": ["instruction", dataset_name, "huggingface"],
        "metadata": {"dataset": dataset_name, "type": "instruction"}
    }

def format_text(example, dataset_name):
    """Format text example as knowledge entry."""
    text = example.get("text", example.get("content", example.get("document", "")))
    
    if not text:
        return None
    
    # Truncate long texts
    if len(text) > 2000:
        text = text[:2000] + "..."
    
    content = f"## {dataset_name}\n\n{text}\n"
    
    return {
        "content": content,
        "source_type": "text",
        "source_path": f"huggingface/{dataset_name}",
        "tags": ["text", dataset_name, "huggingface"],
        "metadata": {"dataset": dataset_name, "type": "text"}
    }

def fetch_dataset(dataset_name, max_samples=100):
    """Fetch and process a dataset."""
    print(f"Fetching: {dataset_name}...")
    
    try:
        # Load dataset
        ds = load_dataset(dataset_name, split="train")
        
        # Limit samples
        if len(ds) > max_samples:
            ds = ds.select(range(max_samples))
        
        entries = []
        
        for example in ds:
            entry = None
            
            # Determine format based on columns
            columns = set(example.keys())
            
            if "question" in columns and ("answers" in columns or "context" in columns):
                entry = format_qa(example, dataset_name)
            elif "code" in columns or "func_code_string" in columns:
                entry = format_code(example, dataset_name)
            elif "instruction" in columns or ("question" in columns and "output" in columns):
                entry = format_instruction(example, dataset_name)
            else:
                entry = format_text(example, dataset_name)
            
            if entry and entry["content"]:
                entries.append(entry)
        
        print(f"  ✓ {len(entries)} entries from {dataset_name}")
        return entries
        
    except Exception as e:
        print(f"  ✗ Error fetching {dataset_name}: {e}")
        return []

def save_entries(entries, dataset_name):
    """Save entries to JSON file."""
    output_file = OUTPUT_DIR / f"{dataset_name.replace('/', '_')}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    
    return output_file

def main():
    """Main function."""
    print("=" * 60)
    print("HuggingFace Dataset Fetcher")
    print("=" * 60)
    
    all_entries = []
    
    for dataset_name in DATASETS:
        entries = fetch_dataset(dataset_name, max_samples=100)
        if entries:
            save_entries(entries, dataset_name)
            all_entries.extend(entries)
    
    # Save combined file
    combined_file = OUTPUT_DIR / "all_datasets.json"
    with open(combined_file, 'w', encoding='utf-8') as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print(f"Total entries fetched: {len(all_entries)}")
    print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
