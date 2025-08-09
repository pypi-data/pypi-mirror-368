import torch
import torch.nn as nn

class ModelAnalyzer:
              def __init__(self, model: nn.Module, input_size: tuple, device: str = 'cuda'):
                            self.model = model.to(device)
                            self.input_size = input_size
                            self.device = device

              def find_optimal_batch_size(self, start_batch_size=16, max_batch_size=4096):
                            batch_size = start_batch_size
                            optimal_batch_size = batch_size
                            while batch_size <= max_batch_size:
                                          try:
                                                        inputs = torch.randn(batch_size, *self.input_size[1:]).to(self.device)
                                                        outputs = self.model(inputs)
                                                        optimal_batch_size = batch_size
                                                        batch_size *= 2
                                          except RuntimeError as e:
                                                        print(f"Batch size {batch_size} exceeds memory limits.")
                                                        break
                            print(f"Optimal batch size: {optimal_batch_size}")
                            return optimal_batch_size

              # Add more analysis methods as needed
              def count_parameters(self):
                            return sum(p.numel() for p in self.model.parameters() if p.requires_grad)

# Example usage:
if __name__ == "__main__":
              # === Setting Hyperparameters ===
              total_epochs=50
              model_dim=64 
              num_heads=8 
              num_layers=3
              model = nn.Linear(1000, 1000)
              input_size = (1000, 1000)  # (batch_size, features)
              analyzer = ModelAnalyzer(model, input_size)
              analyzer.find_optimal_batch_size()
              print(f"Trainable parameters: {analyzer.count_parameters()}")