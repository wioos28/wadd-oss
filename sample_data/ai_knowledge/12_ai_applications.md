# AI Applications - Complete Guide

## 1. Natural Language Processing Applications

### Chatbots and Virtual Assistants
```python
class ChatBot:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.history = []
    
    def respond(self, user_input):
        # Add to history
        self.history.append({"role": "user", "content": user_input})
        
        # Generate response
        prompt = self.build_prompt()
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs, max_length=500)
        response = self.tokenizer.decode(outputs[0])
        
        # Add to history
        self.history.append({"role": "assistant", "content": response})
        
        return response
    
    def build_prompt(self):
        prompt = "You are a helpful assistant.\n\n"
        for msg in self.history:
            prompt += f"{msg['role']}: {msg['content']}\n"
        prompt += "assistant: "
        return prompt
```

### Sentiment Analysis
```python
from transformers import pipeline

classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def analyze_sentiment(texts):
    results = classifier(texts)
    return [{"text": text, "sentiment": res["label"], "score": res["score"]} 
            for text, res in zip(texts, results)]
```

### Named Entity Recognition
```python
import spacy

nlp = spacy.load("en_core_web_trf")

def extract_entities(text):
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]
```

### Text Summarization
```python
from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize(text, max_length=150):
    return summarizer(text, max_length=max_length, min_length=50)[0]["summary_text"]
```

### Machine Translation
```python
from transformers import pipeline

translator = pipeline("translation_en_to_fr", model="Helsinki-NLP/opus-mt-en-fr")

def translate(text):
    return translator(text)[0]["translation_text"]
```

## 2. Computer Vision Applications

### Image Classification
```python
from transformers import pipeline

classifier = pipeline("image-classification", model="google/vit-base-patch16-224")

def classify_image(image_path):
    return classifier(image_path)
```

### Object Detection
```python
from transformers import pipeline

detector = pipeline("object-detection", model="facebook/detr-resnet-50")

def detect_objects(image_path):
    return detector(image_path)
```

### Image Segmentation
```python
from transformers import pipeline

segmenter = pipeline("image-segmentation", model="facebook/detr-resnet-50-panoptic")

def segment_image(image_path):
    return segmenter(image_path)
```

### Image Generation
```python
from diffusers import StableDiffusionPipeline

pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
pipe = pipe.to("cuda")

def generate_image(prompt, num_inference_steps=50):
    return pipe(prompt, num_inference_steps=num_inference_steps).images[0]
```

## 3. Code Generation Applications

### Code Completion
```python
from transformers import pipeline

code_generator = pipeline("text-generation", model="codellama/CodeLlama-7b-hf")

def complete_code(prompt, max_length=200):
    return code_generator(prompt, max_length=max_length)[0]["generated_text"]
```

### Code Review
```python
def review_code(code, language="python"):
    prompt = f"""Review the following {language} code for potential issues:

```{language}
{code}
```

Provide:
1. Code quality assessment
2. Potential bugs
3. Security concerns
4. Performance improvements
5. Best practices violations
"""
    return llm.complete(prompt)
```

### Code Translation
```python
def translate_code(code, source_lang, target_lang):
    prompt = f"""Translate the following {source_lang} code to {target_lang}:

```{source_lang}
{code}
```

Provide only the translated code:
"""
    return llm.complete(prompt)
```

## 4. Healthcare Applications

### Medical Image Analysis
```python
def analyze_medical_image(image, modality="xray"):
    if modality == "xray":
        model = load_model("medical-xray-classifier")
    elif modality == "mri":
        model = load_model("medical-mri-segmenter")
    
    return model.predict(image)
```

### Clinical NLP
```python
def extract_clinical_info(text):
    # Extract medical entities
    entities = medical_ner(text)
    
    # Extract relations
    relations = medical_re(text)
    
    # Generate summary
    summary = medical_summarizer(text)
    
    return {
        "entities": entities,
        "relations": relations,
        "summary": summary
    }
```

### Drug Discovery
```python
def predict_drug_properties(molecule):
    # Predict properties
    toxicity = toxicity_model.predict(molecule)
    solubility = solubility_model.predict(molecule)
    efficacy = efficacy_model.predict(molecule)
    
    return {
        "toxicity": toxicity,
        "solubility": solubility,
        "efficacy": efficacy
    }
```

## 5. Finance Applications

### Fraud Detection
```python
def detect_fraud(transaction):
    features = extract_features(transaction)
    prediction = fraud_model.predict(features)
    return prediction > 0.5
```

### Sentiment Analysis for Trading
```python
def analyze_market_sentiment(news_articles):
    sentiments = []
    for article in news_articles:
        sentiment = sentiment_analyzer(article["text"])
        sentiments.append({
            "article": article["title"],
            "sentiment": sentiment,
            "impact": estimate_impact(article, sentiment)
        })
    return sentiments
```

### Algorithmic Trading
```python
def trading_strategy(market_data):
    # Predict price movement
    prediction = price_model.predict(market_data)
    
    # Generate signals
    if prediction > threshold:
        return "BUY"
    elif prediction < -threshold:
        return "SELL"
    else:
        return "HOLD"
```

## 6. Autonomous Vehicles

### Perception
```python
def perceive_environment(sensor_data):
    # Object detection
    objects = object_detector(sensor_data["camera"])
    
    # Depth estimation
    depth = depth_estimator(sensor_data["camera"])
    
    # Lane detection
    lanes = lane_detector(sensor_data["camera"])
    
    # Point cloud processing
    obstacles = point_cloud_processor(sensor_data["lidar"])
    
    return {
        "objects": objects,
        "depth": depth,
        "lanes": lanes,
        "obstacles": obstacles
    }
```

### Planning
```python
def plan_trajectory(perception, destination):
    # Generate candidate trajectories
    candidates = trajectory_generator(perception, destination)
    
    # Evaluate trajectories
    scored = [(t, evaluate_trajectory(t)) for t in candidates]
    
    # Select best trajectory
    best = max(scored, key=lambda x: x[1])
    
    return best[0]
```

## 7. Recommendation Systems

### Content-Based Filtering
```python
def content_based_recommend(user_profile, items):
    # Calculate similarity
    scores = []
    for item in items:
        similarity = calculate_similarity(user_profile, item)
        scores.append((item, similarity))
    
    # Return top recommendations
    return sorted(scores, key=lambda x: x[1], reverse=True)[:10]
```

### Collaborative Filtering
```python
def collaborative_filtering(user_id, user_item_matrix):
    # Find similar users
    similar_users = find_similar_users(user_id, user_item_matrix)
    
    # Get their preferences
    recommendations = []
    for user in similar_users:
        items = get_user_items(user)
        recommendations.extend(items)
    
    # Rank by frequency
    return rank_by_frequency(recommendations)[:10]
```

### Hybrid Recommendations
```python
def hybrid_recommend(user_id, items):
    # Content-based scores
    content_scores = content_based_recommend(user_id, items)
    
    # Collaborative scores
    collab_scores = collaborative_filtering(user_id, items)
    
    # Combine scores
    combined = combine_scores(content_scores, collab_scores)
    
    return combined[:10]
```

## 8. Robotics

### Motion Planning
```python
def plan_motion(start, goal, obstacles):
    # RRT (Rapidly-exploring Random Tree)
    tree = [start]
    
    while not reached_goal(tree, goal):
        random_point = sample_free_space(obstacles)
        nearest = find_nearest(tree, random_point)
        new_point = steer(nearest, random_point)
        
        if collision_free(nearest, new_point, obstacles):
            tree.append(new_point)
    
    return extract_path(tree, start, goal)
```

### Grasp Planning
```python
def plan_grasp(object_point_cloud):
    # Detect grasp candidates
    candidates = grasp_detector(object_point_cloud)
    
    # Score grasps
    scored = [(g, score_grasp(g)) for g in candidates]
    
    # Select best grasp
    return max(scored, key=lambda x: x[1])[0]
```

## 9. Speech and Audio

### Speech Recognition
```python
from transformers import pipeline

recognizer = pipeline("automatic-speech-recognition", model="openai/whisper-base")

def transcribe(audio_path):
    return recognizer(audio_path)["text"]
```

### Text-to-Speech
```python
from transformers import pipeline

synthesizer = pipeline("text-to-speech", model="microsoft/speecht5_tts")

def synthesize(text):
    return synthesizer(text)
```

### Voice Cloning
```python
def clone_voice(reference_audio, target_text):
    # Extract voice features
    voice_features = voice_encoder(reference_audio)
    
    # Generate speech
    speech = tts_model.generate(target_text, voice_features)
    
    return speech
```

## 10. Game AI

### Game Playing (RL)
```python
class GameAI:
    def __init__(self, model):
        self.model = model
    
    def choose_action(self, state):
        # Get Q-values
        q_values = self.model(state)
        
        # Epsilon-greedy
        if random.random() < self.epsilon:
            return random_action()
        return q_values.argmax()
    
    def train(self, experience):
        state, action, reward, next_state, done = experience
        
        # Calculate target
        if done:
            target = reward
        else:
            target = reward + self.gamma * self.model(next_state).max()
        
        # Update model
        loss = criterion(self.model(state)[action], target)
        loss.backward()
        self.optimizer.step()
```

### Procedural Content Generation
```python
def generate_level(seed):
    random.seed(seed)
    
    # Generate terrain
    terrain = generate_terrain()
    
    # Place objects
    objects = place_objects(terrain)
    
    # Add enemies
    enemies = spawn_enemies(terrain)
    
    return {
        "terrain": terrain,
        "objects": objects,
        "enemies": enemies
    }
```
