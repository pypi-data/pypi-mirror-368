from abc import abstractmethod, ABC

import torch

from src.output_tools.save_run import SaveRun


class NNTrainerAbstract(ABC):
    def __init__(self, model, optimizer, loss_fn, device, scheduler=None):
        self._model = model
        self._optimizer = optimizer
        self._loss_fn = loss_fn
        self._device = device
        self._scheduler = scheduler

    @abstractmethod
    def train_step(self, batch):
        """
        Perform a single training step. Must be implemented by subclasses.
        """
        pass

    def train(self, dataloader, epochs, save_run: SaveRun = None):
        """
        Generic training loop. Assumes `train_step` always returns a dictionary of losses.
        Returns:
            list: A list of average losses for each epoch.
        """
        epoch_losses = []

        for epoch in range(epochs):
            self._model.train()
            loss_dict = {}

            for batch in dataloader:
                batch_loss = self.train_step(batch)

                # Accumulate losses
                for key, value in batch_loss.items():
                    loss_dict[key] = loss_dict.get(key, 0) + value.item()

            # Average and print losses
            for key in loss_dict:
                loss_dict[key] /= len(dataloader)
                if save_run:
                    save_run.log_metric(key, loss_dict[key])
            print(f"Epoch {epoch + 1} | " + " | ".join(f"{key}: {value:.4f}" for key, value in loss_dict.items()))
            epoch_losses.append(loss_dict)

            if self._scheduler:
                self._scheduler.step(loss_dict.get("loss", 0))

        return epoch_losses
    
    def get_model(self):
        """
        Retrieve the trained model.
        """
        return self._model

class TransformerTrainer(NNTrainerAbstract):
    def train_step(self, batch):
        """
        Perform a single training step for sequence models.

        Args:
            batch (tuple): A batch of data (inputs, targets).
        Returns:
            dict: A dictionary containing the computed loss for the batch.
        """
        # Unpack the batch
        batch_inputs, batch_targets = batch
        batch_inputs, batch_targets = batch_inputs.to(self._device), batch_targets.to(self._device)

        # Zero the gradients
        self._optimizer.zero_grad()

        # Create src_mask based on sequence lengths
        src_lengths = [t.size(0) for t in batch_inputs.unbind()]
        max_len = max(src_lengths)
        src_mask = self._model.generate_square_subsequent_mask(max_len).to(self._device)

        # Forward pass
        output = self._model(batch_inputs, src_mask)

        # Calculate loss
        loss = 0
        batch_size = len(src_lengths)
        output_list = [output[i, :src_lengths[i]] for i in range(batch_size)]
        target_list = [batch_targets[i] for i in range(batch_size)]

        for out_seq, target_seq in zip(output_list, target_list):
            loss += self._loss_fn(out_seq, target_seq)

        loss = loss / batch_size  # Average loss

        # Backward pass and optimization
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self._model.parameters(), 1.0)
        self._optimizer.step()

        return {"loss": loss}
    
    


