from __future__ import annotations
import numpy as np
import json
import ast
from typing import List, Tuple, Dict, Any, Union, Optional
from fractions import Fraction

class FXTensor:
    """A tensor with support for string-labeled dimensions and tensor operations."""

    def __init__(
        self,
        profile: Union[
            List[List[Union[int, List[str]]]],
            Tuple[List[int], List[int]]
        ],
        data: Optional[np.ndarray] = None,
    ) -> None:
        if isinstance(profile, tuple):
            domain_dims = list(profile[0])
            codomain_dims = list(profile[1])
            self._labels = None
        else:
            if len(profile) != 2:
                raise ValueError("Invalid profile format")
            is_numeric = True
            for group in profile:
                if group:
                    if not isinstance(group[0], int):
                        is_numeric = False
                    break
            if is_numeric:
                domain_dims = list(profile[0])
                codomain_dims = list(profile[1])
                self._labels = None
            else:
                domain_labels = profile[0] if profile[0] else []
                codomain_labels = profile[1] if profile[1] else []
                self._labels = (domain_labels, codomain_labels)
                domain_dims = [len(dim) for dim in domain_labels]
                codomain_dims = [len(dim) for dim in codomain_labels]
        self._profile = (domain_dims, codomain_dims)

        shape = tuple(domain_dims + codomain_dims)
        if data is not None:
            self.data = np.asarray(data)
            if self.data.shape != shape:
                raise ValueError(f"Data shape {data.shape} does not match profile {shape}")
        else:
            self.data = np.zeros(shape)

    @property
    def profile(self) -> List[List[int]]:
        """Get the tensor's profile as a list of lists [[domain], [codomain]]."""
        return [list(self._profile[0]), list(self._profile[1])]

    @property
    def labels(self) -> Optional[Tuple[List[List[str]], List[List[str]]]]:
        """Get the tensor's string labels."""
        domain = self._labels[0] if self._labels and self._labels[0] else None
        codomain = self._labels[1] if self._labels and self._labels[1] else None
        return (domain, codomain)

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> 'FXTensor':
        """Create a tensor from JSON data."""
        profile = json_data["profile"]
        if len(profile) != 2:
            raise ValueError("Invalid profile format")
        is_numeric = True
        for group in profile:
            if group:
                if not isinstance(group[0], int):
                    is_numeric = False
                break
        if is_numeric:
            shape = tuple(profile[0] + profile[1]) if profile else ()
        else:
            domain_dims = [len(dim) for dim in profile[0]] if profile[0] else []
            codomain_dims = [len(dim) for dim in profile[1]] if profile[1] else []
            shape = tuple(domain_dims + codomain_dims)
        data = np.array(json_data["data"]).reshape(shape)
        return cls(profile, data=data)

    @classmethod
    def from_strands(
        cls, 
        profile: Union[Tuple[List[int], List[int]], List[List[List[str]]]],
        strands: Dict[str, Union[float, Fraction]]
    ) -> 'FXTensor':
        """Create a tensor from strands (string representation)."""
        tensor = cls(profile)
        is_labeled = tensor._labels is not None
        for strand_str, weight in strands.items():
            domain_part, codomain_part = ast.literal_eval(strand_str)
            indices = []
            for part, label_idx in [(domain_part, 0), (codomain_part, 1)]:
                for axis, dim_part in enumerate(part):
                    val = dim_part[0]
                    if is_labeled:
                        idx = tensor._labels[label_idx][axis].index(val)
                    else:
                        idx = val - 1
                    indices.append(idx)
            tensor.data[tuple(indices)] = float(weight)
        return tensor

    def to_json(self) -> dict:
        """Convert the tensor to a JSON-serializable dictionary."""
        if self._labels is not None:
            profile = [self._labels[0], self._labels[1]]
        else:
            profile = [list(self._profile[0]), list(self._profile[1])]
        data = self.data.tolist()
        return {
            "profile": profile,
            "data": data,
            "dtype": str(self.data.dtype)
        }

    def save_to_file(self, filename: str) -> None:
        """Save the tensor to a JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.to_json(), f, indent=2)

    @classmethod
    def load_from_file(cls, filename: str) -> 'FXTensor':
        """Load a tensor from a JSON file."""
        with open(filename, 'r') as f:
            return cls.from_json(json.load(f))

    def composition(self, other: 'FXTensor') -> 'FXTensor':
        """Standard tensor composition."""
        if self._profile[1] != other._profile[0]:
            raise ValueError("Tensors are not composable: codomain of self must match domain of other.")
        self_codomain_axes = list(range(len(self._profile[0]), self.data.ndim))
        other_domain_axes = list(range(len(other._profile[0])))
        new_domain = self._profile[0]
        new_codomain = other._profile[1]
        new_profile = [new_domain, new_codomain]
        new_labels = None
        if self._labels is not None and other._labels is not None:
            new_labels = (self._labels[0], other._labels[1])
        result_data = np.tensordot(self.data, other.data, axes=(self_codomain_axes, other_domain_axes))
        if new_labels and (new_labels[0] or new_labels[1]):
            result_profile = [new_labels[0], new_labels[1]]
        else:
            result_profile = new_profile
        return FXTensor(result_profile, data=result_data)

    def tensor_product(self, other: 'FXTensor') -> 'FXTensor':
        """Perform tensor product operation."""
        new_domain = self._profile[0] + other._profile[0]
        new_codomain = self._profile[1] + other._profile[1]
        new_profile = [new_domain, new_codomain]
        new_domain_labels = (self._labels[0] if self._labels is not None else []) + (other._labels[0] if other._labels is not None else [])
        new_codomain_labels = (self._labels[1] if self._labels is not None else []) + (other._labels[1] if other._labels is not None else [])
        new_labels = (new_domain_labels, new_codomain_labels) if new_domain_labels or new_codomain_labels else None
        self_dom_len = len(self._profile[0])
        other_dom_len = len(other._profile[0])
        self_cod_len = len(self._profile[1])
        other_cod_len = len(other._profile[1])
        self_reshaped = self.data.reshape(self._profile[0] + [1]*other_dom_len + self._profile[1] + [1]*other_cod_len)
        other_reshaped = other.data.reshape([1]*self_dom_len + other._profile[0] + [1]*self_cod_len + other._profile[1])
        new_data = self_reshaped * other_reshaped
        if new_labels and (new_labels[0] or new_labels[1]):
            result_profile = [new_labels[0], new_labels[1]]
        else:
            result_profile = new_profile
        return FXTensor(result_profile, data=new_data)

    def is_markov(self) -> bool:
        """Check if the tensor is a Markov tensor."""
        if not self._profile[0]:
            return False
        codomain_axes = tuple(range(len(self._profile[0]), self.data.ndim))
        sums = np.sum(self.data, axis=codomain_axes)
        return np.all(np.isclose(sums, 1) | np.isclose(sums, 0))

    def conditionalization(self, concat_start_index: int) -> 'FXTensor':
        """Create a conditional probability distribution from a joint state."""
        if self._profile[0]:
            raise ValueError("Tensor must be a state (empty domain) for conditionalization")
        split_point = concat_start_index - 1
        if not (0 < concat_start_index <= len(self._profile[1])):
            raise ValueError("concat_start_index is out of bounds")
        new_domain = self._profile[1][:split_point]
        new_codomain = self._profile[1][split_point:]
        new_profile = [new_domain, new_codomain]
        new_labels = None
        if self._labels is not None:
            new_domain_labels = self._labels[1][:split_point]
            new_codomain_labels = self._labels[1][split_point:]
            new_labels = (new_domain_labels, new_codomain_labels)
        sum_over_codomain = np.sum(self.data, axis=tuple(range(split_point, len(self._profile[1]))), keepdims=True)
        sum_over_codomain[sum_over_codomain == 0] = 1
        new_data = self.data / sum_over_codomain
        if new_labels and (new_labels[0] or new_labels[1]):
            result_profile = [new_labels[0], new_labels[1]]
        else:
            result_profile = new_profile
        return FXTensor(result_profile, data=new_data)

    def marginalization(self, start_B: int) -> 'FXTensor':
        """Marginalize out a part of the codomain by summing over it."""
        domain_len = len(self._profile[0])
        codomain_len = len(self._profile[1])
        if not (1 <= start_B <= codomain_len + 1):
            raise ValueError("start_B must be a valid split index in the codomain")
        if start_B > codomain_len:
            return self
        sum_axes = tuple(range(domain_len + start_B - 1, self.data.ndim))
        new_data = np.sum(self.data, axis=sum_axes)
        new_codomain = self._profile[1][:start_B - 1]
        new_profile = [self._profile[0], new_codomain]
        new_labels = None
        if self._labels is not None:
            new_labels = (self._labels[0], self._labels[1][:start_B - 1])
        if new_labels and (new_labels[0] or new_labels[1]):
            result_profile = [new_labels[0], new_labels[1]]
        else:
            result_profile = new_profile
        return FXTensor(result_profile, data=new_data)

    def jointification(self, other: 'FXTensor') -> 'FXTensor':
        """Create a joint state from two tensors."""
        if self._profile[0] or other._profile[0]:
            raise ValueError("Both tensors must be states (empty domain) for jointification")
        self_expanded = self.data.reshape(self._profile[1] + [1] * len(other._profile[1]))
        result_data = self_expanded * other.data
        new_codomain = self._profile[1] + other._profile[1]
        new_profile = [[], new_codomain]
        new_labels = None
        if self._labels is not None and other._labels is not None:
            new_labels = ([], self._labels[1] + other._labels[1])
        if new_labels and (new_labels[0] or new_labels[1]):
            result_profile = [new_labels[0], new_labels[1]]
        else:
            result_profile = new_profile
        return FXTensor(result_profile, data=result_data)

    def partial_composition(self, other: 'FXTensor', concat_start_index: int) -> 'FXTensor':
        """Perform partial composition."""
        idx = concat_start_index - 1
        a_part = self._profile[1][:idx]
        b_part = self._profile[1][idx:]
        if other._profile[0][:len(b_part)] != b_part:
            raise ValueError("Tensors are not suitable for partial composition")
        id_a = FXTensor.identity_tensor(a_part)
        id_a_otimes_other = id_a.tensor_product(other)
        len_a = len(a_part)
        len_o_dom = len(other._profile[0])
        len_a_cod = len(a_part)
        transpose_order = list(range(len_a, len_a + len_o_dom)) + \
                          list(range(len_a)) + \
                          list(range(len_a + len_o_dom, len_a + len_o_dom + len_a_cod)) + \
                          list(range(len_a + len_o_dom + len_a_cod, id_a_otimes_other.data.ndim))
        transposed_data = id_a_otimes_other.data.transpose(transpose_order)
        new_codomain = a_part + other._profile[1]
        reshaped_other = FXTensor([self._profile[1], new_codomain], data=transposed_data.reshape(tuple(self._profile[1] + new_codomain)))
        return self.composition(reshaped_other)

    def to_original_dict(self) -> Dict[str, Any]:
        """Convert tensor to original dictionary format with 1-based indexing."""
        strands = {}
        domain_len = len(self._profile[0])
        for idx in np.ndindex(self.data.shape):
            weight = self.data[idx]
            if weight != 0:
                domain_idx = [d + 1 for d in idx[:domain_len]]
                codomain_idx = [c + 1 for c in idx[domain_len:]]
                strand_key = str([domain_idx, codomain_idx])
                strands[strand_key] = weight
        return {"profile": self.profile, "strands": strands}

    @staticmethod
    def swap(list_a: List[int], list_b: List[int]) -> 'FXTensor':
        """Create a swap tensor."""
        domain = list_a + list_b
        codomain = list_b + list_a
        profile = [domain, codomain]
        shape = tuple(domain + codomain)
        data = np.zeros(shape)
        len_a = len(list_a)
        for idx in np.ndindex(*domain):
            idx_a = idx[:len_a]
            idx_b = idx[len_a:]
            to_idx = idx_b + idx_a
            full_idx = tuple(list(idx) + list(to_idx))
            data[full_idx] = 1
        return FXTensor(profile, data=data)

    def get_label_index(self, axis: int, label: str) -> int:
        """
        Get the index of a label for a given axis.
        """
        if self._labels is None:
            raise ValueError("No labels defined for this tensor")
        domain_len = len(self._profile[0])
        if axis < domain_len:
            return self._labels[0][axis].index(label)
        else:
            return self._labels[1][axis - domain_len].index(label)

    def get_index_label(self, axis: int, index: int) -> str:
        """
        Get the label for a given axis and index.
        """
        if self._labels is None:
            raise ValueError("No labels defined for this tensor")
        domain_len = len(self._profile[0])
        if axis < domain_len:
            return self._labels[0][axis][index]
        else:
            return self._labels[1][axis - domain_len][index]

    def __repr__(self) -> str:
        """Return a string representation of the FXTensor."""
        if self._labels is not None:
            domain_labels = f"[{', '.join(['[' + ', '.join(dim) + ']' for dim in self._labels[0]])}]" if self._labels[0] else "[]"
            codomain_labels = f"[{', '.join(['[' + ', '.join(dim) + ']' for dim in self._labels[1]])}]" if self._labels[1] else "[]"
            return f"FXTensor(profile={self.profile}, labels=({domain_labels}, {codomain_labels}), shape={self.data.shape})"
        else:
            return f"FXTensor(profile={self.profile}, shape={self.data.shape})"

    @staticmethod
    def exclamation(list_x: List[int]) -> 'FXTensor':
        """Create an exclamation tensor (discarding)."""
        profile = [list_x, []]
        data = np.ones(tuple(list_x))
        return FXTensor(profile, data=data)

    def first_marginalization(self, concat_start_index: int) -> 'FXTensor':
        """Marginalize out the second part of the codomain."""
        start_B = concat_start_index - 1
        a_sizes = self._profile[1][:start_B]
        b_sizes = self._profile[1][start_B:]
        unit_a = FXTensor.identity_tensor(a_sizes)
        excl_b = FXTensor.exclamation(b_sizes)
        tp = unit_a.tensor_product(excl_b)
        return self.composition(tp)

    def second_marginalization(self, concat_start_index: int) -> 'FXTensor':
        """Marginalize out the first part of the codomain."""
        start_B = concat_start_index - 1
        a_sizes = self._profile[1][:start_B]
        b_sizes = self._profile[1][start_B:]
        excl_a = FXTensor.exclamation(a_sizes)
        unit_b = FXTensor.identity_tensor(b_sizes)
        tp = excl_a.tensor_product(unit_b)
        return self.composition(tp)

    def discard_prefix(self, start_B: int) -> 'FXTensor':
        """Discard a prefix of the codomain by summing over it."""
        domain_len = len(self._profile[0])
        codomain_len = len(self._profile[1])
        if not (1 <= start_B <= codomain_len + 1):
            raise ValueError("start_B must be a valid split index in the codomain")
        if start_B == 1:
            return self
        num_axes_to_sum = start_B - 1
        sum_axes = tuple(range(domain_len, domain_len + num_axes_to_sum))
        new_data = np.sum(self.data, axis=sum_axes)
        new_codomain = self._profile[1][num_axes_to_sum:]
        new_profile = [self._profile[0], new_codomain]
        new_labels = None
        if self._labels is not None:
            new_labels = (self._labels[0], self._labels[1][num_axes_to_sum:])
        if new_labels and (new_labels[0] or new_labels[1]):
            result_profile = [new_labels[0], new_labels[1]]
        else:
            result_profile = new_profile
        return FXTensor(result_profile, data=new_data)

    @classmethod
    def identity_tensor(cls, list_x: Union[List[int], List[List[str]]]) -> 'FXTensor':
        """Create an identity tensor."""
        if not list_x:
            return cls([[], []], data=np.array(1.0))
        if isinstance(list_x[0], int):
            dims = list_x
        else:
            dims = [len(dim) for dim in list_x]
        data = np.eye(np.prod(dims)).reshape(dims + dims)
        if isinstance(list_x[0], list):
            return cls([list_x, list_x], data=data)
        else:
            return cls([dims, dims], data=data)

    @classmethod
    def unit_tensor(cls, dims: List[int]) -> 'FXTensor':
        """Create a unit tensor (all ones) with the given dimensions."""
        return cls([[], dims], data=np.ones(tuple(dims)))

    @classmethod
    def delta_tensor(cls, dims: List[int]) -> 'FXTensor':
        """Create a delta tensor (identity matrix) with the given dimensions."""
        return cls.identity_tensor(dims)