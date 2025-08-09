from dataclasses import dataclass
from typing import Optional, Dict
import torch
import dgl


@dataclass
class GVAELossInputs:
    """Container for all inputs needed for GVAE loss calculation"""
    # Required for KL divergence
    mu: Optional[torch.Tensor] = None
    logvar: Optional[torch.Tensor] = None
    
    # Node-related inputs
    true_node_feats: Optional[torch.Tensor] = None
    node_logits: Optional[torch.Tensor] = None
    
    # Edge-related inputs
    true_edge_type_feats: Optional[torch.Tensor] = None
    edge_type_logits: Optional[torch.Tensor] = None
    true_edge_exist_feats: Optional[torch.Tensor] = None
    all_edge_exist_logits: Optional[torch.Tensor] = None
    edge_index: Optional[torch.Tensor] = None
    
    # Graph structure
    graph: Optional[dgl.DGLGraph] = None
    
    # Flags and parameters
    compute_valence: bool = False
    temperature: Optional[float] = None
    
    def validate(self):
        """Check for required combinations of inputs"""
        if self.compute_valence and (self.graph is None or self.node_logits is None or self.edge_index is None):
            raise ValueError("Valence computation requires graph, node_logits and edge_index")
        
        # Add more validation rules as needed
        
        
class GVAELossInputsBuilder:
    def __init__(self):
        self._inputs = GVAELossInputs()
    
    def with_latent(self, mu: torch.Tensor, logvar: torch.Tensor):
        self._inputs.mu = mu
        self._inputs.logvar = logvar
        return self
    
    def with_node_data(self, true_feats: torch.Tensor, logits: torch.Tensor):
        self._inputs.true_node_feats = true_feats
        self._inputs.node_logits = logits
        return self
    
    def with_valence_calculation(self, graph: dgl.DGLGraph, edge_index: torch.Tensor):
        self._inputs.graph = graph
        self._inputs.edge_index = edge_index
        self._inputs.compute_valence = True
        return self
    
    def build(self) -> GVAELossInputs:
        self._inputs.validate()
        return self._inputs


class GVAELossCalculator:
    def __init__(self, 
                 weights: Dict[str, float] = None,
                 default_temperature: float = None,
                 device: str = 'cpu'):
        """
        Initialize the loss calculator with weights for different loss components.
        
        Args:
            weights: Dictionary of loss weights (keys: 'node', 'edge_type', 
                     'edge_exist', 'kl', 'valence')
            default_temperature: Default temperature for Gumbel-Softmax
            device: Device to use for computations
        """
        self.device = device
        self.temperature = default_temperature
        
        # Default weights (can be overridden)
        self.weights = {
            'node': 1.0,
            'edge_type': 1.0,
            'edge_exist': 1.0,
            'kl': 0.1,
            'valence': 1.0
        }
        
        if weights:
            self.weights.update(weights)
    
    def compute_losses(self, inputs: GVAELossInputs) -> Dict[str, torch.Tensor]:
        """
        Compute all requested losses with optional weights.
        
        Args:
            inputs: GVAELossInputs containing all necessary data
            
        Returns:
            Dictionary containing all computed losses and total weighted loss
        """
        inputs.validate()
        temperature = inputs.temperature if inputs.temperature is not None else self.temperature
        losses = {}
        
        # Node feature loss
        if self.weights['node'] > 0 and inputs.true_node_feats is not None and inputs.node_logits is not None:
            if temperature is not None:
                losses['node'] = self._gumbel_node_feat_loss(inputs.true_node_feats, inputs.node_logits, temperature)
            else:
                losses['node'] = self._simple_node_feat_loss(inputs.true_node_feats, inputs.node_logits)
        
        # Edge type loss
        if self.weights['edge_type'] > 0 and inputs.true_edge_type_feats is not None and inputs.edge_type_logits is not None:
            if temperature is not None:
                losses['edge_type'] = self._gumbel_edge_type_loss(inputs.true_edge_type_feats, inputs.edge_type_logits, temperature)
            else:
                losses['edge_type'] = self._simple_edge_type_loss(inputs.true_edge_type_feats, inputs.edge_type_logits)
        
        # Edge existence loss
        if self.weights['edge_exist'] > 0 and inputs.true_edge_exist_feats is not None and inputs.all_edge_exist_logits is not None:
            if temperature is not None:
                losses['edge_exist'] = self._gumbel_edge_exist_loss(inputs.true_edge_exist_feats, inputs.all_edge_exist_logits, temperature)
            else:
                losses['edge_exist'] = self._simple_edge_exist_loss(inputs.true_edge_exist_feats, inputs.all_edge_exist_logits)
        
        # KL divergence
        if self.weights['kl'] > 0 and inputs.mu is not None and inputs.logvar is not None:
            losses['kl'] = self._kl_divergence(inputs.mu, inputs.logvar)
        
        # Valence loss
        if self.weights['valence'] > 0 and inputs.compute_valence:
            losses['valence'] = self._valence_loss(inputs.graph, inputs.node_logits, inputs.edge_index, inputs.edge_type_logits)
        
        # Calculate total weighted loss
        total_loss = torch.tensor(0.0, device=self.device)
        for loss_name, loss_value in losses.items():
            total_loss += self.weights[loss_name] * loss_value
        
        losses['total'] = total_loss
        return losses
    
        # Individual loss calculation methods
    def _simple_node_feat_loss(self, true_node_feats, node_logits):
        node_labels = true_node_feats.argmax(dim=1)
        return F.cross_entropy(node_logits, node_labels)
    
    def _gumbel_node_feat_loss(self, true_node_feats, node_logits, temperature):
        node_labels = true_node_feats.argmax(dim=1)
        node_feat_prob = F.gumbel_softmax(node_logits, tau=temperature, hard=False)
        log_probs = torch.log(node_feat_prob + 1e-10)
        return F.nll_loss(log_probs, node_labels)
    
    def _simple_edge_type_loss(self, true_edge_type_feats, edge_type_logits):
        edge_labels = true_edge_type_feats.argmax(dim=1)
        return F.cross_entropy(edge_type_logits, edge_labels)
    
    def _gumbel_edge_type_loss(self, true_edge_type_feats, edge_type_logits, temperature):
        num_nodes = int(np.sqrt(true_edge_type_feats.shape[0]))
        rows, cols = torch.triu_indices(num_nodes, num_nodes, offset=1)
        upper_tri_indices = rows * num_nodes + cols
        
        upper_tri_edge_logits = edge_type_logits[upper_tri_indices]
        upper_tri_edge_labels = true_edge_type_feats[upper_tri_indices].argmax(dim=1)
        
        edge_type_probs = F.gumbel_softmax(upper_tri_edge_logits, tau=temperature, hard=False)
        log_probs = torch.log(edge_type_probs + 1e-10)
        return F.nll_loss(log_probs, upper_tri_edge_labels)
    
    def _simple_edge_exist_loss(self, true_edge_exist_feats, all_edge_exist_logits):
        true_edge_exist_labels = true_edge_exist_feats.argmax(dim=1)
        return F.cross_entropy(all_edge_exist_logits, true_edge_exist_labels)
    
    def _gumbel_edge_exist_loss(self, true_edge_exist_feats, all_edge_exist_logits, temperature):
        num_nodes = int(np.sqrt(true_edge_exist_feats.shape[0]))
        rows, cols = torch.triu_indices(num_nodes, num_nodes, offset=1)
        upper_tri_indices = rows * num_nodes + cols
        
        upper_tri_edge_logits = all_edge_exist_logits[upper_tri_indices]
        upper_tri_edge_labels = true_edge_exist_feats[upper_tri_indices].argmax(dim=1)
        
        edge_exist_probs = F.gumbel_softmax(upper_tri_edge_logits, tau=temperature, hard=False)
        log_probs = torch.log(edge_exist_probs + 1e-10)
        return F.nll_loss(log_probs, upper_tri_edge_labels)
    
    def _kl_divergence(self, mu, logvar):
        return -0.5 * torch.mean(1 + logvar - mu.pow(2) - logvar.exp())
    
    def _valence_loss(self, g, node_logits, g_edge_index, edge_type_logits):
        # This would use your DGLGraphMaker and DGLGraphHandler
        # Implementation depends on these external classes
        dgl_graph_maker = DGLGraphMaker(atom_types=VALID_ATOMS_NAME)
        node_probs = torch.softmax(node_logits, dim=-1) 
        recon_node_one_hot = (node_probs == node_probs.max(dim=-1, keepdim=True)[0]).float()
        edge_type_probs = torch.softmax(edge_type_logits, dim=-1) 
        recon_edge_type_one_hot = (edge_type_probs == edge_type_probs.max(dim=-1, keepdim=True)[0]).float()
        recon_graph = dgl_graph_maker.create_from_one_hot(recon_node_one_hot, g_edge_index, recon_edge_type_one_hot)
        dgl_graph_handler = DGLGraphHandler()
        return dgl_graph_handler.compute_valence_constraint_loss(recon_graph)
