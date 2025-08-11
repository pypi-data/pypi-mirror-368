import numpy as np
import json
import ast
from typing import List, Tuple, Dict, Any

class FXTensor:
    """A tensor class for functional programming with tensors.
    
    Attributes:
        profile: A tuple of two lists representing domain and codomain dimensions
        data: Numpy array containing the tensor data
    """
    
    def __init__(self, profile: Tuple[List[int], List[int]], data: np.ndarray = None):
        """Initialize a tensor with a given profile and optional data.
        
        Args:
            profile: A tuple of two lists representing domain and codomain dimensions
            data: Optional numpy array with matching shape
        """
        self.profile = profile
        domain_profile = profile[0]
        codomain_profile = profile[1]
        self.shape = tuple(domain_profile) + tuple(codomain_profile)
        
        if data is None:
            self.data = np.zeros(self.shape)
        else:
            assert data.shape == self.shape, "Data shape must match profile shape"
            self.data = data

    # Creation Methods
    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> 'FXTensor':
        """Create a tensor from JSON data."""
        profile = json_data["profile"]
        domain_profile = profile[0]
        codomain_profile = profile[1]
        shape = tuple(domain_profile) + tuple(codomain_profile)
        data = np.array(json_data["data"]).reshape(shape)
        
        return cls(profile, data=data)

    @classmethod
    def from_strands(cls, profile: Tuple[List[int], List[int]], strands: Dict[str, float]) -> 'FXTensor':
        """Create a tensor from strands (string representation)."""
        tensor = cls(profile)
        for strand_str, weight in strands.items():
            strand = ast.literal_eval(strand_str)
            domain_idx = tuple(x - 1 for x in strand[0])
            codomain_idx = tuple(x - 1 for x in strand[1])
            idx = domain_idx + codomain_idx
            tensor.data[idx] = weight
        return tensor

    # Special Tensors
    @classmethod
    def unit_tensor(cls, list_x: List[int]) -> 'FXTensor':
        """Create a unit tensor (state of all ones)."""
        profile = [[], list_x]
        shape = tuple(list_x)
        data = np.ones(shape)
        return cls(profile, data=data)

    @classmethod
    def identity_tensor(cls, list_x: List[int]) -> 'FXTensor':
        """Create an identity tensor."""
        profile = [list_x, list_x]
        shape = tuple(list_x) + tuple(list_x)
        size = int(np.prod(list_x))
        data = np.identity(size).reshape(shape)
        return cls(profile, data=data)

    @classmethod
    def delta(cls, list_x: List[int]) -> 'FXTensor':
        """Create a delta tensor (copying)."""
        domain = list_x
        codomain = list_x + list_x
        profile = [domain, codomain]
        shape = tuple(domain) + tuple(codomain)
        data = np.zeros(shape)
        
        for idx in np.ndindex(*tuple(domain)):
            full_idx = idx + idx + idx
            data[full_idx] = 1
        
        return cls(profile, data=data)

    # Serialization
    def to_json(self) -> dict:
        """Convert the tensor to a JSON-serializable dictionary."""
        if not self.profile[0]: # It's a state
            strands = []
        else:
            domain_indices = list(np.ndindex(*self.profile[0]))
            codomain_indices = list(np.ndindex(*self.profile[1]))
            strands = [{'from': list(d), 'to': list(c)} for d in domain_indices for c in codomain_indices]

        return {
            "profile": self.profile,
            "strands": strands,
            "data": self.data.flatten().tolist()
        }

    def save_to_file(self, filename: str) -> None:
        """Save tensor to JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.to_json(), f, indent=2)

    @classmethod
    def load_from_file(cls, filename: str) -> 'FXTensor':
        """Load tensor from JSON file."""
        with open(filename, 'r') as f:
            json_data = json.load(f)
        return cls.from_json(json_data)

    # Operations
    def composition(self, other: 'FXTensor') -> 'FXTensor':
        """Standard tensor composition."""
        if self.profile[1] != other.profile[0]:
            raise ValueError("Tensors are not composable: codomain of self must match domain of other.")
        
        self_codomain_axes = list(range(len(self.profile[0]), len(self.shape)))
        other_domain_axes = list(range(len(other.profile[0])))
        
        result_data = np.tensordot(self.data, other.data, axes=(self_codomain_axes, other_domain_axes))
        result_profile = [self.profile[0], other.profile[1]]
        return FXTensor(result_profile, data=result_data)

    def tensor_product(self, other: 'FXTensor') -> 'FXTensor':
        """Perform tensor product operation."""
        new_domain = self.profile[0] + other.profile[0]
        new_codomain = self.profile[1] + other.profile[1]
        new_profile = [new_domain, new_codomain]

        # Reshape self.data and other.data to align axes for tensor product
        self_dom_len = len(self.profile[0])
        other_dom_len = len(other.profile[0])
        self_cod_len = len(self.profile[1])
        other_cod_len = len(other.profile[1])

        self_reshaped = self.data.reshape(self.profile[0] + [1]*other_dom_len + self.profile[1] + [1]*other_cod_len)
        other_reshaped = other.data.reshape([1]*self_dom_len + other.profile[0] + [1]*self_cod_len + other.profile[1])

        new_data = self_reshaped * other_reshaped
        return FXTensor(new_profile, data=new_data)

    # Markov Operations
    def is_markov(self) -> bool:
        """Check if the tensor is a Markov tensor."""
        if not self.profile[0]:
            return False
        
        codomain_axes = tuple(range(len(self.profile[0]), self.data.ndim))
        sums = np.sum(self.data, axis=codomain_axes)
        # For a valid Markov tensor, each row must sum to 1.
        # We also consider rows that sum to 0 as valid (e.g., from an impossible event).
        return np.all(np.isclose(sums, 1) | np.isclose(sums, 0))

    def conditionalization(self, concat_start_index: int) -> 'FXTensor':
        """Create a conditional probability distribution from a joint state."""
        if self.profile[0]:  # Check if domain is not empty
            raise ValueError("Tensor must be a state (empty domain) for conditionalization")

        codomain = self.profile[1]
        split_point = concat_start_index - 1

        if not (0 < concat_start_index <= len(codomain)):
            raise ValueError("concat_start_index is out of bounds")

        new_domain = codomain[:split_point]
        new_codomain = codomain[split_point:]

        # Normalize the data to create a valid conditional probability distribution
        sum_over_codomain = np.sum(self.data, axis=tuple(range(split_point, len(codomain))), keepdims=True)
        # Avoid division by zero for zero-probability events
        sum_over_codomain[sum_over_codomain == 0] = 1
        new_data = self.data / sum_over_codomain

        return FXTensor([new_domain, new_codomain], data=new_data)

    def marginalization(self, start_B: int) -> 'FXTensor':
        """Marginalize out a part of the codomain by summing over it."""
        domain_len = len(self.profile[0])
        codomain = self.profile[1]
        
        if not (1 <= start_B <= len(codomain) + 1):
            raise ValueError("start_B must be a valid split index in the codomain")

        # If start_B is beyond the last element, it means no marginalization, return self.
        if start_B > len(codomain):
            return self

        # Axes to sum over are in the codomain part of the data shape
        sum_axes = tuple(range(domain_len + start_B - 1, self.data.ndim))
        
        new_data = np.sum(self.data, axis=sum_axes)
        new_codomain = codomain[:start_B-1]
        new_profile = [self.profile[0], new_codomain]
        
        return FXTensor(new_profile, data=new_data)

    def jointification(self, other: 'FXTensor') -> 'FXTensor':
        """Create a joint state from two tensors."""
        if not (self.profile[0] == [] and other.profile[0] == []):
            raise ValueError("Both tensors must be states (empty domain) for jointification")
        
        a = self.profile[1]
        b = other.profile[1]
        
        self_expanded = self.data.reshape(tuple(a) + (1,) * len(b))
        result_data = self_expanded * other.data
        result_profile = [[], a + b]
        return FXTensor(result_profile, data=result_data)

    def partial_composition(self, other: 'FXTensor', concat_start_index: int) -> 'FXTensor':
        """Perform partial composition."""
        # Decompose profiles using 0-based index
        idx = concat_start_index - 1
        a_part = self.profile[1][:idx]
        b_part = self.profile[1][idx:]
        if other.profile[0][:len(b_part)] != b_part:
            raise ValueError("Tensors are not suitable for partial composition")
        c_part = other.profile[0][len(b_part):]

        # Create identity tensor for a_part
        id_a = FXTensor.identity_tensor(a_part)

        # Tensor product of id_a and other
        id_a_otimes_other = id_a.tensor_product(other)

        # Transpose and reshape for composition
        new_codomain = a_part + other.profile[1]
        
        # Build the transpose order dynamically
        # Order for a_part's domain, other's domain, a_part's codomain, other's codomain
        len_a_dom = len(id_a.profile[0])
        len_o_dom = len(other.profile[0])
        len_a_cod = len(id_a.profile[1])
        
        transpose_order = list(range(len_a_dom, len_a_dom + len_o_dom)) + \
                          list(range(len_a_dom)) + \
                          list(range(len_a_dom + len_o_dom, len_a_dom + len_o_dom + len_a_cod)) + \
                          list(range(len_a_dom + len_o_dom + len_a_cod, len(id_a_otimes_other.data.shape)))
        
        transposed_data = id_a_otimes_other.data.transpose(transpose_order)

        reshaped_other = FXTensor(
            [self.profile[1], new_codomain],
            data=transposed_data.reshape(self.profile[1] + new_codomain)
        )

        # Perform composition
        return self.composition(reshaped_other)

    # Conversion Methods
    def to_original_dict(self) -> Dict[str, Any]:
        """Convert tensor to original dictionary format with 1-based indexing."""
        profile = self.profile
        strands = {}
        total_domain_dims = len(self.profile[0])
        
        for idx in np.ndindex(self.data.shape):
            weight = self.data[idx]
            if weight != 0:
                domain_idx = [d + 1 for d in idx[:total_domain_dims]]
                codomain_idx = [c + 1 for c in idx[total_domain_dims:]]
                strand_key = str([domain_idx, codomain_idx])
                strands[strand_key] = weight
        
        return {"profile": profile, "strands": strands}

    @staticmethod
    def swap(list_a: List[int], list_b: List[int]) -> 'FXTensor':
        """Create a swap tensor."""
        domain = list_a + list_b
        codomain = list_b + list_a
        profile = [domain, codomain]
        
        len_a = len(list_a)
        len_b = len(list_b)
        
        permutation = list(range(len_a, len_a + len_b)) + list(range(len_a))
        
        identity_data = np.identity(np.prod(domain)).reshape(tuple(domain) * 2)
        result_data = np.transpose(identity_data, permutation + [i + len(domain) for i in range(len(domain))])
        
        shape = tuple(domain) + tuple(codomain)
        data = np.zeros(shape)
        
        from_indices = np.ndindex(*tuple(domain))
        
        for from_idx in from_indices:
            idx_a = from_idx[:len_a]
            idx_b = from_idx[len_a:]
            to_idx = idx_b + idx_a
            full_idx = from_idx + to_idx
            data[full_idx] = 1
            
        return FXTensor(profile, data=data)

    def __repr__(self) -> str:
        """Provide a string representation of the FXTensor instance."""
        return f"FXTensor(profile={self.profile}, shape={self.data.shape})"

    @staticmethod
    def exclamation(list_x: List[int]) -> 'FXTensor':
        """Create an exclamation tensor (discarding)."""
        profile = [list_x, []]
        shape = tuple(list_x)
        data = np.ones(shape)
        return FXTensor(profile, data=data)

    def first_marginalization(self, concat_start_index: int) -> 'FXTensor':
        """Marginalize out the second part of the codomain."""
        codomain = self.profile[1]
        start_B = concat_start_index - 1
        A_sizes = codomain[0:start_B]
        B_sizes = codomain[start_B:]

        unit_A = FXTensor.identity_tensor(A_sizes)
        excl_B = FXTensor.exclamation(B_sizes)
        
        tp = unit_A.tensor_product(excl_B)
        result = self.composition(tp)
        return result

    def second_marginalization(self, concat_start_index: int) -> 'FXTensor':
        """Marginalize out the first part of the codomain."""
        codomain = self.profile[1]
        start_B = concat_start_index - 1
        A_sizes = codomain[0:start_B]
        B_sizes = codomain[start_B:]
        
        excl_A = FXTensor.exclamation(A_sizes)
        unit_B = FXTensor.identity_tensor(B_sizes)
        
        tp = excl_A.tensor_product(unit_B)
        result = self.composition(tp)
        return result

    def discard_prefix(self, start_B: int) -> 'FXTensor':
        """Discard a prefix of the codomain by summing over it."""
        domain_len = len(self.profile[0])
        codomain = self.profile[1]

        if not (1 <= start_B <= len(codomain) + 1):
            raise ValueError("start_B must be a valid split index in the codomain")

        if start_B == 1:
            return self

        # Axes to sum over are the prefix of the codomain
        num_axes_to_sum = start_B - 1
        sum_axes = tuple(range(domain_len, domain_len + num_axes_to_sum))

        new_data = np.sum(self.data, axis=sum_axes)
        new_codomain = codomain[num_axes_to_sum:]
        new_profile = [self.profile[0], new_codomain]

        return FXTensor(new_profile, data=new_data)