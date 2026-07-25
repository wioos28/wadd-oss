# Reinforcement Learning - Complete Guide

## 1. Fundamentals

### What is RL?
- Agent learns by interacting with environment
- Maximize cumulative reward
- Trial and error learning
- Sequential decision making

### Key Concepts
- **Agent**: Learns and makes decisions
- **Environment**: The world the agent interacts with
- **State (s)**: Current situation
- **Action (a)**: What the agent does
- **Reward (r)**: Feedback signal
- **Policy (π)**: Strategy for choosing actions

### MDP (Markov Decision Process)
- States: S
- Actions: A
- Transition: P(s'|s,a)
- Reward: R(s,a,s')
- Discount: γ ∈ [0,1]

## 2. Value-Based Methods

### Q-Learning
```python
import numpy as np

class QLearning:
    def __init__(self, n_states, n_actions, lr=0.1, gamma=0.99, epsilon=0.1):
        self.q_table = np.zeros((n_states, n_actions))
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
    
    def choose_action(self, state):
        if np.random.random() < self.epsilon:
            return np.random.randint(self.q_table.shape[1])
        return np.argmax(self.q_table[state])
    
    def update(self, state, action, reward, next_state, done):
        if done:
            target = reward
        else:
            target = reward + self.gamma * np.max(self.q_table[next_state])
        
        self.q_table[state, action] += self.lr * (target - self.q_table[state, action])
```

### DQN (Deep Q-Network)
```python
import torch
import torch.nn as nn

class DQN(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, action_dim)
        )
    
    def forward(self, x):
        return self.network(x)

class DQNAgent:
    def __init__(self, state_dim, action_dim):
        self.q_network = DQN(state_dim, action_dim)
        self.target_network = DQN(state_dim, action_dim)
        self.optimizer = torch.optim.Adam(self.q_network.parameters())
        self.memory = ReplayBuffer(10000)
    
    def update(self, batch):
        states, actions, rewards, next_states, dones = batch
        
        q_values = self.q_network(states).gather(1, actions)
        next_q_values = self.target_network(next_states).max(1)[0]
        target = rewards + (1 - dones) * 0.99 * next_q_values
        
        loss = nn.MSELoss()(q_values.squeeze(), target)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
```

## 3. Policy-Based Methods

### REINFORCE
```python
class REINFORCE:
    def __init__(self, state_dim, action_dim, lr=0.01):
        self.policy = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim),
            nn.Softmax(dim=-1)
        )
        self.optimizer = torch.optim.Adam(self.policy.parameters(), lr=lr)
    
    def update(self, states, actions, rewards):
        # Calculate returns
        returns = []
        G = 0
        for r in reversed(rewards):
            G = r + 0.99 * G
            returns.insert(0, G)
        returns = torch.tensor(returns)
        returns = (returns - returns.mean()) / (returns.std() + 1e-8)
        
        # Calculate loss
        log_probs = torch.log(self.policy(states))
        loss = 0
        for log_prob, G, action in zip(log_probs, returns, actions):
            loss -= log_prob[action] * G
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
```

### PPO (Proximal Policy Optimization)
```python
class PPO:
    def __init__(self, state_dim, action_dim, lr=3e-4, gamma=0.99, clip=0.2):
        self.actor = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim),
            nn.Softmax(dim=-1)
        )
        self.critic = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
        self.optimizer = torch.optim.Adam([
            {'params': self.actor.parameters(), 'lr': lr},
            {'params': self.critic.parameters(), 'lr': lr}
        ])
        self.clip = clip
    
    def update(self, states, actions, old_log_probs, returns, advantages):
        # Actor loss
        new_log_probs = torch.log(self.actor(states)).gather(1, actions)
        ratio = torch.exp(new_log_probs - old_log_probs)
        
        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 1 - self.clip, 1 + self.clip) * advantages
        actor_loss = -torch.min(surr1, surr2).mean()
        
        # Critic loss
        values = self.critic(states)
        critic_loss = nn.MSELoss()(values.squeeze(), returns)
        
        loss = actor_loss + 0.5 * critic_loss
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
```

## 4. Actor-Critic Methods

### A2C (Advantage Actor-Critic)
```python
class A2C:
    def __init__(self, state_dim, action_dim):
        self.actor = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim),
            nn.Softmax(dim=-1)
        )
        self.critic = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
        self.optimizer = torch.optim.Adam(self.parameters(), lr=3e-4)
    
    def update(self, states, actions, rewards, next_states, dones):
        # Advantages
        values = self.critic(states).squeeze()
        next_values = self.critic(next_states).squeeze()
        advantages = rewards + 0.99 * next_values * (1 - dones) - values
        
        # Actor loss
        log_probs = torch.log(self.actor(states))
        actor_loss = -(log_probs.gather(1, actions) * advantages).mean()
        
        # Critic loss
        critic_loss = advantages.pow(2).mean()
        
        loss = actor_loss + 0.5 * critic_loss
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
```

### SAC (Soft Actor-Critic)
- Maximum entropy RL
- Off-policy
- Continuous actions
- Better exploration

## 5. RLHF (RL from Human Feedback)

### Pipeline
```
1. SFT: Fine-tune on demonstrations
2. RM: Train reward model on preferences
3. PPO: Optimize policy with reward model
```

### Reward Model Training
```python
class RewardModel(nn.Module):
    def __init__(self, base_model):
        super().__init__()
        self.base_model = base_model
        self.reward_head = nn.Linear(base_model.config.hidden_size, 1)
    
    def forward(self, input_ids, attention_mask):
        outputs = self.base_model(input_ids, attention_mask=attention_mask)
        reward = self.reward_head(outputs.last_hidden_state[:, -1, :])
        return reward

def train_reward_model(model, chosen, rejected):
    chosen_reward = model(chosen.input_ids, chosen.attention_mask)
    rejected_reward = model(rejected.input_ids, rejected.attention_mask)
    
    loss = -torch.log(torch.sigmoid(chosen_reward - rejected_reward)).mean()
    return loss
```

### PPO for RLHF
```python
def rlhf_step(policy, reward_model, prompts):
    # Generate responses
    responses = policy.generate(prompts)
    
    # Get rewards
    rewards = reward_model(prompts, responses)
    
    # KL penalty
    kl_penalty = compute_kl_penalty(policy, responses)
    
    # Total reward
    total_reward = rewards - kl_penalty
    
    # Update policy
    policy.update(prompts, responses, total_reward)
```

## 6. Exploration Strategies

### Epsilon-Greedy
```python
def epsilon_greedy(q_values, epsilon):
    if np.random.random() < epsilon:
        return np.random.randint(len(q_values))
    return np.argmax(q_values)
```

### Upper Confidence Bound (UCB)
```python
def ucb(q_values, visit_counts, t):
    return q_values + np.sqrt(2 * np.log(t) / visit_counts)
```

### Thompson Sampling
```python
def thompson_sampling(alpha, beta):
    return np.random.beta(alpha, beta)
```

## 7. Multi-Agent RL

### Concepts
- Multiple agents
- Shared environment
- Cooperative/competitive
- Emergent behavior

### Algorithms
- MADDPG
- QMIX
- COMA
- MAPPO

## 8. Applications

### Game Playing
- AlphaGo
- Atari games
- StarCraft
- Dota 2

### Robotics
- Manipulation
- Locomotion
- Navigation

### Autonomous Driving
- Decision making
- Path planning

### LLM Alignment
- RLHF
- DPO
- Constitutional AI

## 9. Challenges

### Sample Efficiency
- Off-policy methods
- Experience replay
- Model-based RL

### Stability
- Trust regions
- Gradient clipping
- Target networks

### Exploration
- Intrinsic rewards
- Curiosity-driven
- Count-based

## 10. Tools and Frameworks

### OpenAI Gym
```python
import gym

env = gym.make('CartPole-v1')
state = env.reset()
done = False

while not done:
    action = env.action_space.sample()
    next_state, reward, done, info = env.step(action)
    state = next_state
```

### Stable Baselines3
```python
from stable_baselines3 import PPO

model = PPO('MlpPolicy', 'CartPole-v1', verbose=1)
model.learn(total_timesteps=100000)
model.save("ppo_cartpole")
```

### RLlib
```python
import ray
from ray.rllib.algorithms.ppo import PPOConfig

config = PPOConfig().environment("CartPole-v1")
algo = config.build()
for i in range(10):
    result = algo.train()
    print(f"Iteration {i}: reward = {result['episode_reward_mean']}")
```
