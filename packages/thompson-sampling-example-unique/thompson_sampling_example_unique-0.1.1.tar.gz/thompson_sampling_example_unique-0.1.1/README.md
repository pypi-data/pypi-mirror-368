
# Thompson Sampling Package

A simple Python package implementing Thompson Sampling for solving the Multi-Armed Bandit problem.

## Installation

You can install the package using pip:

```bash
pip install thompson-sampling-example-unique
```

## Usage

Here's how to use the `ThompsonSampling` class:

```python
from thompson_sampling.bandit import ThompsonSampling

# Initialize the bandit with 3 arms
n_arms = 3
bandit = ThompsonSampling(n_arms)

# Simulate playing the bandit for a number of rounds
n_rounds = 100
for _ in range(n_rounds):
    # Select an arm based on Thompson Sampling
    chosen_arm = bandit.select_arm()

    # Simulate a reward (replace with your actual reward mechanism)
    # For this example, let's assume arm 0 is slightly better
    reward = 1 if chosen_arm == 0 and np.random.rand() < 0.6 else 0
    if chosen_arm == 1 and np.random.rand() < 0.5:
        reward = 1
    if chosen_arm == 2 and np.random.rand() < 0.4:
        reward = 1


    # Update the bandit with the observed reward
    bandit.update(chosen_arm, reward)

# After the simulation, you can inspect the success and failure counts
print("Successes:", bandit.successes)
print("Failures:", bandit.failures)
```
