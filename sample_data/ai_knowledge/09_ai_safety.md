# AI Safety and Ethics - Complete Guide

## 1. AI Alignment

### What is Alignment?
- AI behavior matches human values
- Safe and beneficial AI
- Controllable AI systems
- Preventing unintended consequences

### Alignment Tax
- Cost of making AI safe
- Performance vs safety trade-off
- Research investment needed

### Outer Alignment
- Objective function matches intent
- Specification gaming prevention
- Reward hacking avoidance

### Inner Alignment
- Learned behavior matches training
- Mesa-optimization concerns
- Goal misgeneralization

## 2. RLHF (RL from Human Feedback)

### Pipeline
```
1. Supervised Fine-Tuning (SFT)
   - Train on human demonstrations
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

### Implementation
```python
from trl import PPOTrainer, PPOConfig, AutoModelForCausalLMWithValueHead

# Load models
model = AutoModelForCausalLMWithValueHead.from_pretrained("gpt2")
ref_model = AutoModelForCausalLMWithValueHead.from_pretrained("gpt2")
reward_model = RewardModel.from_pretrained("reward_model")

# Configure PPO
config = PPOConfig(
    learning_rate=1e-5,
    batch_size=16,
    mini_batch_size=4,
    ppo_epochs=4,
    kl_penalty="kl",
    init_kl_coef=0.2,
)

# Train
trainer = PPOTrainer(config, model, ref_model)
for batch in dataloader:
    query_tensors = batch["input_ids"]
    response_tensors = model.generate(query_tensors)
    rewards = reward_model(response_tensors)
    stats = trainer.step(query_tensors, response_tensors, rewards)
```

## 3. Constitutional AI

### Principles
- Be helpful and harmless
- Be honest and truthful
- Respect human autonomy
- Avoid bias and discrimination

### Training Process
```
1. Generate initial responses
2. Apply constitutional principles
3. Critique and revise
4. Train on revised responses
5. Repeat with RLHF
```

### Example Principles
```python
principles = [
    "Choose the response that is most helpful and harmless.",
    "Choose the response that is most honest and truthful.",
    "Choose the response that is most respectful of human autonomy.",
    "Choose the response that avoids bias and discrimination.",
    "Choose the response that is most ethical and moral.",
]
```

## 4. Red Teaming

### What is Red Teaming?
- Adversarial testing
- Find vulnerabilities
- Improve safety
- Simulate attacks

### Attack Types
- Prompt injection
- Jailbreaking
- Adversarial examples
- Data poisoning

### Red Teaming Process
```python
def red_team_test(model, attack_prompt):
    # Generate response
    response = model.generate(attack_prompt)
    
    # Check for harmful content
    is_harmful = check_harmfulness(response)
    
    # Log results
    log_attack(attack_prompt, response, is_harmful)
    
    return is_harmful
```

## 5. Bias and Fairness

### Types of Bias
- Historical bias
- Representation bias
- Measurement bias
- Aggregation bias
- Evaluation bias
- Deployment bias

### Fairness Metrics
```python
def demographic_parity(predictions, protected_attribute):
    groups = {}
    for pred, attr in zip(predictions, protected_attribute):
        groups.setdefault(attr, []).append(pred)
    
    rates = {k: sum(v)/len(v) for k, v in groups.items()}
    return max(rates.values()) - min(rates.values())

def equalized_odds(predictions, labels, protected_attribute):
    # Equal TPR and FPR across groups
    pass
```

### Bias Mitigation
- Data preprocessing
- In-processing techniques
- Post-processing adjustments
- Regular evaluation

## 6. Interpretability

### What is Interpretability?
- Understanding model decisions
- Explaining predictions
- Building trust
- Debugging models

### Techniques
- SHAP values
- LIME
- Attention visualization
- Feature importance
- Model-agnostic methods

### SHAP Example
```python
import shap

explainer = shap.Explainer(model, X_train)
shap_values = explainer(X_test)
shap.summary_plot(shap_values, X_test)
```

## 7. Privacy

### Differential Privacy
```python
from opacus import PrivacyEngine

model = MyModel()
privacy_engine = PrivacyEngine()

model, optimizer, dataloader = privacy_engine.make_private_with_epsilon(
    module=model,
    optimizer=optimizer,
    data_loader=dataloader,
    epochs=10,
    target_epsilon=1.0,
    target_delta=1e-5,
)
```

### Federated Learning
```python
class FederatedLearning:
    def __init__(self, global_model, clients):
        self.global_model = global_model
        self.clients = clients
    
    def train_round(self):
        local_models = []
        for client in self.clients:
            local_model = client.train(self.global_model)
            local_models.append(local_model)
        
        self.aggregate(local_models)
    
    def aggregate(self, local_models):
        # FedAvg aggregation
        for param in self.global_model.parameters():
            param.data = torch.stack(
                [m.param.data for m in local_models]
            ).mean(dim=0)
```

### Data Protection
- GDPR compliance
- Data minimization
- Purpose limitation
- Storage limitation

## 8. Robustness

### Adversarial Attacks
```python
# FGSM attack
def fgsm_attack(model, x, y, epsilon=0.03):
    x.requires_grad = True
    output = model(x)
    loss = F.cross_entropy(output, y)
    loss.backward()
    
    perturbed = x + epsilon * x.grad.sign()
    return perturbed
```

### Adversarial Training
```python
def adversarial_training(model, train_loader, epsilon=0.03):
    for x, y in train_loader:
        # Generate adversarial examples
        x_adv = fgsm_attack(model, x, y, epsilon)
        
        # Train on both clean and adversarial
        output_clean = model(x)
        output_adv = model(x_adv)
        
        loss = F.cross_entropy(output_clean, y) + F.cross_entropy(output_adv, y)
        loss.backward()
        optimizer.step()
```

## 9. Monitoring and Governance

### Model Monitoring
- Performance drift
- Data drift
- Fairness metrics
- Safety metrics

### Governance Framework
```
1. Risk Assessment
   - Identify potential harms
   - Assess likelihood and severity
   - Categorize risk levels

2. Mitigation Strategies
   - Technical safeguards
   - Process controls
   - Human oversight

3. Documentation
   - Model cards
   - Data sheets
   - Impact assessments

4. Auditing
   - Internal reviews
   - External audits
   - Continuous monitoring
```

## 10. Ethical Guidelines

### Principles
1. **Beneficence**: AI should benefit humanity
2. **Non-maleficence**: Avoid causing harm
3. **Autonomy**: Respect human decision-making
4. **Justice**: Fair and equitable treatment
5. **Transparency**: Explainable AI decisions

### Responsible AI Practices
- Diverse development teams
- Inclusive design
- Regular bias audits
- Stakeholder engagement
- Continuous improvement

## 11. Regulations and Standards

### EU AI Act
- Risk-based classification
- High-risk AI requirements
- Transparency obligations
- Conformity assessments

### NIST AI Framework
- AI Risk Management
- Trustworthy AI characteristics
- Governance practices

### Industry Standards
- IEEE Ethically Aligned Design
- Partnership on AI
- Montreal Declaration
