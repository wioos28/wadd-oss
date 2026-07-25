# RAG (Retrieval-Augmented Generation) - Complete Guide

## 1. Fundamentals

### What is RAG?
- Combines retrieval + generation
- Accesses external knowledge
- Reduces hallucinations
- Enables up-to-date information

### RAG Pipeline
```
Query → Retrieval → Context → Generation → Answer
```

### Benefits
- Factual accuracy
- Domain expertise
- Reduced training cost
- Real-time knowledge
- Source attribution

## 2. Architecture

### Naive RAG
```
User Query → Embedding → Vector Search → Top-K Docs → LLM → Answer
```

### Advanced RAG
```
User Query → Query Rewriting → Hybrid Search → Re-ranking → Context → LLM → Answer
```

### Modular RAG
```
User Query → Intent Detection → Query Routing → Specialized Pipeline → Answer
```

## 3. Retrieval Methods

### Dense Retrieval
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def dense_search(query, documents, top_k=5):
    query_embedding = model.encode(query)
    doc_embeddings = model.encode(documents)
    
    similarities = cosine_similarity([query_embedding], doc_embeddings)[0]
    top_indices = similarities.argsort()[-top_k:][::-1]
    
    return [documents[i] for i in top_indices]
```

### Sparse Retrieval (BM25)
```python
from rank_bm25 import BM25Okapi

def bm25_search(query, documents, top_k=5):
    tokenized_docs = [doc.split() for doc in documents]
    bm25 = BM25Okapi(tokenized_docs)
    
    tokenized_query = query.split()
    scores = bm25.get_scores(tokenized_query)
    
    top_indices = scores.argsort()[-top_k:][::-1]
    return [documents[i] for i in top_indices]
```

### Hybrid Search
```python
def hybrid_search(query, documents, top_k=5, alpha=0.5):
    dense_results = dense_search(query, documents, top_k)
    sparse_results = bm25_search(query, documents, top_k)
    
    # Reciprocal Rank Fusion
    combined = {}
    for rank, doc in enumerate(dense_results):
        combined[doc] = combined.get(doc, 0) + alpha / (60 + rank)
    for rank, doc in enumerate(sparse_results):
        combined[doc] = combined.get(doc, 0) + (1-alpha) / (60 + rank)
    
    sorted_docs = sorted(combined.items(), key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in sorted_docs[:top_k]]
```

### Semantic Search
```python
def semantic_search(query, vector_store, top_k=5):
    query_embedding = embedding_model.encode(query)
    results = vector_store.search(query_embedding, top_k)
    return results
```

## 4. Chunking Strategies

### Fixed-Size Chunking
```python
def fixed_chunking(text, chunk_size=512, overlap=64):
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)
    return chunks
```

### Semantic Chunking
```python
def semantic_chunking(text, model, threshold=0.5):
    sentences = split_sentences(text)
    chunks = []
    current_chunk = [sentences[0]]
    
    for i in range(1, len(sentences)):
        sim = cosine_similarity(
            model.encode(sentences[i-1]),
            model.encode(sentences[i])
        )
        if sim < threshold:
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentences[i]]
        else:
            current_chunk.append(sentences[i])
    
    chunks.append(' '.join(current_chunk))
    return chunks
```

### Recursive Chunking
```python
def recursive_chunking(text, chunk_size=512):
    if len(text) <= chunk_size:
        return [text]
    
    # Try splitting by paragraphs
    paragraphs = text.split('\n\n')
    chunks = []
    current = ''
    
    for para in paragraphs:
        if len(current) + len(para) <= chunk_size:
            current += para + '\n\n'
        else:
            if current:
                chunks.append(current.strip())
            current = para + '\n\n'
    
    if current:
        chunks.append(current.strip())
    
    return chunks
```

### Document-Specific Chunking
```python
def markdown_chunking(text):
    sections = re.split(r'\n## ', text)
    return [f'## {section}' for section in sections if section.strip()]

def code_chunking(code, language='python'):
    # Split by functions/classes
    tree = ast.parse(code)
    chunks = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            chunks.append(ast.get_source_segment(code, node))
    return chunks
```

## 5. Embedding Models

### Sentence Transformers
```python
from sentence_transformers import SentenceTransformer

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Encode text
embeddings = model.encode(['Hello world', 'How are you?'])

# Similarity
similarity = model.similarity(embeddings[0], embeddings[1])
```

### OpenAI Embeddings
```python
import openai

client = openai.OpenAI()

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=["Hello world"]
)

embedding = response.data[0].embedding
```

### Cohere Embeddings
```python
import cohere

co = cohere.Client('API_KEY')

response = co.embed(
    texts=["Hello world"],
    model='embed-english-v3.0'
)

embedding = response.embeddings[0]
```

## 6. Vector Databases

### ChromaDB
```python
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("documents")

# Add documents
collection.add(
    documents=["doc1", "doc2"],
    metadatas=[{"source": "file1"}, {"source": "file2"}],
    ids=["id1", "id2"]
)

# Query
results = collection.query(
    query_texts=["search query"],
    n_results=5
)
```

### Pinecone
```python
from pinecone import Pinecone

pc = Pinecone(api_key="API_KEY")
index = pc.Index("documents")

# Upsert
index.upsert(vectors=[
    {"id": "doc1", "values": embedding, "metadata": {"source": "file1"}}
])

# Query
results = index.query(
    vector=query_embedding,
    top_k=5,
    include_metadata=True
)
```

### Weaviate
```python
import weaviate

client = weaviate.Client("http://localhost:8080")

# Create schema
client.schema.create_class({
    "class": "Document",
    "properties": [
        {"name": "content", "dataType": ["text"]},
        {"name": "source", "dataType": ["string"]}
    ]
})

# Add objects
client.data_object.create(
    {"content": "doc1", "source": "file1"},
    "Document"
)

# Query
results = client.query.get("Document", ["content", "source"]) \
    .with_near_text({"concepts": ["search query"]}) \
    .with_limit(5) \
    .do()
```

### FAISS
```python
import faiss
import numpy as np

# Create index
dimension = 384
index = faiss.IndexFlatIP(dimension)

# Add vectors
index.add(np.array(embeddings).astype('float32'))

# Search
distances, indices = index.search(
    np.array([query_embedding]).astype('float32'),
    k=5
)
```

## 7. Re-ranking

### Cross-Encoder Re-ranking
```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def rerank(query, documents, top_k=5):
    pairs = [(query, doc) for doc in documents]
    scores = reranker.predict(pairs)
    
    ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in ranked[:top_k]]
```

### Cohere Rerank
```python
import cohere

co = cohere.Client('API_KEY')

results = co.rerank(
    query="search query",
    documents=["doc1", "doc2", "doc3"],
    model="rerank-english-v3.0",
    top_n=5
)
```

## 8. Query Transformation

### Query Rewriting
```python
def rewrite_query(query, llm):
    prompt = f"Rewrite this query for better search results:\n\n{query}\n\nRewritten query:"
    return llm.complete(prompt)
```

### HyDE (Hypothetical Document Embeddings)
```python
def hyde_search(query, llm, vector_store, top_k=5):
    # Generate hypothetical document
    prompt = f"Write a detailed answer to: {query}"
    hypothetical_doc = llm.complete(prompt)
    
    # Search with hypothetical document
    results = vector_store.search(hypothetical_doc, top_k)
    return results
```

### Multi-Query
```python
def multi_query(query, llm, vector_store, num_queries=3, top_k=5):
    # Generate multiple queries
    prompt = f"Generate {num_queries} different queries for: {query}"
    queries = llm.complete(prompt).split('\n')
    
    # Search with each query
    all_results = []
    for q in queries:
        results = vector_store.search(q, top_k)
        all_results.extend(results)
    
    # Deduplicate and rank
    return deduplicate_and_rank(all_results, top_k)
```

## 9. Context Window Management

### Truncation
```python
def truncate_context(context, max_tokens=4000):
    tokens = tokenize(context)
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
    return detokenize(tokens)
```

### Summarization
```python
def summarize_context(context, llm, max_length=500):
    prompt = f"Summarize this in {max_length} words:\n\n{context}"
    return llm.complete(prompt)
```

### Compression
```python
def compress_context(context, query, llm):
    prompt = f"Extract only the relevant information for this query:\n\nQuery: {query}\n\nContext: {context}\n\nRelevant information:"
    return llm.complete(prompt)
```

## 10. Evaluation

### Metrics
- **Faithfulness**: Is the answer grounded in context?
- **Relevance**: Is the answer relevant to the query?
- **Context Precision**: Are the retrieved documents relevant?
- **Context Recall**: Is all relevant information retrieved?

### RAGAS Framework
```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy

result = evaluate(
    dataset=eval_dataset,
    metrics=[faithfulness, answer_relevancy]
)

print(result)
```

### Evaluation Pipeline
```python
def evaluate_rag(query, answer, context, ground_truth):
    metrics = {
        'faithfulness': check_faithfulness(answer, context),
        'relevancy': check_relevancy(answer, query),
        'precision': check_precision(context, ground_truth),
        'recall': check_recall(context, ground_truth)
    }
    return metrics
```
