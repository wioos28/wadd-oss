# Natural Language Processing - Complete Guide

## 1. Fundamentals

### What is NLP?
- Understanding human language
- Text and speech processing
- Language generation
- Machine translation

### Core Tasks
- Text Classification
- Named Entity Recognition
- Sentiment Analysis
- Question Answering
- Summarization
- Translation

## 2. Text Preprocessing

### Tokenization
```python
# Word tokenization
text = "Hello, how are you?"
tokens = text.split()

# Sentence tokenization
sentences = "Hello. How are you? I'm fine.".split(". ")

# Subword tokenization (BPE)
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
tokens = tokenizer.tokenize("Hello, how are you?")
```

### Normalization
```python
import re
import nltk
from nltk.stem import PorterStemmer, WordNetLemmatizer

def normalize(text):
    # Lowercase
    text = text.lower()
    # Remove special characters
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Stemming
ps = PorterStemmer()
stemmed = ps.stem("running")  # "run"

# Lemmatization
lemmatizer = WordNetLemmatizer()
lemmatized = lemmatizer.lemmatize("running", pos='v')  # "run"
```

### Stop Words
```python
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))
tokens = [word for word in text.split() if word not in stop_words]
```

## 3. Text Representation

### Bag of Words (BoW)
```python
from sklearn.feature_extraction.text import CountVectorizer

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(documents)
```

### TF-IDF
```python
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(documents)
```

### Word Embeddings (Word2Vec)
```python
from gensim.models import Word2Vec

model = Word2Vec(sentences, vector_size=100, window=5, min_count=1)
vector = model.wv['hello']
```

### Sentence Embeddings
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(sentences)
```

## 4. Text Classification

### Traditional ML
```python
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier

# Naive Bayes
nb = MultinomialNB()
nb.fit(X_train, y_train)

# SVM
svm = SVC()
svm.fit(X_train, y_train)

# Random Forest
rf = RandomForestClassifier()
rf.fit(X_train, y_train)
```

### Deep Learning
```python
import torch
import torch.nn as nn

class TextClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim, num_classes):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.fc = nn.Linear(embed_dim, num_classes)
    
    def forward(self, x):
        embedded = self.embedding(x).mean(dim=1)
        return self.fc(embedded)
```

### Transformer-based
```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer

model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased", num_labels=2
)
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

inputs = tokenizer("This movie is great!", return_tensors="pt")
outputs = model(**inputs)
```

## 5. Named Entity Recognition (NER)

### spaCy
```python
import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("Apple is looking at buying U.K. startup for $1 billion")

for ent in doc.ents:
    print(ent.text, ent.label_)
```

### Transformers
```python
from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch

tokenizer = AutoTokenizer.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")
model = AutoModelForTokenClassification.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")

inputs = tokenizer("Apple is looking at buying U.K. startup", return_tensors="pt")
outputs = model(**inputs)
predictions = torch.argmax(outputs.logits, dim=2)
```

## 6. Sentiment Analysis

### Rule-based
```python
from textblob import TextBlob

def get_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return "positive"
    elif analysis.sentiment.polarity < 0:
        return "negative"
    else:
        return "neutral"
```

### Transformer-based
```python
from transformers import pipeline

classifier = pipeline("sentiment-analysis")
result = classifier("I love this product!")
print(result)  # [{'label': 'POSITIVE', 'score': 0.9998}]
```

## 7. Machine Translation

### Seq2Seq
```python
class Seq2Seq(nn.Module):
    def __init__(self, src_vocab, tgt_vocab, embed_dim, hidden_dim):
        super().__init__()
        self.encoder = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        self.decoder = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, tgt_vocab)
    
    def forward(self, src, tgt):
        _, (hidden, cell) = self.encoder(src)
        output, _ = self.decoder(tgt, (hidden, cell))
        return self.fc(output)
```

### Transformer Translation
```python
from transformers import MarianMTModel, MarianTokenizer

model_name = "Helsinki-NLP/opus-mt-en-fr"
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

text = "Hello, how are you?"
translated = model.generate(**tokenizer(text, return_tensors="pt"))
print(tokenizer.decode(translated[0], skip_special_tokens=True))
```

## 8. Text Summarization

### Extractive
```python
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

def extractive_summary(text, num_sentences=3):
    sentences = sent_tokenize(text)
    words = word_tokenize(text.lower())
    
    # Calculate word frequencies
    freq = {}
    for word in words:
        if word not in stopwords.words('english'):
            freq[word] = freq.get(word, 0) + 1
    
    # Score sentences
    scores = {}
    for sent in sentences:
        for word in word_tokenize(sent.lower()):
            if word in freq:
                scores[sent] = scores.get(sent, 0) + freq[word]
    
    # Get top sentences
    ranked = sorted(scores, key=scores.get, reverse=True)[:num_sentences]
    return ' '.join(ranked)
```

### Abstractive
```python
from transformers import pipeline

summarizer = pipeline("summarization")
summary = summarizer(text, max_length=150, min_length=50)
```

## 9. Question Answering

### Extractive QA
```python
from transformers import pipeline

qa = pipeline("question-answering")
result = qa(question="What is the capital of France?", context="France is a country in Europe. Its capital is Paris.")
print(result['answer'])  # "Paris"
```

### Generative QA
```python
from transformers import pipeline

generator = pipeline("text2text-generation", model="t5-base")
result = generator(f"question: What is AI? context: AI is artificial intelligence.")
```

## 10. Text Generation

### Language Models
```python
from transformers import pipeline

generator = pipeline("text-generation", model="gpt2")
output = generator("The future of AI is", max_length=50)
```

### Beam Search
```python
def beam_search(model, tokenizer, prompt, num_beams=5, max_length=50):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(
        **inputs,
        max_length=max_length,
        num_beams=num_beams,
        early_stopping=True
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
```

### Top-k Sampling
```python
def top_k_sampling(model, tokenizer, prompt, k=50, temperature=1.0):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(
        **inputs,
        max_length=100,
        do_sample=True,
        top_k=k,
        temperature=temperature
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
```

## 11. Evaluation Metrics

### BLEU Score
```python
from nltk.translate.bleu_score import sentence_bleu

reference = [['the', 'cat', 'is', 'on', 'the', 'mat']]
candidate = ['there', 'is', 'a', 'cat', 'on', 'the', 'mat']
score = sentence_bleu(reference, candidate)
```

### ROUGE Score
```python
from rouge_score import rouge_scorer

scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
scores = scorer.score(reference, candidate)
```

### Perplexity
```python
import torch

def perplexity(model, tokenizer, text):
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs, labels=inputs["input_ids"])
    return torch.exp(outputs.loss)
```

## 12. Tools and Libraries

### NLTK
```python
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
```

### spaCy
```python
import spacy
nlp = spacy.load("en_core_web_sm")
```

### Hugging Face
```python
from transformers import pipeline, AutoModel, AutoTokenizer
```

### Gensim
```python
from gensim.models import Word2Vec, LdaModel
```
