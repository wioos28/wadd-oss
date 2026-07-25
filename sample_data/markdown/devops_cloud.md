# DevOps & Cloud Computing

## 1. DevOps Principles

### Core Values
- **Culture**: Collaboration between Dev and Ops
- **Automation**: Automate everything possible
- **Measurement**: Measure everything
- **Sharing**: Share knowledge and tools

### CALMS Framework
- **C**ulture
- **A**utomation
- **L**ean
- **M**easurement
- **S**haring

## 2. CI/CD

### Continuous Integration (CI)
- Merge code frequently
- Automated build & test
- Early bug detection

### Continuous Delivery (CD)
- Always production-ready
- Automated deployment pipeline
- Manual approval for production

### Continuous Deployment
- Automated deployment to production
- No manual intervention

### Tools
- **GitHub Actions**: GitHub native
- **GitLab CI/CD**: GitLab native
- **Jenkins**: Self-hosted, extensible
- **CircleCI**: Cloud-based
- **Travis CI**: Cloud-based

## 3. Containerization

### Docker
```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: myapp
```

### Key Concepts
- **Image**: Read-only template
- **Container**: Running instance
- **Volume**: Persistent storage
- **Network**: Container communication

## 4. Kubernetes (K8s)

### Architecture
- **Master Node**: Control plane
  - API Server
  - etcd
  - Scheduler
  - Controller Manager
- **Worker Node**: Running containers
  - kubelet
  - kube-proxy
  - Container Runtime

### Core Objects
| Object | Purpose |
|--------|---------|
| **Pod** | Smallest deployable unit |
| **Service** | Network endpoint for pods |
| **Deployment** | Manage pod replicas |
| **ConfigMap** | Configuration data |
| **Secret** | Sensitive data |
| **Ingress** | HTTP routing |

### Example Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: nginx:latest
        ports:
        - containerPort: 80
```

## 5. Cloud Computing

### Service Models
| Model | Provider Manages | User Manages | Examples |
|-------|------------------|--------------|----------|
| **IaaS** | Hardware, VMs | OS, Apps | AWS EC2, Azure VMs |
| **PaaS** | Hardware, OS, Runtime | Apps, Data | Heroku, Google App Engine |
| **SaaS** | Everything | Just use | Gmail, Salesforce |

### Major Providers
- **AWS**: Amazon Web Services
- **Azure**: Microsoft
- **GCP**: Google Cloud Platform
- **DigitalOcean**: Developer-friendly
- **Linode/Akamai**: Simple cloud

### Key Services
| Category | AWS | Azure | GCP |
|----------|-----|-------|-----|
| Compute | EC2, Lambda | VMs, Functions | Compute Engine, Cloud Functions |
| Storage | S3 | Blob Storage | Cloud Storage |
| Database | RDS, DynamoDB | SQL Database | Cloud SQL, Firestore |
| Networking | VPC | Virtual Network | VPC |

## 6. Infrastructure as Code (IaC)

### Tools
- **Terraform**: Multi-cloud, HCL
- **Pulumi**: Multi-cloud, programming languages
- **CloudFormation**: AWS native
- **Ansible**: Configuration management

### Terraform Example
```hcl
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  
  tags = {
    Name = "WebServer"
  }
}
```

## 7. Monitoring & Observability

### Three Pillars
1. **Metrics**: Numerical measurements
2. **Logs**: Event records
3. **Traces**: Request flow

### Tools
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **ELK Stack**: Elasticsearch, Logstash, Kibana
- **Jaeger**: Distributed tracing
- **Datadog**: Full-stack monitoring

### Alerting
- Define SLOs/SLIs
- Set thresholds
- Route alerts
- Escalation policies

## 8. Security in DevOps (DevSecOps)

### Practices
- SAST/DAST scanning
- Container scanning
- Secret management
- Compliance as code
- Security monitoring
