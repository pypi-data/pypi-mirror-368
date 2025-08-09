
import os
import json
from typing import Dict
import matplotlib.pyplot as plt
import torch
import datetime
import csv
from torch.quantization import quantize_dynamic
import torch.nn as nn
class NNVisualizer:
    """
    A helper class for visualizing and generating images for training metrics and parameters.
    """
    def __init__(self, output_folder):
        self.output_folder = output_folder
        os.makedirs(self.output_folder, exist_ok=True)

    def plot_metric(self, metric_values, metric_name, save_as_image=True):
        """
        Plots a metric (e.g., loss, accuracy) over epochs.
        """
        plt.figure()
        plt.plot(range(1, len(metric_values) + 1), metric_values, label=metric_name)
        plt.xlabel('Epochs')
        plt.ylabel(metric_name)
        plt.title(f'{metric_name} vs Epochs')
        plt.legend()
        if save_as_image:
            image_path = os.path.join(self.output_folder, f'{metric_name}_vs_epochs.png')
            plt.savefig(image_path)
            print(f"Saved {metric_name} plot to {image_path}")
        plt.close()

    def plot_params(self, param_dict, param_name, save_as_image=True):
        """
        Visualizes specific parameters (e.g., mu, sigma) as requested by the user.
        """
        plt.figure()
        for key, values in param_dict.items():
            plt.plot(range(1, len(values) + 1), values, label=f'{param_name} - {key}')
        plt.xlabel('Epochs')
        plt.ylabel(param_name)
        plt.title(f'{param_name} vs Epochs')
        plt.legend()
        if save_as_image:
            image_path = os.path.join(self.output_folder, f'{param_name}_vs_epochs.png')
            plt.savefig(image_path)
            print(f"Saved {param_name} plot to {image_path}")
        plt.close()


class SaveRun:
    """
    A class to save and visualize the outcomes of a neural network training run.
    Each run is saved in a unique output folder with the current date and time in its name.
    """

    def __init__(self, output_folder, model=None, nn_visualizer=None, folder_suffix=""):
        self._base_output_folder = output_folder
        self._output_folder = self._make_unique_output_folder(self._base_output_folder, folder_suffix)
        self._model = model
        self._nn_visualizer = nn_visualizer or NNVisualizer(self._output_folder)
        self._metrics = {}
        self._params = {}
        self._training_losses = []

    @staticmethod
    def _make_unique_output_folder(base_folder, folder_suffix):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        unique_folder = os.path.join(base_folder, f"run_{timestamp}_{folder_suffix}" if folder_suffix else f"run_{timestamp}")
        os.makedirs(unique_folder, exist_ok=True)
        return unique_folder

    def log_training_info(self, message: str):
        log_file = os.path.join(self._output_folder, "training_log.txt")
        with open(log_file, "a") as f:
            f.write(message + "\n")
        print(message)

    @property
    def model(self):
        return self._model
    
    @model.setter
    def model(self, model):
        self._model = model



    def save_model(self, checkpoint: Dict, save_state_dict: bool = True, save_torchscript: bool = False, quantize: bool = False):
        """
        Saves:
        1) state_dict (always if save_state_dict=True)
        2) optional TorchScript module (self-contained, no class needed).
           If quantize=True it will dynamic-quantize all Linear layers.
        """
        # 1) State‐dict
        if save_state_dict:
            sd_path = os.path.join(self._output_folder, f"model_epoch_{checkpoint['epoch']}_state_dict.pth")
            torch.save(checkpoint, sd_path)
            print(f"Complete checkpoint saved to {sd_path}")

        # 2) TorchScript
        if save_torchscript:
            model_to_script = self._model
            model_to_script.eval()

            # optional dynamic quantization to shrink size ∼4× for Linear layers
            if quantize:
                model_to_script = quantize_dynamic(
                    model_to_script,
                    {nn.Linear},
                    dtype=torch.qint8
                )

            # JIT‐script and save
            scripted = torch.jit.script(model_to_script)
            ts_path = os.path.join(self._output_folder, f"model_epoch_{epoch}.pt")
            scripted.save(ts_path)
            print(f"[+] TorchScript{' + quantized' if quantize else ''} model saved to {ts_path}")

    def log_metric(self, metric_name, value):
        """
        Logs a metric (e.g., loss, accuracy) for visualization.
        Call this directly from your training loop after each epoch/step.
        """
        if metric_name not in self._metrics:
            self._metrics[metric_name] = []
        self._metrics[metric_name].append(value)
        if metric_name.lower() == "loss" or metric_name.lower() == "training_loss":
            self._training_losses.append(value)

    def log_param(self, param_name, param_values):
        """
        Logs specific parameters (e.g., mu, sigma) for visualization.
        Call this directly from your training loop after each epoch/step.
        """
        if param_name not in self._params:
            self._params[param_name] = {}
        for key, value in param_values.items():
            if key not in self._params[param_name]:
                self._params[param_name][key] = []
            self._params[param_name][key].append(value)

    def save_metrics(self):
        """
        Saves all logged metrics to a JSON file.
        """
        metrics_path = os.path.join(self._output_folder, 'metrics.json')
        with open(metrics_path, 'w') as f:
            json.dump(self._metrics, f, indent=4)
        print(f"Metrics saved to {metrics_path}")

    def save_params(self):
        """
        Saves all logged parameters to a JSON file.
        """
        params_path = os.path.join(self._output_folder, 'params.json')
        with open(params_path, 'w') as f:
            json.dump(self._params, f, indent=4)
        print(f"Parameters saved to {params_path}")

    def save_training_losses(self):
        """
        Saves the training losses to a CSV file in a tabular format.
        """
        losses_path = os.path.join(self._output_folder, 'training_losses.csv')
        with open(losses_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Epoch', 'Training Loss'])
            for epoch, loss in enumerate(self._training_losses, start=1):
                writer.writerow([epoch, loss])
        print(f"Training losses saved to {losses_path}")

    def visualize_metrics(self):
        """
        Visualizes all logged metrics using the NNVisualizer.
        """
        for metric_name, values in self._metrics.items():
            self._nn_visualizer.plot_metric(values, metric_name)

    def visualize_params(self):
        """
        Visualizes all logged parameters using the NNVisualizer.
        """
        for param_name, param_dict in self._params.items():
            self._nn_visualizer.plot_params(param_dict, param_name)

    def save_vis_outputs(self):
        """
        Finalizes the run by saving metrics, parameters, training losses, and visualizing them.
        """
        self.save_metrics()
        self.save_params()
        self.save_training_losses()
        self.visualize_metrics()
        self.visualize_params()