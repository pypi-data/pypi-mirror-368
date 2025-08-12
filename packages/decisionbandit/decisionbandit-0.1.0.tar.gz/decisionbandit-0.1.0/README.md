# epsilon-policies

A collection of exploration–exploitation strategies for reinforcement learning, including ε-greedy and related policies.

## Features
- **Exploration** – Select random actions to discover new possibilities.
- **Exploitation** – Choose the best-known action based on current estimates.
- **Fixed Exploration–Then–Exploitation** – Explore for a fixed period, then fully exploit.
- **ε-Greedy** – Balance exploration and exploitation with a probability parameter.
- **ε-Greedy with UCB** – Enhance ε-greedy with Upper Confidence Bound for better action selection.

## Installation


```bash
pip install decisionbandit


import decisionbandit as dcb

# Example: ε-greedy
action = dcb.epsilon_greedy(q_values=[1.0, 0.5, 0.2], epsilon=0.1)
print("Selected action:", action)


MIT License
