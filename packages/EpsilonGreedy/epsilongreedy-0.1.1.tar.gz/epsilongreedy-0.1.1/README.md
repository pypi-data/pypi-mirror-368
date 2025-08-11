# Epsilon-Greedy Multi-Armed Bandit

A simple Python implementation of the Epsilon-Greedy algorithm for the multi-armed bandit problem. This package provides classes for creating bandit environments and an agent that learns to select the best action. It also includes a command-line interface for running simulations.

## Features

- **EpsilonGreedyAgent**: A configurable agent with parameters for exploration rate (`epsilon`), epsilon decay, and optimistic initial values.
- **MultiArmedBandit Environment**: Supports arms with different reward distributions:
  - **Bernoulli**: For modeling binary outcomes (e.g., click/no-click).
  - **Normal (Gaussian)**: For modeling continuous outcomes.
- **Simulation Runner**: A function to run experiments and collect results like average reward and optimal action rate.
- **Command-Line Interface**: A convenient CLI for running simulations without writing Python code.

## Project Structure

```
.
├── EpsilonGreedy/
│   ├── __init__.py
│   └── main.py
└── README.md
```

- [`EpsilonGreedy/main.py`](EpsilonGreedy/main.py): Contains all the core logic for the `Arm`, `MultiArmedBandit`, and `EpsilonGreedyAgent` classes, as well as the CLI entry point.
- [`EpsilonGreedy/__init__.py`](EpsilonGreedy/__init__.py): Makes the directory a Python package and exposes the main classes for easy import.

## Usage

You can use this project either as a Python library or as a command-line tool.

### As a Library

Import the necessary classes from the `EpsilonGreedy` package to build and run your own bandit simulations.

```python
from EpsilonGreedy import Arm, MultiArmedBandit, EpsilonGreedyAgent, run_bandit

# 1. Define the arms for the bandit problem
arms = [
    Arm(name="arm_1", distribution="bernoulli", p=0.1),
    Arm(name="arm_2", distribution="bernoulli", p=0.5),
    Arm(name="arm_3", distribution="bernoulli", p=0.9),
]

# 2. Create the bandit environment
bandit_env = MultiArmedBandit(arms=arms, seed=42)

# 3. Create the Epsilon-Greedy agent
agent = EpsilonGreedyAgent(
    n_actions=bandit_env.k,
    epsilon=0.1,
    seed=123
)

# 4. Run the simulation
results = run_bandit(env=bandit_env, agent=agent, steps=1000)

# 5. Print the results
print(f"Average reward: {results['avg_reward']:.4f}")
print(f"Optimal action selection rate: {results['optimal_action_rate']:.4f}")
print(f"Final Q-value estimates: {results['final_estimates']}")
```
