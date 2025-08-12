# FXTensor

FXTensor is a Python library for tensor-based computations, particularly suited for modeling probabilistic systems and processes inspired by category theory. It leverages NumPy for efficient numerical computations. The library primarily supports labeled indices for enhanced readability while maintaining compatibility with unlabeled numeric indices.

## Core Concepts

An FXTensor is defined by its `profile` and `data`, with optional string labels to make tensors more intuitive and meaningful.

- **Profile**: A pair `[domain, codomain]` specifying the dimensions of input (domain) and output (codomain) indices. For labeled tensors, e.g., `[[['a', 'b']], [['x', 'y', 'z']]]` represents a 2x3 matrix with labeled rows and columns. For unlabeled tensors, `[[2], [3]]` specifies dimensions numerically.
- **Labels (Optional)**: String labels can be assigned to each dimension, enhancing interpretability. For example, input axis labeled `['a', 'b']` and output axis labeled `['x', 'y', 'z']`. Unlabeled tensors have `labels` set to `None`.
- **Data**: A NumPy array holding the tensor’s values. Its shape must match the total number of dimensions in the profile (`len(domain) + len(codomain)`).

## Usage Examples

### Basic Example: Labeled Tensor

```python
import numpy as np
from fxtensor_salmon import FXTensor

# Create a 2x3 matrix with string labels
profile = [[['a', 'b']], [['x', 'y', 'z']]]
data = np.array([
    [0.1, 0.2, 0.7],  # a -> x, y, z
    [0.3, 0.3, 0.4]   # b -> x, y, z
])
tensor = FXTensor(profile, data=data)

# Access elements using labels
assert tensor.get_label_index(0, 'a') == 0  # Index of label 'a' on input axis
assert tensor.get_index_label(1, 2) == 'z'  # Label at index 2 on output axis
```

### Unlabeled Tensor

```python
# Create a 2x3 matrix with numeric indices
profile = [[2], [3]]
data = np.array([
    [0.1, 0.2, 0.7],
    [0.3, 0.3, 0.4]
])
tensor = FXTensor(profile, data=data)
assert tensor.labels == (None, None)  # No labels
```

### Creating Tensor from Strands

```python
# Create a tensor from labeled strands
profile = [[['a', 'b']], [['x', 'y', 'z']]]
strands = {
    "[[['a']], [['x']]]": 0.1,
    "[[['a']], [['y']]]": 0.2,
    "[[['a']], [['z']]]": 0.7,
    "[[['b']], [['x']]]": 0.3,
    "[[['b']], [['y']]]": 0.3,
    "[[['b']], [['z']]]": 0.4
}
tensor = FXTensor.from_strands(profile, strands)
assert tensor.labels == ([['a', 'b']], [['x', 'y', 'z']])
```

### Labeled Tensor Composition

```python
# P(Y|X) where X={a,b}, Y={x,y}
tensor1 = FXTensor(
    [[['a', 'b']], [['x', 'y']]],
    data=np.array([
        [0.2, 0.8],  # a -> x, y
        [0.6, 0.4]   # b -> x, y
    ])
)

# P(Z|Y) where Y={x,y}, Z={p,q}
tensor2 = FXTensor(
    [[['x', 'y']], [['p', 'q']]],
    data=np.array([
        [0.3, 0.7],  # x -> p, q
        [0.9, 0.1]   # y -> p, q
    ])
)

# Composition: P(Z|X) = P(Y|X) ; P(Z|Y)
result = tensor1.composition(tensor2)
assert result.labels == ([['a', 'b']], [['p', 'q']])
```

### Labeled Tensor Product

```python
# P(X) where X={a,b}
tensor1 = FXTensor(
    [[], [['a', 'b']]],
    data=np.array([0.3, 0.7])
)

# P(Y) where Y={x,y,z}
tensor2 = FXTensor(
    [[], [['x', 'y', 'z']]],
    data=np.array([0.2, 0.3, 0.5])
)

# Tensor product: P(X,Y) = P(X) ⊗ P(Y)
result = tensor1.tensor_product(tensor2)
assert result.labels == ([], [['a', 'b'], ['x', 'y', 'z']])
```

## Simple Example: Weather Forecast (Labeled)

Model a weather system with states “Sunny” or “Rainy.”

- **State Tensor**: Represents today’s weather probability with labels. If today is certainly sunny, the state is `[1, 0]`.

  ```python
  weather_states = ['Sunny', 'Rainy']
  sunny_today = FXTensor([[], [weather_states]], data=np.array([1, 0]))
  ```

- **Process Tensor**: Represents a weather forecast as a labeled Markov kernel.

  ```python
  forecast_matrix = np.array([
      [0.8, 0.2],  # Sunny -> Sunny: 0.8, Rainy: 0.2
      [0.4, 0.6]   # Rainy -> Sunny: 0.4, Rainy: 0.6
  ])
  forecast_tensor = FXTensor([[weather_states], [weather_states]], data=forecast_matrix)
  ```

- **Composition**: Predict tomorrow’s weather by composing today’s state with the forecast.

  ```python
  sunny_tomorrow = sunny_today.composition(forecast_tensor)
  sunny_idx = sunny_tomorrow.get_label_index(1, 'Sunny')
  p_sunny = sunny_tomorrow.data[sunny_idx]  # 0.8
  ```

## Advanced Example: Multidimensional System (Labeled)

Model the joint probability of **Season** (Spring, Summer, Other) and **Weather** (Sunny, Rainy) given **Location** (Urban, Rural).

- **Profile**: `[[['Urban', 'Rural']], [['Spring', 'Summer', 'Other'], ['Sunny', 'Rainy']]]`
- **Data**: A 3D array of shape `(2, 3, 2)`.

  ```python
  location_labels = ['Urban', 'Rural']
  season_labels = ['Spring', 'Summer', 'Other']
  weather_labels = ['Sunny', 'Rainy']
  process_data = np.random.rand(2, 3, 2)
  process_data /= process_data.sum(axis=(1, 2), keepdims=True)
  process_tensor = FXTensor([[location_labels], [season_labels, weather_labels]], data=process_data)
  ```

### Key Method Applications

#### `from_json(json_data)`

Creates a tensor from JSON data, loading profile and data to instantiate an FXTensor.

```python
json_data = {
    "profile": [[['a', 'b']], [['x', 'y']]],
    "data": [[0.2, 0.8], [0.6, 0.4]]
}
tensor = FXTensor.from_json(json_data)
assert tensor.labels == ([['a', 'b']], [['x', 'y']])
```

#### `from_strands(profile, strands)`

Creates a tensor from strands (sparse string representations of non-zero elements).

```python
profile = [[['a', 'b']], [['x', 'y', 'z']]]
strands = {
    "[[['a']], [['x']]]": 0.1,
    "[[['a']], [['y']]]": 0.2,
    "[[['a']], [['z']]]": 0.7,
    "[[['b']], [['x']]]": 0.3,
    "[[['b']], [['y']]]": 0.3,
    "[[['b']], [['z']]]": 0.4
}
tensor = FXTensor.from_strands(profile, strands)
assert tensor.labels == ([['a', 'b']], [['x', 'y', 'z']])
```

#### `identity_tensor(list_x)`

Creates an identity tensor for the given dimensions, supporting labeled or numeric inputs.

```python
labels = [['a', 'b']]
id_tensor = FXTensor.identity_tensor(labels)
assert id_tensor.labels == ([labels], [labels])
```

#### `unit_tensor(dims)`

Creates a unit state tensor (all-ones vector) for the given dimensions.

```python
dims = [2, 3]
unit = FXTensor.unit_tensor(dims)
assert unit.profile == [[], dims]
assert np.all(unit.data == 1)
```

#### `delta_tensor(dims)`

Creates a delta tensor (identity matrix) for the given dimensions, used for copying.

```python
dims = [2]
delta = FXTensor.delta_tensor(dims)
assert delta.profile == [[dims], [dims]]
```

#### `conditionalization(concat_start_index)`

Creates a conditional probability distribution from a joint state by dividing at the specified index in codomain.

```python
# Compute P(Weather | Location, Season)
cond_tensor = process_tensor.conditionalization(concat_start_index=2)
assert cond_tensor.labels == ([['Urban', 'Rural'], ['Spring', 'Summer', 'Other']], [['Sunny', 'Rainy']])
```

#### `marginalization(start_B)`

Marginalizes out part of the codomain by summing over it.

```python
# Get P(Season | Location) by marginalizing Weather
season_tensor = process_tensor.marginalization(start_B=2)
assert season_tensor.labels == ([['Urban', 'Rural']], [['Spring', 'Summer', 'Other']])
```

#### `jointification(other)`

Creates a joint state from two state tensors.

```python
# Define another state tensor
traffic_labels = ['Low', 'High']
traffic_state = FXTensor([[], [traffic_labels]], data=np.array([0.7, 0.3]))
# Create joint state
joint_state = process_tensor.jointification(traffic_state)
assert joint_state.labels == ([], [['Urban', 'Rural'], ['Spring', 'Summer', 'Other'], ['Sunny', 'Rainy'], ['Low', 'High']])
```

## Theoretical Background: Relation to Markov Categories

The `fxtensor-salmon` library is designed based on the **Markov Category**, a framework for categorical probability theory.

### Markov Category Basics

- **Objects**: State spaces, represented in `FXTensor` as `domain` or `codomain` (e.g., `[['Urban', 'Rural']]` or `[[2]]`).
- **Morphisms**: Markov kernels (probabilistic transitions), represented by `FXTensor` instances with profile and data.

### Categorical Operations and Methods

1. **Composition (`composition`)**: Combines morphisms `f: A -> B` and `g: B -> C`. Corresponds to connecting wires in string diagrams.
2. **Tensor Product (`tensor_product`)**: Combines independent systems. Represented as side-by-side diagrams.
3. **Discard (`exclamation`)**: Sums over output axes to eliminate them. `exclamation(list_x)` creates a discarding tensor for the specified dimensions.
4. **Copy (`delta_tensor`)**: Deterministic copying operation.

### Probabilistic Properties

- `is_markov()`: Verifies if the tensor satisfies the normalization condition (sum of outputs equals 1 or 0).
- Labeled tensors enable intuitive interpretation via `get_label_index` and `get_index_label`.

## Testing

Tests are implemented in `tests/test_fxtensor.py` using `pytest`.

```bash
pytest
```

## References
- [1] [檜山正幸のキマイラ飼育記 (はてなBlog), マルコフ圏 A First Look -- 圏論的確率論の最良の定式化](https://m-hiyama.hatenablog.com/entry/2020/06/09/154044)
- [2] [檜山正幸のキマイラ飼育記 (はてなBlog), マルコフ圏におけるテンソル計算の手順とコツ](https://m-hiyama.hatenablog.com/entry/2021/04/05/153325)