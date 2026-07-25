# Computer Vision - Complete Guide

## 1. Fundamentals

### What is Computer Vision?
- Teaching machines to "see"
- Understanding visual information
- Image and video analysis
- Pattern recognition

### Core Tasks
- Image Classification
- Object Detection
- Semantic Segmentation
- Instance Segmentation
- Pose Estimation
- Image Generation

## 2. Convolutional Neural Networks (CNNs)

### Basic CNN
```python
import torch
import torch.nn as nn

class BasicCNN(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 4 * 4, 256),
            nn.ReLU(),
            nn.Linear(256, num_classes),
        )
    
    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x
```

### ResNet
```python
class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, stride=stride, padding=1)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, padding=1)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, 1, stride=stride),
                nn.BatchNorm2d(out_channels)
            )
    
    def forward(self, x):
        out = torch.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += self.shortcut(x)
        out = torch.relu(out)
        return out
```

### EfficientNet
- Compound scaling
- Depth, width, resolution
- Efficient architecture search

## 3. Object Detection

### YOLO (You Only Look Once)
```python
# YOLOv5 inference
import torch

model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
results = model('image.jpg')
results.print()
results.show()
```

### Faster R-CNN
- Region Proposal Network (RPN)
- ROI Pooling
- Two-stage detection

### SSD (Single Shot Detector)
- Multi-scale feature maps
- Anchor boxes
- Single-stage detection

## 4. Semantic Segmentation

### U-Net
```python
class UNet(nn.Module):
    def __init__(self, in_channels=3, out_channels=1):
        super().__init__()
        # Encoder
        self.enc1 = self.conv_block(in_channels, 64)
        self.enc2 = self.conv_block(64, 128)
        self.enc3 = self.conv_block(128, 256)
        
        # Bottleneck
        self.bottleneck = self.conv_block(256, 512)
        
        # Decoder
        self.dec3 = self.conv_block(512 + 256, 256)
        self.dec2 = self.conv_block(256 + 128, 128)
        self.dec1 = self.conv_block(128 + 64, 64)
        
        self.final = nn.Conv2d(64, out_channels, 1)
    
    def conv_block(self, in_ch, out_ch):
        return nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(),
        )
```

### Mask R-CNN
- Instance segmentation
- Per-pixel masks
- Bounding boxes + masks

## 5. Vision Transformers (ViT)

### ViT Architecture
```python
class VisionTransformer(nn.Module):
    def __init__(self, img_size=224, patch_size=16, in_channels=3, 
                 num_classes=1000, embed_dim=768, num_heads=12, num_layers=12):
        super().__init__()
        self.patch_embed = PatchEmbedding(img_size, patch_size, in_channels, embed_dim)
        num_patches = (img_size // patch_size) ** 2
        
        self.cls_token = nn.Parameter(torch.randn(1, 1, embed_dim))
        self.pos_embed = nn.Parameter(torch.randn(1, num_patches + 1, embed_dim))
        
        self.transformer = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(d_model=embed_dim, nhead=num_heads),
            num_layers=num_layers
        )
        
        self.head = nn.Linear(embed_dim, num_classes)
    
    def forward(self, x):
        B = x.shape[0]
        x = self.patch_embed(x)
        
        cls_tokens = self.cls_token.expand(B, -1, -1)
        x = torch.cat([cls_tokens, x], dim=1)
        x = x + self.pos_embed
        
        x = self.transformer(x)
        x = x[:, 0]
        x = self.head(x)
        return x
```

### DeiT (Data-efficient Image Transformer)
- Knowledge distillation
- Data augmentation
- Regularization

### Swin Transformer
- Hierarchical vision transformer
- Shifted windows
- Multi-scale features

## 6. Image Generation

### GANs (Generative Adversarial Networks)
```python
class Generator(nn.Module):
    def __init__(self, latent_dim=100):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(latent_dim, 256),
            nn.LeakyReLU(0.2),
            nn.Linear(256, 512),
            nn.LeakyReLU(0.2),
            nn.Linear(512, 1024),
            nn.LeakyReLU(0.2),
            nn.Linear(1024, 784),
            nn.Tanh()
        )
    
    def forward(self, z):
        return self.model(z)

class Discriminator(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = nn.Sequential(
            nn.Linear(784, 512),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )
    
    def forward(self, img):
        return self.model(img)
```

### Diffusion Models
```python
class DiffusionModel:
    def __init__(self, model, timesteps=1000):
        self.model = model
        self.timesteps = timesteps
        self.betas = torch.linspace(0.0001, 0.02, timesteps)
        self.alphas = 1 - self.betas
        self.alpha_bar = torch.cumprod(self.alphas, dim=0)
    
    def forward_diffusion(self, x0, t):
        noise = torch.randn_like(x0)
        alpha_bar_t = self.alpha_bar[t].reshape(-1, 1, 1, 1)
        xt = torch.sqrt(alpha_bar_t) * x0 + torch.sqrt(1 - alpha_bar_t) * noise
        return xt, noise
    
    def reverse_diffusion(self, xt, t):
        predicted_noise = self.model(xt, t)
        alpha_t = self.alphas[t]
        alpha_bar_t = self.alpha_bar[t]
        
        mean = (1 / torch.sqrt(alpha_t)) * (xt - (1 - alpha_t) / torch.sqrt(1 - alpha_bar_t) * predicted_noise)
        variance = torch.sqrt(1 - alpha_bar_t) * torch.randn_like(xt)
        
        return mean + variance
```

### VAE (Variational Autoencoder)
```python
class VAE(nn.Module):
    def __init__(self, latent_dim=128):
        super().__init__()
        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(784, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU()
        )
        self.mu = nn.Linear(256, latent_dim)
        self.logvar = nn.Linear(256, latent_dim)
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Linear(512, 784),
            nn.Sigmoid()
        )
    
    def encode(self, x):
        h = self.encoder(x)
        return self.mu(h), self.logvar(h)
    
    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std
    
    def decode(self, z):
        return self.decoder(z)
    
    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        return self.decode(z), mu, logvar
```

## 7. Pre-trained Models

### ImageNet Models
```python
import torchvision.models as models

# ResNet
resnet = models.resnet50(pretrained=True)

# EfficientNet
efficientnet = models.efficientnet_b0(pretrained=True)

# ViT
vit = models.vit_b_16(pretrained=True)
```

### CLIP
```python
import clip

model, preprocess = clip.load("ViT-B/32")
image = preprocess(Image.open("image.jpg")).unsqueeze(0)
text = clip.tokenize(["a photo of a cat"])

image_features = model.encode_image(image)
text_features = model.encode_text(text)
```

## 8. Data Augmentation

### Basic Augmentations
```python
from torchvision import transforms

transform = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])
```

### Advanced Augmentations
- CutOut
- MixUp
- CutMix
- AutoAugment
- RandAugment

## 9. Evaluation Metrics

### Classification
- Accuracy
- Precision, Recall, F1
- AUC-ROC
- Confusion Matrix

### Detection
- mAP (mean Average Precision)
- IoU (Intersection over Union)

### Segmentation
- IoU (Jaccard Index)
- Dice Coefficient
- Pixel Accuracy

## 10. Applications

### Medical Imaging
- X-ray analysis
- MRI segmentation
- Pathology detection

### Autonomous Driving
- Lane detection
- Object detection
- Depth estimation

### AR/VR
- Face detection
- Pose estimation
- Scene understanding

### Security
- Face recognition
- Anomaly detection
- Surveillance
