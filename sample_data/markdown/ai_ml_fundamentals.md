# AI & Machine Learning Fundamentals

## 1. Artificial Intelligence Overview

### Definition
AI là lĩnh vực khoa học máy tính致力于 tạo ra các hệ thống có thể thực hiện các tác vụ thông thường cần trí thông minh của con người.

### Types of AI
| Loại | Mô tả | Ví dụ |
|------|-------|-------|
| Narrow AI (ANI) | Chuyên biệt cho 1 lĩnh vực | Chess engine, Siri, recommendation systems |
| General AI (AGI) | Thông minh như con người | Chưa tồn tại |
| Super AI (ASI) | Vượt trội hơn con người | Lý thuyết |

### AI Approaches
1. **Symbolic AI** - Dùng logic, rule-based systems
2. **Machine Learning** - Học từ data
3. **Deep Learning** - Neural networks nhiều lớp
4. **Hybrid** - Kết hợp nhiều approaches

## 2. Machine Learning

### Supervised Learning
Học từ data có labels (input → output).

**Algorithms:**
- **Linear Regression**: Dự đoán giá trị liên tục
  ```
  y = w1*x1 + w2*x2 + ... + b
  ```
- **Logistic Regression**: Phân loại binary
  ```
  P(y=1) = sigmoid(w*x + b)
  ```
- **Decision Tree**: Cây quyết định
- **Random Forest**: Nhiều decision trees kết hợp
- **SVM (Support Vector Machine)**: Tìm hyperplane tối ưu
- **KNN (K-Nearest Neighbors)**: Phân loại dựa trên k láng giềng gần nhất

### Unsupervised Learning
Học từ data không có labels.

**Algorithms:**
- **K-Means Clustering**: Phân cụm
- **DBSCAN**: Clustering dựa trên density
- **PCA (Principal Component Analysis)**: Giảm chiều dữ liệu
- **Autoencoder**: Học biểu diễn compressed

### Reinforcement Learning
Agent học bằng cách tương tác với environment, nhận rewards/penalties.

**Key Concepts:**
- **Agent**: Entity đang học
- **Environment**: Thế giới mà agent tương tác
- **State**: Tình trạng hiện tại
- **Action**: Hành động có thể thực hiện
- **Reward**: Phần thưởng/penalty
- **Policy**: Chiến lược chọn actions
- **Value Function**: Ước tính reward tương lai

**Algorithms:**
- Q-Learning
- Deep Q-Network (DQN)
- Policy Gradient
- Actor-Critic (A2C, A3C, PPO)

## 3. Deep Learning

### Neural Networks Basics
```
Input Layer → Hidden Layer(s) → Output Layer
```

**Activation Functions:**
- **Sigma**: σ(x) = 1/(1+e^(-x)) — Output (0,1)
- **Tanh**: tanh(x) — Output (-1,1)
- **ReLU**: max(0,x) — Most common
- **Leaky ReLU**: max(0.01x, x)
- **Softmax**: Chuyển logits thành probabilities

### Network Types

#### CNN (Convolutional Neural Network)
- Dùng cho image processing
- Components: Convolution → Pooling → Fully Connected
- Ứng dụng: Image classification, object detection, segmentation

#### RNN (Recurrent Neural Network)
- Xử lý sequential data
- Có "memory" từ steps trước
- Issues: Vanishing/Exploding gradients

#### LSTM (Long Short-Term Memory)
-解决 vanishing gradient problem
- Gates: Forget, Input, Output
- Ứng dụng: NLP, time series, speech recognition

#### Transformer
- Attention mechanism thay vì recurrence
- Parallel processing hiệu quả
- Architecture: Encoder-Decoder
- Ứng dụng: BERT, GPT, T5

### Training Process
1. **Forward Pass**: Input → Prediction
2. **Loss Calculation**: So sánh prediction với actual
3. **Backward Pass**: Tính gradients
4. **Weight Update**: Cập nhật weights
5. **Repeat**: Until convergence

**Optimizers:**
- SGD (Stochastic Gradient Descent)
- Adam (Adaptive Moment Estimation)
- RMSprop
- AdaGrad

## 4. Natural Language Processing (NLP)

### Core Tasks
- **Text Classification**: Phân loại văn bản
- **Named Entity Recognition (NER)**: Nhận diện thực thể
- **Sentiment Analysis**: Phân tích cảm xúc
- **Machine Translation**: Dịch máy
- **Question Answering**: Trả lời câu hỏi
- **Text Summarization**: Tóm tắt văn bản

### Word Embeddings
- **Word2Vec**: Word → Vector (Skip-gram, CBOW)
- **GloVe**: Global Vectors
- **FastText**: Word2Vec + subword information

### Modern NLP
- **BERT**: Bidirectional Encoder (understanding)
- **GPT**: Generative Pre-trained Transformer (generation)
- **T5**: Text-to-Text Transfer Transformer
- **LLaMA**: Open-source LLM by Meta

## 5. Computer Vision

### Tasks
- **Image Classification**: Phân loại ảnh
- **Object Detection**: Phát hiện vật thể (YOLO, R-CNN)
- **Semantic Segmentation**: Phân vùng pixel
- **Instance Segmentation**: Phân vùng instance
- **Pose Estimation**: Ước tính tư thế

### Architectures
- **LeNet**: Early CNN
- **AlexNet**: Deep CNN breakthrough
- **VGGNet**: Very deep CNN
- **ResNet**: Residual connections
- **EfficientNet**: Balanced scaling

## 6. Generative AI

### GANs (Generative Adversarial Networks)
- Generator: Tạo data fake
- Discriminator: Phát hiện fake
- Training: Adversarial process

### VAEs (Variational Autoencoders)
- Encoder: Input → Latent space
- Decoder: Latent space → Reconstruction
- Generating new samples từ latent space

### Diffusion Models
- Forward process: Thêm noise逐步
- Reverse process: Remove noise逐步
- Ứng dụng: DALL-E, Stable Diffusion

### LLMs (Large Language Models)
- Scale: billions of parameters
- Capabilities: In-context learning, reasoning
- Examples: GPT-4, Claude, LLaMA, Gemini

## 7. MLOps & Production

### Model Deployment
- **Batch Prediction**: Run periodically
- **Real-time Serving**: API endpoint
- **Edge Deployment**: On-device inference

### Monitoring
- Data drift detection
- Model performance degradation
- A/B testing

### Tools
- MLflow: Experiment tracking
- Kubeflow: ML workflows
- TensorBoard: Visualization
- Weights & Biases: Experiment tracking
