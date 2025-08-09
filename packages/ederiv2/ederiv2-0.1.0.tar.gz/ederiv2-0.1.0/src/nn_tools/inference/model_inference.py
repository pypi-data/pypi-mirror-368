"""
A module to infer the Ai model 
"""

import os
import random
import shutil
from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple

from nn_tools.models.transformer.mol_transformer import generate_sequence  # generation function from your transformer file
from input_tools.transformers.mol_translator import MolTranslator  # assumed location for MolTranslator
from chem_handlers.smiles_handler import SmilesHandler, SmilesHandlingStrategyWithRDKIT
import dgl
import torch
from torch.utils.data import Dataset, Subset

from clean_driver import generate_graph_using_v1_model
from graph_handler import DGLGraphHandler
from gvae_base_models import BaseEAGVAE, GVAEAbstract
from gvae_models import DecoderFactory, EncoderFactory

from abc import ABC, abstractmethod
import torch
import numpy as np
from typing import Dict, List, Any, Optional, Union
from src.output_tools.save_run import SaveRun

class ModelInferenceAbstract(ABC):
    """
    Abstract class for model inference, post-processing and visualization.
    Handles loading a trained model, running inference on data, post-processing results,
    and generating visualizations.
    """
    
    def __init__(self, model: torch.nn.Module, output_folder: str, device: str = None):
        """
        Initialize the inference engine with a trained model.
        
        Args:
            model: The trained PyTorch model
            output_folder: Base folder to save inference outputs
            device: Device to run inference on ('cpu' or 'cuda')
        """
        self.model = model
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.model.eval()
        self.results = {}
        
        # Initialize SaveRun for logging and visualization
        self.save_run = SaveRun(output_folder, model)
        self.save_run.log_training_info(f"Initialized inference engine with model: {type(model).__name__}")
        self.save_run.log_training_info(f"Using device: {self.device}")
    
    @abstractmethod
    def preprocess_data(self, data):
        """
        Preprocess the data before inference.
        
        Args:
            data: The input data
            
        Returns:
            Preprocessed data ready for the model
        """
        pass
    
    @abstractmethod
    def run_inference(self, data):
        """
        Run inference on the data using the model.
        
        Args:
            data: The preprocessed data
            
        Returns:
            Raw model outputs
        """
        with torch.no_grad():
            # Implementation depends on model type
            pass
    
    @abstractmethod
    def postprocess_results(self, outputs, data=None):
        """
        Post-process the model outputs.
        
        Args:
            outputs: Raw model outputs
            data: Original data (optional)
            
        Returns:
            Processed results
        """
        pass
    
    @abstractmethod
    def visualize_results(self, results=None, save_path=None):
        """
        Generate visualizations from the results.
        
        Args:
            results: Results to visualize (uses self.results if None)
            save_path: Path to save visualizations (optional)
        """
        pass
    
    def run_pipeline(self, data, save_outputs=True):
        """
        Run the full inference pipeline.
        
        Args:
            data: Input data
            save_outputs: Whether to save outputs
            
        Returns:
            Processed results
        """
        self.save_run.log_training_info("Starting inference pipeline")
        
        # Preprocess
        self.save_run.log_training_info("Preprocessing data")
        preprocessed_data = self.preprocess_data(data)
        
        # Run inference
        self.save_run.log_training_info("Running model inference")
        outputs = self.run_inference(preprocessed_data)
        
        # Postprocess
        self.save_run.log_training_info("Postprocessing results")
        results = self.postprocess_results(outputs, data)
        self.results = results
        
        # Log metrics from results if available
        if isinstance(results, dict):
            for key, value in results.items():
                if isinstance(value, (int, float)):
                    self.save_run.log_metric(key, value)
                elif isinstance(value, dict) and all(isinstance(v, (int, float)) for v in value.values()):
                    self.save_run.log_param(key, value)
        
        # Visualize
        self.save_run.log_training_info("Generating visualizations")
        self.visualize_results(results)
        
        # Save results
        if save_outputs:
            self.save_results()
            self.save_run.save_vis_outputs()
            
        self.save_run.log_training_info("Inference pipeline completed")
        return results
    
    def save_results(self):
        """
        Save the inference results using SaveRun.
        """
        # Save structured data
        try:
            import json
            results_path = os.path.join(self.save_run._output_folder, 'inference_results.json')
            with open(results_path, 'w') as f:
                json.dump(self.results, f, indent=2, default=lambda x: str(x) if not isinstance(x, (int, float, str, list, dict, bool, type(None))) else x)
            self.save_run.log_training_info(f"Results saved to {results_path}")
        except Exception as e:
            self.save_run.log_training_info(f"Error saving results as JSON: {str(e)}")
            
            # Fallback to pickle
            try:
                import pickle
                results_path = os.path.join(self.save_run._output_folder, 'inference_results.pkl')
                with open(results_path, 'wb') as f:
                    pickle.dump(self.results, f)
                self.save_run.log_training_info(f"Results saved to {results_path}")
            except Exception as e2:
                self.save_run.log_training_info(f"Error saving results as pickle: {str(e2)}")

class GVAEInferencer(ModelInferenceAbstract):
    _subdir_prefix_vis_graphs="testing_plots"
    
    def __init__(self, trained_model: GVAEAbstract, model_type, output_dir, dgl_graph_handler:DGLGraphHandler):
        self._trained_model: GVAEAbstract=trained_model
        self._model_type: str=model_type
        self._dgl_graph_handler: DGLGraphHandler=dgl_graph_handler
        self._output_dir=output_dir
        
    def _generate_dirs(self,output_dir)->Tuple[str,...]: 
        subdir_name = f'{self._subdir_prefix_vis_graphs}_{self._model_type}_model'
        images_dir=os.path.join(output_dir,subdir_name)
        # Check if directory exists
        if os.path.exists(images_dir):
            # Directory exists - empty it
            shutil.rmtree(images_dir)  # Remove all contents recursively
            os.makedirs(images_dir)    # Recreate empty directory
        else:
            # Directory doesn't exist - create it
            os.makedirs(images_dir)
            
        return images_dir


    def graphs_to_images(self, graphs, graphs_subdir):
        counter=1
        graphs_full_path=os.path.join(self._output_dir, graphs_subdir)
        for graph in graphs:
            image_file_path=os.path.join(graphs_full_path,f"gen_graph_{counter}.png")
            self._dgl_graph_handler.visualize(graph,image_file_path)
            counter+=1
            
        print(f"Successfully wrote graphs to ")

    def generate_graph_from_latent(self, z, device, edge_threshold=0.5):
        node_count = z.shape[0]
        node_logits, edge_logits, edge_index = self._trained_model.decode(z)

        # One-hot encoded node features
        node_probs = torch.softmax(node_logits, dim=1)
        node_classes = torch.argmax(node_probs, dim=1)  # Class indices
        pred_node_feats = torch.nn.functional.one_hot(
            node_classes,
            num_classes=node_logits.shape[1]
        ).float()  # [num_nodes, num_classes]

        # Edge probabilities and classes
        edge_probs = torch.softmax(edge_logits, dim=1)
        edge_classes = torch.argmax(edge_probs, dim=1)  # Class indices
        
        # Filter edges based on threshold
        mask = edge_probs.max(dim=1)[0] > edge_threshold
        filtered_edges = edge_index[:, mask]
        filtered_edge_classes = edge_classes[mask]
        
        # One-hot encoded edge features
        num_edge_classes = edge_logits.shape[1]  # Get number of edge classes
        filtered_edge_features = torch.nn.functional.one_hot(
            filtered_edge_classes,
            num_classes=num_edge_classes
        ).float()  # [num_edges, num_edge_classes]
        
        # Create graph
        graph = dgl.graph((filtered_edges[0], filtered_edges[1]), num_nodes=node_count)
        
        # Assign features
        graph.ndata['x'] = pred_node_feats
        graph.edata['e'] = filtered_edge_features  # One-hot encoded edges
        
        return graph, filtered_edges
    
    def infer(self, dataset, data_frac:float, device):
    
        self._trained_model.eval()
        
        num_samples=round(len(dataset)*data_frac)
        random_samples = random.sample(range(len(dataset)), num_samples)
        subset = Subset(dataset, random_samples)
        generated_graphs=[]
        with torch.no_grad():
            for g, smi, edge_index in subset:
                g = g.to(device)
                node_feats = g.ndata['x'].float()
                edge_feats = g.edata['e'].float()
                # Encode
                mu, logvar = self._trained_model.encode(g, node_feats,edge_feats)
                z_input = self._trained_model.reparameterize(mu, logvar)
                # Sample new z from prior
                z_prior = torch.randn_like(z_input)
                z_graph = z_input.mean(dim=0, keepdim=True)  
                gen_graph, gen_filtered_edges = self._dgl_graph_handler.generate_graph_from_latent(self._trained_model, z_prior.squeeze(0), device)
                generated_graphs.append(gen_graph)
        print(f'Successfully used the {self._model_type} graph model in the inference phase.')
        
        return generated_graphs
    

class TransformerInferencer(ModelInferenceAbstract):
    """
    Generic inferencer for transformer models.
    """
    def __init__(self, trained_model, vocab_builder, output_dir, device='cpu'):
        """
        Args:
            trained_model: The transformer model.
            vocab_builder: Vocabulary builder used during training.
            output_dir: Directory where outputs are saved.
            device: Computation device.
        """
        super().__init__(trained_model, model_type="transformer", output_dir=output_dir)
        self._vocab_builder = vocab_builder
        self._device = device


    @abstractmethod
    def postprocess(self, raw_outputs):
        """
        Convert raw outputs to human-readable format.
        """
        pass

    def infer(self, num_samples: int, max_len: int = 30, temperature: float = 1.0, greedy: bool = False, **kwargs):
        """
        Generate sequences using the transformer model.

        Args:
            num_samples: Number of samples to generate.
            max_len: Maximum sequence length.
            temperature: Sampling temperature.
            greedy: Whether to use greedy decoding.
            **kwargs: Additional arguments for the generation function.

        Returns:
            List of generated sequences.
        """
        self._trained_model.eval()
        device = self._device
        vocab = self._vocab_builder
        start_token = vocab.start_token_id if hasattr(vocab, "start_token_id") else vocab.token_to_id["<START>"]
        end_token = vocab.end_token_id if hasattr(vocab, "end_token_id") else vocab.token_to_id["<END>"]
        pad_token = vocab.pad_token_id if hasattr(vocab, "pad_token_id") else vocab.token_to_id.get("<PAD>", 0)

        sequences = torch.full((num_samples, max_len), pad_token, dtype=torch.long, device=device)
        sequences[:, 0] = start_token
        finished = torch.zeros(num_samples, dtype=torch.bool, device=device)

        for t in range(1, max_len):
            with torch.no_grad():
                logits = self._trained_model(sequences[:, :t])  # [num_samples, t, vocab_size]
                logits = logits[:, -1, :]  # [num_samples, vocab_size]
                if greedy:
                    next_tokens = torch.argmax(logits, dim=-1)
                else:
                    probs = torch.softmax(logits / temperature, dim=-1)
                    next_tokens = torch.multinomial(probs, num_samples=1).squeeze(-1)
                next_tokens = next_tokens.masked_fill(finished, pad_token)
                sequences[:, t] = next_tokens
                finished = finished | (next_tokens == end_token)
                if finished.all():
                    break

        # Convert to list of token lists, truncate at end_token
        result = []
        for seq in sequences.tolist():
            if end_token in seq:
                idx = seq.index(end_token)
                result.append(seq[1:idx])  # skip start token, stop at end token
            else:
                result.append(seq[1:])  # skip start token
        return result


class ActionSequenceTransformerInferencer(TransformerInferencer):
    """
    Inferencer for transformer models that generate sequences of actions.
    This class generates action sequences, converts them to SMILES via MolTranslator,
    and then returns valid SMILES strings.
    """
    def __init__(self, trained_model, vocab_builder, output_dir,
                 device='cpu', temperature=1.0, max_len=30, greedy=False):
        super().__init__(trained_model, vocab_builder, output_dir, generate_fn=generate_sequence, device=device)
        # Instantiate a SmilesHandler with an RDKit-based strategy.
        self.smiles_handler = SmilesHandler(smiles_handling_strategy=SmilesHandlingStrategyWithRDKIT())
        # Instantiate MolTranslator (assumed to have a to_smiles(seq) method).
        self.mol_translator = MolTranslator()
        self.temperature = temperature
        self.max_len = max_len
        self.greedy = greedy

    def infer(self, num_samples: int, **kwargs):
        """
        Generate new action sequences using the transformer model.
        """
        raw_sequences = self._generate_fn(
            self._trained_model,
            self._vocab_builder,
            num_samples=num_samples,
            max_len=self.max_len,
            temperature=self.temperature,
            greedy=self.greedy,
            device=self._device
        )
        return raw_sequences

    def postprocess(self, raw_outputs):
        """
        Convert generated action sequences to SMILES strings.
        Only returns valid SMILES (i.e. representing a single molecule).
        """
        smiles_list = []
        for seq in raw_outputs:
            smiles = self.mol_translator.to_smiles(seq)
            if smiles is not None and self.smiles_handler.is_single_molecule(smiles):
                smiles_list.append(smiles)
        return smiles_list
    

    

if __name__ == "__main__":
    import torch
    from dgl.data.utils import load_graphs
    from graph_handler import DGLGraphHandler

    # 1. Setup
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    output_dir = "./inference_test_output/run1"
    os.makedirs(output_dir, exist_ok=True)
    
    
    
    # 2. Load real data (replace with your dataset)
    # data_generator=data_generator()
    
    # 3. Initialize components (replace with your actual model)
    # Hyperparameters
    hidden_dim = 128
    latent_dim = 32
    node_feat_dim = 11 #13     # depends on VALID ATOMS
    edge_feat_dim = 5      # e.g., one-hot bond types
    edge_exist_feat_dim=2   # Edge either exists or not-exists
    
    node_classes = 11     # number of atom types
    edge_classes = 5      # number of bond types (including 'no bond')
    edge_exist_classes=2 
    
    encoder = EncoderFactory.create('v1', in_node_dim=node_feat_dim, in_edge_dim=edge_feat_dim, hidden_dim=hidden_dim, latent_dim=latent_dim)
    decoder = DecoderFactory.create('v1',latent_dim=latent_dim, node_classes=node_classes, edge_classes=edge_classes)
    gvae_model=BaseEAGVAE(encoder,decoder)
    
    gvae_model = gvae_model.to(device)
    gvae_model.load_state_dict(torch.load('/home/meisam/GitHub_codes/eDeriv2/outputs/run_357/best_model.pt'))
    
    dgl_handler = DGLGraphHandler()

    # 4. Run inference
    inferencer = GVAEInferencer(
        trained_model=model,
        model_type="v1",  
        dgl_graph_handler=dgl_handler
    )
    
    print(f"Running inference on {len(dataset)} molecules...")
    inferencer.infer(
        dataset=dataset,
        data_frac=1.0,  # Process 100% of the test set
        output_dir=output_dir,
        device=device
    )
    
    # 5. Verify output
    generated_files = [f for f in os.listdir(output_dir) if f.endswith(".png")]
    print(f"Generated {len(generated_files)} graph visualizations in {output_dir}")
    
