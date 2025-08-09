
import torch
from torch.nn.utils.rnn import pad_sequence

class CollateFunctions:
    """
    Collection of static collate functions for different model/data types.
    """

    @staticmethod
    def collate_fn_mlp(batch):
        """
        Collate function for MLP models.
        Assumes each item in batch is (input_tensor, target_tensor) with fixed size.
        """
        inputs, targets = zip(*batch)
        # Ensure all are tensors
        inputs = [tensor if isinstance(tensor, torch.Tensor) else torch.tensor(tensor) for tensor in inputs]
        targets = [tensor if isinstance(tensor, torch.Tensor) else torch.tensor(tensor) for tensor in targets]
        # Check shapes
        if not all(inputs[0].shape == inp.shape for inp in inputs):
            raise ValueError("All input tensors must have the same shape for MLP collate.")
        if not all(targets[0].shape == tgt.shape for tgt in targets):
            raise ValueError("All target tensors must have the same shape for MLP collate.")
        inputs = torch.stack(inputs)
        targets = torch.stack(targets)
        return inputs, targets

    @staticmethod
    def collate_fn_float(batch):
        """
        Collate function for regression models (float targets).
        Assumes each item in batch is (input_tensor, float_target).
        """
        inputs, targets = zip(*batch)
        inputs = [tensor if isinstance(tensor, torch.Tensor) else torch.tensor(tensor) for tensor in inputs]
        # Targets should be float or 0-dim tensor
        targets = [float(t.item()) if isinstance(t, torch.Tensor) and t.dim() == 0 else float(t) for t in targets]
        # Check shapes
        if not all(inputs[0].shape == inp.shape for inp in inputs):
            raise ValueError("All input tensors must have the same shape for regression collate.")
        inputs = torch.stack(inputs)
        targets = torch.tensor(targets, dtype=torch.float32)
        return inputs, targets

    @staticmethod
    def collate_fn_graph(batch):
        """
        Collate function for graph models.
        Assumes each item is a tuple (graph_data, target).
        Returns a list of graph_data objects and a tensor of targets.
        """
        graphs, targets = zip(*batch)
        # No type check for graphs (could be DGLGraph, PyG Data, etc.)
        targets = [tensor if isinstance(tensor, torch.Tensor) else torch.tensor(tensor) for tensor in targets]
        # Try to stack targets if possible, else just tensor
        try:
            targets = torch.stack(targets)
        except Exception:
            targets = torch.tensor(targets)
        return list(graphs), targets

    @staticmethod
    def collate_fn_transformer(batch):
        """
        Collate function for transformer models with padded sequences.
        Each item: (input_seq_tensor, target_seq_tensor)
        Pads sequences to the max length in the batch.
        """
        input_seqs, target_seqs = zip(*batch)
        input_seqs = [tensor if isinstance(tensor, torch.Tensor) else torch.tensor(tensor, dtype=torch.long) for tensor in input_seqs]
        target_seqs = [tensor if isinstance(tensor, torch.Tensor) else torch.tensor(tensor, dtype=torch.long) for tensor in target_seqs]
        # Check 1D
        if not all(inp.dim() == 1 for inp in input_seqs):
            raise ValueError("All input sequences must be 1D tensors for transformer collate.")
        if not all(tgt.dim() == 1 for tgt in target_seqs):
            raise ValueError("All target sequences must be 1D tensors for transformer collate.")
        input_seqs_padded = pad_sequence(input_seqs, batch_first=True, padding_value=0)
        target_seqs_padded = pad_sequence(target_seqs, batch_first=True, padding_value=0)
        return input_seqs_padded, target_seqs_padded

    @staticmethod
    def collate_fn_transformer_nested(batch):
        """
        Collate function for transformer models using nested tensors (variable-length, no padding).
        Each item: (input_seq_tensor, target_seq_tensor)
        Returns nested tensors for input and target.
        """
        inputs, targets = zip(*batch)
        # Convert each sequence to a tensor if they aren't already
        inputs = [tensor if isinstance(tensor, torch.Tensor) else torch.tensor(tensor) 
                for tensor in inputs]
        targets = [tensor if isinstance(tensor, torch.Tensor) else torch.tensor(tensor)
                for tensor in targets]
        # Check 1D
        if not all(inp.dim() == 1 for inp in inputs):
            raise ValueError("All input sequences must be 1D tensors for transformer nested collate.")
        if not all(tgt.dim() == 1 for tgt in targets):
            raise ValueError("All target sequences must be 1D tensors for transformer nested collate.")
        # Create nested tensors
        try:
            inputs_nt = torch.nested.nested_tensor(list(inputs), dtype=torch.long)
            targets_nt = torch.nested.nested_tensor(list(targets), dtype=torch.long)
        except TypeError as e:
            print("Error creating nested tensor:")
            print(f"Inputs type: {type(inputs)}")
            print(f"First input type: {type(inputs[0])}")
            print(f"First input shape: {inputs[0].shape if hasattr(inputs[0], 'shape') else 'N/A'}")
            raise e
        return inputs_nt, targets_nt
    
class CollateFunctionFactory:
    """
    A factory class to return the appropriate collate function based on user input.
    """

    @staticmethod
    def get_collate_function(collate_type):
        """
        Returns the appropriate collate function based on the input type.

        Args:
            collate_type (str): The type of collate function. Options are:
                - "default"
                - "float"
                - "graph"
                - "transformer"
                - "transformer_nested"

        Returns:
            function: The corresponding collate function.

        Raises:
            ValueError: If the collate_type is not recognized.
        """
        if collate_type == "default":
            return CollateFunctions.collate_fn
        elif collate_type == "float":
            return CollateFunctions.collate_fn_float
        elif collate_type == "graph":
            return CollateFunctions.collate_fn_graph
        elif collate_type == "transformer":
            return CollateFunctions.collate_fn_transformer
        elif collate_type == "transformer_nested":
            return CollateFunctions.collate_fn_transformer_nested
        else:
            raise ValueError(f"Unknown collate type: {collate_type}")


