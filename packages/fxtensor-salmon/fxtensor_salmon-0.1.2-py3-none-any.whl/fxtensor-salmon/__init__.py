import numpy as np
import json
import ast

class FXTensor:
    def __init__(self, profile, data=None):
        self.profile = profile
        domain_profile = profile[0]
        codomain_profile = profile[1]
        self.shape = tuple(domain_profile) + tuple(codomain_profile)
        if data is None:
            self.data = np.zeros(self.shape)
        else:
            # Ensure the provided data shape matches the profile
            assert data.shape == self.shape, "Data shape must match profile shape"
            self.data = data

    @staticmethod
    def from_json(json_data):
        """Creates an FXTensor instance from a JSON object."""
        profile = json_data["profile"]
        domain_profile = profile[0]
        codomain_profile = profile[1]
        shape = tuple(domain_profile) + tuple(codomain_profile)
        data = np.zeros(shape)
        for strand in json_data["strands"]:
            from_idx = tuple(strand["from"])
            to_idx = tuple(strand["to"])
            full_idx = from_idx + to_idx
            data[full_idx] = strand["weight"]
        return FXTensor(profile, data=data)

    def to_json(self):
        """Converts the FXTensor instance to a JSON serializable dictionary."""
        profile = self.profile
        strands = []
        k = len(self.profile[0]) # Number of dimensions in the domain
        for idx in np.ndindex(self.data.shape):
            if self.data[idx] != 0:
                from_idx = list(idx[:k])
                to_idx = list(idx[k:])
                weight = float(self.data[idx])
                strands.append({"from": from_idx, "to": to_idx, "weight": weight})
        return {"profile": profile, "strands": strands}

    def save_to_file(self, filename):
        """Saves the tensor to a JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.to_json(), f, indent=2)

    @staticmethod
    def load_from_file(filename):
        """Loads a tensor from a JSON file."""
        with open(filename, 'r') as f:
            json_data = json.load(f)
        return FXTensor.from_json(json_data)

    @staticmethod
    def from_strands(profile, strands):
        """Creates a tensor from a dictionary of strands (string representation)."""
        tensor = FXTensor(profile)
        for strand_str, weight in strands.items():
            # Safely evaluate the string representation of the list
            strand = ast.literal_eval(strand_str)
            # Adjust for 1-based indexing if necessary
            domain_idx = tuple(x - 1 for x in strand[0])
            codomain_idx = tuple(x - 1 for x in strand[1])
            idx = domain_idx + codomain_idx
            tensor.data[idx] = weight
        return tensor

    def to_original_dict(self):
        """Converts the tensor back to the original dictionary format with 1-based indexing."""
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

    def composition(self, other):
        """Performs tensor composition (matrix multiplication for tensors)."""
        if self.profile[1] != other.profile[0]:
            raise ValueError("Tensors are not composable: codomain of self must match domain of other.")
        
        # Axes to contract over
        self_codomain_axes = list(range(len(self.profile[0]), len(self.shape)))
        other_domain_axes = list(range(len(other.profile[0])))
        
        result_data = np.tensordot(self.data, other.data, axes=(self_codomain_axes, other_domain_axes))
        result_profile = [self.profile[0], other.profile[1]]
        return FXTensor(result_profile, data=result_data)

    def tensor_product(self, other):
        """Performs the tensor product of two FXTensors."""
        dx, cx = self.profile
        dy, cy = other.profile

        # Reshape self and other to be broadcastable
        self_reshaped_shape = tuple(dx) + (1,) * len(dy) + tuple(cx) + (1,) * len(cy)
        other_reshaped_shape = (1,) * len(dx) + tuple(dy) + (1,) * len(cx) + tuple(cy)
        
        self_reshaped = self.data.reshape(self_reshaped_shape)
        other_reshaped = other.data.reshape(other_reshaped_shape)
        
        # Broadcasting multiplication
        result_data = self_reshaped * other_reshaped
        
        # New profile for the resulting tensor
        result_profile = [dx + dy, cx + cy]
        return FXTensor(result_profile, data=result_data)

    @staticmethod
    def unit_tensor(list_x):
        """Creates a unit tensor (identity)."""
        profile = [list_x, list_x]
        shape = tuple(list_x) + tuple(list_x)
        data = np.identity(np.prod(list_x)).reshape(shape)
        return FXTensor(profile, data=data)

    @staticmethod
    def delta(list_x):
        """Creates a delta tensor (copying)."""
        domain = list_x
        codomain = list_x + list_x
        profile = [domain, codomain]
        shape = tuple(domain) + tuple(codomain)
        data = np.zeros(shape)
        
        # Create an identity matrix of size prod(list_x) x prod(list_x)
        identity_matrix = np.identity(np.prod(list_x))
        # Reshape it to the desired tensor shape
        data = identity_matrix.reshape(tuple(list_x) + tuple(list_x))
        
        # This is a more efficient way to create the delta tensor
        # The previous loop was complex; this creates the same result
        temp_data = np.zeros(tuple(list_x) + tuple(list_x))
        for idx in np.ndindex(*tuple(list_x)):
            temp_data[idx + idx] = 1
        
        final_data = temp_data.reshape(shape)

        return FXTensor(profile, data=final_data)


    @staticmethod
    def exclamation(list_x):
        """Creates an exclamation tensor (discarding)."""
        profile = [list_x, []]
        shape = tuple(list_x)
        data = np.ones(shape)
        return FXTensor(profile, data=data)

    def is_markov(self):
        """Checks if the tensor represents a Markov kernel."""
        codomain_axes = tuple(range(len(self.profile[0]), len(self.shape)))
        if not codomain_axes: # Handle case where codomain is empty
            return np.all(self.data == 1.0)
        row_sums = np.sum(self.data, axis=codomain_axes)
        return np.allclose(row_sums, 1)

    def partial_composition(self, other, concat_start_index):
        """Performs partial composition."""
        codomain_profile = self.profile[1]
        c_part = codomain_profile[concat_start_index - 1:]
        unit_c = FXTensor.unit_tensor(c_part)
        tp = other.tensor_product(unit_c)
        return self.composition(tp)

    def jointification(self, other):
        """Creates a joint state from two tensors."""
        if self.profile[0] != [] or other.profile[0] != self.profile[1]:
            raise ValueError("Tensors are not suitable for jointification")
        a = self.profile[1]
        b = other.profile[1]
        
        # Reshape self.data to be broadcastable with other.data
        self_expanded = self.data.reshape(tuple(a) + (1,) * len(b))
        
        result_data = self_expanded * other.data
        result_profile = [[], a + b]
        return FXTensor(result_profile, data=result_data)

    def conditionalization(self, concat_start_index):
        """Creates a conditional probability distribution."""
        if self.profile[0] != []:
            raise ValueError("Tensor must have empty domain for conditionalization")
        codomain = self.profile[1]
        start_B = concat_start_index - 1
        A_sizes = codomain[0:start_B]
        B_sizes = codomain[start_B:]
        
        # Sum over the dimensions of B to get the marginal distribution of A
        sum_axes = tuple(range(len(A_sizes), len(A_sizes) + len(B_sizes)))
        marginal_A = np.sum(self.data, axis=sum_axes)
        
        # Expand marginal_A to be broadcastable with the original data
        marginal_A_expanded_shape = tuple(A_sizes) + (1,) * len(B_sizes)
        marginal_A_expanded = marginal_A.reshape(marginal_A_expanded_shape)
        
        # Avoid division by zero
        # Where marginal_A is zero, the conditional probability is also zero.
        result_data = np.divide(self.data, marginal_A_expanded, out=np.zeros_like(self.data), where=marginal_A_expanded!=0)
        
        result_profile = [A_sizes, B_sizes]
        return FXTensor(result_profile, data=result_data)

    def first_marginalization(self, concat_start_index):
        """Marginalizes out the second part of the codomain."""
        codomain = self.profile[1]
        start_B = concat_start_index - 1
        A_sizes = codomain[0:start_B]
        B_sizes = codomain[start_B:]
        
        unit_A = FXTensor.unit_tensor(A_sizes)
        excl_B = FXTensor.exclamation(B_sizes)
        
        tp = unit_A.tensor_product(excl_B)
        result = self.composition(tp)
        return result

    def second_marginalization(self, concat_start_index):
        """Marginalizes out the first part of the codomain."""
        codomain = self.profile[1]
        start_B = concat_start_index - 1
        A_sizes = codomain[0:start_B]
        B_sizes = codomain[start_B:]
        
        excl_A = FXTensor.exclamation(A_sizes)
        unit_B = FXTensor.unit_tensor(B_sizes)
        
        tp = excl_A.tensor_product(unit_B)
        result = self.composition(tp)
        return result

    @staticmethod
    def swap(list_a, list_b):
        """Creates a swap tensor."""
        domain = list_a + list_b
        codomain = list_b + list_a
        profile = [domain, codomain]
        
        # Create a permutation of axes
        len_a = len(list_a)
        len_b = len(list_b)
        
        # The permutation will move the block of axes for 'a' to the end
        # and the block for 'b' to the beginning.
        # Original axes: 0, 1, ..., len_a-1, len_a, ..., len_a+len_b-1
        # New axes:      len_a, ..., len_a+len_b-1, 0, 1, ..., len_a-1
        permutation = list(range(len_a, len_a + len_b)) + list(range(len_a))
        
        # Create an identity tensor and transpose its domain axes
        identity_data = np.identity(np.prod(domain)).reshape(tuple(domain) * 2)
        result_data = np.transpose(identity_data, permutation + [i + len(domain) for i in range(len(domain))])
        
        # This is a more direct way to create the swap tensor
        shape = tuple(domain) + tuple(codomain)
        data = np.zeros(shape)
        
        # Iterate over the domain indices
        from_indices = np.ndindex(*tuple(domain))
        
        for from_idx in from_indices:
            idx_a = from_idx[:len_a]
            idx_b = from_idx[len_a:]
            to_idx = idx_b + idx_a
            full_idx = from_idx + to_idx
            data[full_idx] = 1
            
        return FXTensor(profile, data=data)

    def __repr__(self):
        """Provides a string representation of the FXTensor instance."""
        return f"FXTensor(profile={self.profile}, shape={self.data.shape})"