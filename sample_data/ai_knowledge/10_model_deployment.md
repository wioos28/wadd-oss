# Model Deployment and Optimization - Complete Guide

## 1. Model Optimization

### Quantization
```python
import torch
from transformers import BitsAndBytesConfig

# INT8 Quantization
bnb_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=6.0,
)

# INT4 Quantization
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    "model_name",
    quantization_config=bnb_config
)
```

### ONNX Export
```python
import torch
from transformers import AutoModel

model = AutoModel.from_pretrained("model_name")
dummy_input = torch.randint(0, 1000, (1, 128))

torch.onnx.export(
    model,
    dummy_input,
    "model.onnx",
    input_names=["input_ids"],
    output_names=["output"],
    dynamic_axes={"input_ids": {0: "batch", 1: "sequence"}},
)
```

### TensorRT Optimization
```python
import tensorrt as trt

# Convert ONNX to TensorRT
logger = trt.Logger(trt.Logger.WARNING)
builder = trt.Builder(logger)
network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
parser = trt.OnnxParser(network, logger)

with open("model.onnx", "rb") as f:
    parser.parse(f.read())

config = builder.create_builder_config()
config.max_workspace_size = 1 << 30  # 1GB
engine = builder.build_engine(network, config)
```

## 2. Serving Solutions

### FastAPI
```python
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI()
classifier = pipeline("text-classification")

class TextRequest(BaseModel):
    text: str

@app.post("/predict")
def predict(request: TextRequest):
    result = classifier(request.text)
    return {"prediction": result}
```

### TorchServe
```python
# handler.py
import torch
from ts.torch_handler.base_handler import BaseHandler

class TextClassifier(BaseHandler):
    def initialize(self, context):
        self.model = torch.load("model.pt")
    
    def preprocess(self, data):
        return data
    
    def inference(self, input_data):
        return self.model(input_data)
    
    def postprocess(self, output):
        return output
```

### Triton Inference Server
```python
# config.pbtxt
name: "text_classifier"
platform: "pytorch_libtorch"
input [
  {
    name: "input_ids"
    dtype: TYPE_INT64
    dims: [128]
  }
]
output [
  {
    name: "output"
    dtype: TYPE_FP32
    dims: [2]
  }
]
```

## 3. Scaling

### Horizontal Scaling
```python
# Load balancer configuration
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://backend;
    }
}
```

### Vertical Scaling
- GPU memory optimization
- Batch processing
- Model parallelism

### Auto-scaling
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: model-server
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: model-server
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## 4. Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  model-server:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models
    environment:
      - MODEL_PATH=/app/models/model.pt
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

## 5. Kubernetes Deployment

### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: model-server
  template:
    metadata:
      labels:
        app: model-server
    spec:
      containers:
      - name: model-server
        image: model-server:latest
        ports:
        - containerPort: 8000
        resources:
          limits:
            nvidia.com/gpu: 1
          requests:
            memory: "4Gi"
            cpu: "2"
```

### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: model-server
spec:
  selector:
    app: model-server
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## 6. Monitoring

### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('requests_total', 'Total requests')
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency')

@app.middleware("http")
async def monitor_requests(request, call_next):
    REQUEST_COUNT.inc()
    with REQUEST_LATENCY.time():
        response = await call_next(request)
    return response
```

### Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

## 7. Cost Optimization

### Spot Instances
```python
# AWS Spot Instance
import boto3

ec2 = boto3.client('ec2')
response = ec2.request_spot_instances(
    SpotPrice='0.10',
    InstanceCount=1,
    Type='one-time',
    LaunchSpecification={
        'ImageId': 'ami-xxx',
        'InstanceType': 'p3.2xlarge',
    }
)
```

### Serverless
```python
# AWS Lambda
import json

def lambda_handler(event, context):
    text = json.loads(event['body'])['text']
    result = model.predict(text)
    return {
        'statusCode': 200,
        'body': json.dumps({'prediction': result})
    }
```

## 8. CI/CD Pipeline

### GitHub Actions
```yaml
name: Model Training

on:
  push:
    branches: [main]

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Train model
      run: python train.py
    
    - name: Evaluate model
      run: python evaluate.py
    
    - name: Deploy
      if: success()
      run: python deploy.py
```

## 9. Edge Deployment

### Mobile (Core ML)
```python
import coremltools as ct

# Convert PyTorch model
model = MyModel()
traced_model = torch.jit.trace(model, example_input)
coreml_model = ct.convert(
    traced_model,
    inputs=[ct.TensorType(name="input", shape=(1, 3, 224, 224))],
)

coreml_model.save("model.mlpackage")
```

### Web (ONNX.js)
```javascript
import * as onnx from 'onnxruntime-web';

const session = await onnx.InferenceSession.create('model.onnx');
const input = new Float32Array([...]);
const results = session.run({ input_ids: input });
```

## 10. Security

### Authentication
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.get("/predict")
def predict(text: str, token: str = Depends(security)):
    if not verify_token(token.credentials):
        raise HTTPException(status_code=401)
    return model.predict(text)
```

### Rate Limiting
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.get("/predict")
@limiter.limit("100/minute")
def predict(text: str):
    return model.predict(text)
```

### Input Validation
```python
from pydantic import BaseModel, validator

class PredictionRequest(BaseModel):
    text: str
    
    @validator('text')
    def text_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('text cannot be empty')
        return v.strip()
```
