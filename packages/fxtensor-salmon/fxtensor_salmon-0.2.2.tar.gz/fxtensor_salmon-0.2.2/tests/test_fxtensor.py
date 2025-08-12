import pytest
import numpy as np
import os
from fxtensor_salmon import FXTensor

@pytest.fixture
def tensor_a():
    """A standard tensor for testing."""
    return FXTensor([[2], [3]], data=np.random.rand(2, 3))

@pytest.fixture
def tensor_b():
    """Another standard tensor for testing composition."""
    return FXTensor([[3], [4]], data=np.random.rand(3, 4))

@pytest.fixture
def state_tensor():
    """A state tensor (empty domain) for testing."""
    return FXTensor([[], [2, 3]], data=np.random.rand(2, 3))


class TestSerialization:
    def test_json_serialization_deserialization(self):
        """Test JSON serialization and deserialization."""
        profile = [[2, 3], [4, 5]]
        data = np.random.rand(2, 3, 4, 5)
        tensor = FXTensor(profile, data=data)
        
        json_dict = tensor.to_json()
        expected_profile = [[2, 3], [4, 5]]
        assert json_dict["profile"] == expected_profile
        assert json_dict["data"] == data.tolist()

        reconstructed_tensor = FXTensor.from_json(json_dict)
        assert reconstructed_tensor.profile == profile
        assert np.allclose(reconstructed_tensor.data, data)

    def test_file_io(self, tmp_path):
        """Test saving to and loading from a file."""
        profile = [[2], [3]]
        data = np.random.rand(2, 3)
        tensor = FXTensor(profile, data=data)
        
        filename = tmp_path / "test_tensor.json"
        tensor.save_to_file(str(filename))
        assert os.path.exists(filename)

        loaded_tensor = FXTensor.load_from_file(str(filename))
        assert loaded_tensor.profile == profile
        assert np.allclose(loaded_tensor.data, data)


class TestSpecialTensors:
    def test_unit_tensor(self):
        """Test unit tensor creation (state of all ones)."""
        unit_tensor = FXTensor.unit_tensor([2, 3])
        expected_profile = [[], [2, 3]]
        expected_data = np.ones((2, 3))
        assert unit_tensor.profile == expected_profile
        assert np.array_equal(unit_tensor.data, expected_data)

    def test_identity_tensor(self):
        """Test identity tensor creation."""
        identity = FXTensor.identity_tensor([2, 3])
        assert identity.profile == [[2, 3], [2, 3]]
        assert identity.data.shape == (2, 3, 2, 3)
        size = 2 * 3
        expected_data = np.identity(size).reshape(2, 3, 2, 3)
        assert np.array_equal(identity.data, expected_data)

    def test_delta_tensor(self):
        """Test delta tensor creation."""
        delta_tensor = FXTensor.delta_tensor([2, 3])
        assert delta_tensor.profile == [[2, 3], [2, 3]]
        assert delta_tensor.data.shape == (2, 3, 2, 3)

    def test_exclamation_tensor(self):
        """Test exclamation tensor creation."""
        excl_tensor = FXTensor.exclamation([2, 3])
        assert excl_tensor.profile == [[2, 3], []]
        assert np.allclose(excl_tensor.data, np.ones((2, 3)))

    def test_scalar_tensor(self):
        """Test scalar tensor (empty profile)."""
        scalar = FXTensor([[], []], data=np.array(5))
        assert scalar.profile == [[], []]
        assert scalar.data.shape == ()
        assert scalar.data == 5


class TestTensorOperations:
    def test_composition(self, tensor_a, tensor_b):
        """Test tensor composition."""
        result = tensor_a.composition(tensor_b)
        assert result.profile == [[2], [4]]
        assert result.data.shape == (2, 4)

    def test_composition_with_identity(self, tensor_a):
        """Test that composing with an identity tensor yields the original tensor."""
        identity = FXTensor.identity_tensor([3])
        result = tensor_a.composition(identity)
        assert result.profile == tensor_a.profile
        assert np.allclose(result.data, tensor_a.data)

    def test_tensor_product(self, tensor_a, tensor_b):
        """Test tensor product operation."""
        result = tensor_a.tensor_product(tensor_b)
        assert result.profile == [[2, 3], [3, 4]]
        assert result.data.shape == (2, 3, 3, 4)

    def test_jointification(self, state_tensor):
        """Test jointification operation."""
        other_state = FXTensor([[], [4]], data=np.random.rand(4))
        result = state_tensor.jointification(other_state)
        assert result.profile == [[], [2, 3, 4]]
        assert result.data.shape == (2, 3, 4)

    def test_partial_composition(self):
        """Test partial composition operation."""
        tensor_a = FXTensor([[2], [3, 4]], data=np.random.rand(2, 3, 4))
        tensor_b = FXTensor([[3, 4], [5]], data=np.random.rand(3, 4, 5))
        result = tensor_a.partial_composition(tensor_b, 1)
        assert result.profile == [[2], [5]]
        assert result.data.shape == (2, 5)

    def test_marginalization(self, state_tensor):
        """Test marginalization operation."""
        # state_tensor has profile [[], [2, 3]]. Marginalize out the second dimension (size 3).
        result = state_tensor.marginalization(2)
        assert result.profile == [[], [2]]
        assert result.data.shape == (2,)

    def test_discard_prefix_all(self, state_tensor):
        """Test discarding the entire prefix, resulting in the same tensor."""
        result = state_tensor.discard_prefix(1)
        assert result.profile == state_tensor.profile
        np.testing.assert_array_equal(result.data, state_tensor.data)

    def test_discard_prefix_one(self, state_tensor):
        """Test discarding the first element of the codomain."""
        result = state_tensor.discard_prefix(2)
        assert result.profile == [[], [3]]
        assert result.data.shape == (3,)

    def test_composition_incompatible_fails(self, tensor_a):
        """Test composition fails for incompatible tensors."""
        incompatible_tensor = FXTensor([[4], [5]], data=np.random.rand(4, 5))
        with pytest.raises(ValueError, match="Tensors are not composable"):
            tensor_a.composition(incompatible_tensor)

    def test_partial_composition_incompatible_fails(self):
        """Test partial composition fails for incompatible tensors."""
        tensor_a = FXTensor([[2], [3, 4]], data=np.random.rand(2, 3, 4))
        tensor_b = FXTensor([[5], [6]], data=np.random.rand(5, 6))
        with pytest.raises(ValueError, match="Tensors are not suitable for partial composition"):
            tensor_a.partial_composition(tensor_b, 2)


class TestMarkovOperations:
    def test_is_markov(self):
        """Test is_markov method for various cases."""
        markov_tensor = FXTensor([[2], [3]], data=np.array([[0.1, 0.2, 0.7], [0.2, 0.3, 0.5]]))
        assert markov_tensor.is_markov()

        non_markov_tensor = FXTensor([[2], [3]], data=np.array([[0.1, 0.2, 0.7], [0.2, 0.3, 0.6]]))
        assert not non_markov_tensor.is_markov()

        state_as_non_markov = FXTensor.unit_tensor([2, 3])
        assert not state_as_non_markov.is_markov()

    def test_conditionalization(self, state_tensor):
        """Test conditionalization operation with a valid state."""
        result = state_tensor.conditionalization(2)
        assert result.profile == [[2], [3]]
        assert result.is_markov()

    def test_conditionalization_on_non_state_fails(self, tensor_a):
        """Test conditionalization fails on a non-state tensor."""
        with pytest.raises(ValueError, match="Tensor must be a state"):
            tensor_a.conditionalization(1)

    def test_conditionalization_out_of_bounds_fails(self, state_tensor):
        """Test conditionalization fails for out-of-bounds index."""
        with pytest.raises(ValueError, match="concat_start_index is out of bounds"):
            state_tensor.conditionalization(3)

    def test_conditionalization_with_zero_slice(self):
        """Test conditionalization where a slice sums to zero."""
        joint_data = np.array([[0.1, 0.2], [0.0, 0.0]])
        joint_tensor = FXTensor([[], [2, 2]], data=joint_data)
        cond_tensor = joint_tensor.conditionalization(2)
        
        expected_data = np.array([[1/3, 2/3], [0.0, 0.0]])
        assert cond_tensor.is_markov()
        np.testing.assert_allclose(cond_tensor.data, expected_data)


class TestStringLabels:
    def test_create_with_string_labels(self):
        """Test creating a tensor with string labels."""
        profile = [[['a', 'b']], [['x', 'y', 'z']]]
        data = np.array([
            [0.1, 0.2, 0.7],  # a -> x, y, z
            [0.3, 0.3, 0.4]   # b -> x, y, z
        ])
        tensor = FXTensor(profile, data=data)
        
        assert tensor.profile == [[2], [3]]
        assert tensor.labels == ([['a', 'b']], [['x', 'y', 'z']])
        assert np.array_equal(tensor.data, data)

    def test_from_strands(self):
        """Test creating a tensor from strands with string labels."""
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
        
        assert tensor.profile == [[2], [3]]
        assert tensor.labels == ([['a', 'b']], [['x', 'y', 'z']])
        assert np.allclose(tensor.data, [
            [0.1, 0.2, 0.7],
            [0.3, 0.3, 0.4]
        ])

    def test_get_label_index(self):
        """Test getting index from label."""
        profile = [[['a', 'b']], [['x', 'y', 'z']]]
        tensor = FXTensor(profile, data=np.zeros((2, 3)))
        
        assert tensor.get_label_index(0, 'a') == 0
        assert tensor.get_label_index(0, 'b') == 1
        assert tensor.get_label_index(1, 'x') == 0
        assert tensor.get_label_index(1, 'y') == 1
        assert tensor.get_label_index(1, 'z') == 2
        
        with pytest.raises(ValueError):
            tensor.get_label_index(0, 'c')

    def test_get_index_label(self):
        """Test getting label from index."""
        profile = [[['a', 'b']], [['x', 'y', 'z']]]
        tensor = FXTensor(profile, data=np.zeros((2, 3)))
        
        assert tensor.get_index_label(0, 0) == 'a'
        assert tensor.get_index_label(0, 1) == 'b'
        assert tensor.get_index_label(1, 0) == 'x'
        assert tensor.get_index_label(1, 1) == 'y'
        assert tensor.get_index_label(1, 2) == 'z'

    def test_json_roundtrip_with_labels(self):
        """Test JSON serialization/deserialization with string labels."""
        profile = [[['a', 'b']], [['x', 'y', 'z']]]
        data = np.array([
            [0.1, 0.2, 0.7],
            [0.3, 0.3, 0.4]
        ])
        tensor = FXTensor(profile, data=data)
        
        # Convert to JSON and back
        json_dict = tensor.to_json()
        reconstructed = FXTensor.from_json(json_dict)
        
        assert reconstructed.profile == tensor.profile
        assert reconstructed.labels == tensor.labels
        assert np.allclose(reconstructed.data, tensor.data)

    def test_composition_with_labels(self):
        """Test composition with tensors that have string labels."""
        # First tensor: P(Y|X) where X={a,b}, Y={x,y}
        tensor1 = FXTensor(
            [[['a', 'b']], [['x', 'y']]],
            data=np.array([
                [0.2, 0.8],  # a -> x, y
                [0.6, 0.4]   # b -> x, y
            ])
        )
        
        # Second tensor: P(Z|Y) where Y={x,y}, Z={p,q}
        tensor2 = FXTensor(
            [[['x', 'y']], [['p', 'q']]],
            data=np.array([
                [0.3, 0.7],  # x -> p, q
                [0.9, 0.1]   # y -> p, q
            ])
        )
        
        # Compose: P(Z|X) = P(Y|X) ; P(Z|Y)
        result = tensor1.composition(tensor2)
        
        # Check the result
        assert result.profile == [[2], [2]]
        assert result.labels == ([['a', 'b']], [['p', 'q']])
        
        # Expected result (matrix multiplication)
        expected_data = np.array([
            [0.2*0.3 + 0.8*0.9, 0.2*0.7 + 0.8*0.1],  # a -> p, q
            [0.6*0.3 + 0.4*0.9, 0.6*0.7 + 0.4*0.1]   # b -> p, q
        ])
        assert np.allclose(result.data, expected_data)

    def test_tensor_product_with_labels(self):
        """Test tensor product with tensors that have string labels."""
        # First tensor: P(X) where X={a,b}
        tensor1 = FXTensor(
            [[], [['a', 'b']]],
            data=np.array([0.3, 0.7])
        )
        
        # Second tensor: P(Y) where Y={x,y,z}
        tensor2 = FXTensor(
            [[], [['x', 'y', 'z']]],
            data=np.array([0.2, 0.3, 0.5])
        )
        
        # Tensor product: P(X,Y) = P(X) ⊗ P(Y)
        result = tensor1.tensor_product(tensor2)
        
        # Check the result
        assert result.profile == [[], [2, 3]]
        assert result.labels == (None, [['a', 'b'], ['x', 'y', 'z']])
        
        # Expected result (outer product)
        expected_data = np.outer(
            np.array([0.3, 0.7]),
            np.array([0.2, 0.3, 0.5])
        )
        assert np.allclose(result.data, expected_data)