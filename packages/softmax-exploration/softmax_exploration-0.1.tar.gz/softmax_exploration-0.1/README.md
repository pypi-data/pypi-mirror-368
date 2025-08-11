# Softmax Exploration Package

A Python package for implementing softmax exploration strategies in reinforcement learning algorithms.

## Installation

```bash
pip install softmax-exploration
```

## Features

- **Softmax Action Selection**: Convert Q-values to action probabilities using softmax function
- **Boltzmann Exploration**: Temperature-controlled exploration strategy
- **Epsilon-Softmax**: Hybrid approach combining epsilon-greedy with softmax
- **Adaptive Temperature**: Dynamic temperature scheduling for exploration decay
- **Numerical Stability**: Robust implementation with overflow protection

## Usage

### Basic Softmax Exploration

```python
from softmax_exploration import softmax, softmax_action_selection

# Q-values for each action
q_values = [1.2, 0.8, 2.1, 0.5]

# Get action probabilities
probabilities = softmax(q_values, temperature=1.0)
print(probabilities)
# Output: [0.234, 0.156, 0.456, 0.154]

# Select action using softmax
action = softmax_action_selection(q_values, temperature=1.0)
print(f"Selected action: {action}")
```

### Temperature Control

```python
# High temperature = more exploration
probs_high_temp = softmax(q_values, temperature=2.0)
print("High temperature (more exploration):", probs_high_temp)

# Low temperature = more exploitation
probs_low_temp = softmax(q_values, temperature=0.5)
print("Low temperature (more exploitation):", probs_low_temp)
```

### Epsilon-Softmax Hybrid

```python
from softmax_exploration import epsilon_softmax

# Combine epsilon-greedy with softmax
action = epsilon_softmax(q_values, epsilon=0.1, temperature=1.0)
print(f"Epsilon-softmax action: {action}")
```

### Adaptive Temperature Scheduling

```python
from softmax_exploration import adaptive_temperature

# Temperature decreases over episodes
for episode in [0, 10, 50, 100]:
    temp = adaptive_temperature(episode)
    print(f"Episode {episode}: Temperature = {temp:.3f}")
```

### Boltzmann Exploration

```python
from softmax_exploration import boltzmann_exploration

# Boltzmann exploration (same as softmax)
action = boltzmann_exploration(q_values, temperature=1.0)
print(f"Boltzmann action: {action}")
```

## API Reference

### `softmax(q_values, temperature=1.0)`
Compute softmax probabilities for given Q-values.

**Parameters:**
- `q_values`: List or numpy array of Q-values
- `temperature`: Temperature parameter (higher = more exploration)

**Returns:** Probability distribution over actions

### `softmax_action_selection(q_values, temperature=1.0, random_state=None)`
Select an action using softmax exploration.

**Parameters:**
- `q_values`: List or numpy array of Q-values
- `temperature`: Temperature parameter
- `random_state`: Random state for reproducibility

**Returns:** Selected action index

### `epsilon_softmax(q_values, epsilon=0.1, temperature=1.0, random_state=None)`
Hybrid exploration combining epsilon-greedy with softmax.

**Parameters:**
- `q_values`: List or numpy array of Q-values
- `epsilon`: Probability of random action selection
- `temperature`: Temperature parameter for softmax
- `random_state`: Random state for reproducibility

**Returns:** Selected action index

### `adaptive_temperature(episode, initial_temp=10.0, decay_rate=0.995, min_temp=0.1)`
Compute adaptive temperature for exploration scheduling.

**Parameters:**
- `episode`: Current episode number
- `initial_temp`: Initial temperature value
- `decay_rate`: Temperature decay rate
- `min_temp`: Minimum temperature value

**Returns:** Adaptive temperature value

## Requirements

- Python 3.6+
- NumPy

## Installation from Source

```bash
git clone https://github.com/yourusername/softmax-exploration.git
cd softmax-exploration
pip install -e .
```

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to contribute to this project by submitting issues or pull requests.
