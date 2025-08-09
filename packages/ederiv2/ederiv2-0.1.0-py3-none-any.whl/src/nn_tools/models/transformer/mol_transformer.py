

import os
import pickle
from typing import Optional
import numpy as np
import torch
import torch.nn as nn
from torch.optim.lr_scheduler import ReduceLROnPlateau
from collections import Counter

from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import Dataset, DataLoader

from src.chem_handlers.smiles_handler import SmilesHandler, SmilesHandlingStrategyWithRDKIT
from src.input_tools.transformers.mol_translator import MolTranslator
from src.input_tools.transformers.action_gen import RDKitMolDFSActionGenerator, SmilesDatasetActionGenerator
from src.nn_tools.models.transformer.utils import get_weighting_function
from src.nn_tools.trainers.nn_trainer import TransformerTrainer
from src.output_tools.save_run import SaveRun
from src.input_tools.transformers.vocab_builder import ActionVocab
from src.nn_tools.auxiliary.batch import CollateFunctionFactory
# === Dataset class ===
class ActionSequenceDataset(Dataset):
    def __init__(self, action_sequences, action_vocab):
        self.vocab = action_vocab
        self.data = []

        for seq in action_sequences:
            input_seq = seq[:-1]  # everything except last
            target_seq = seq[1:]  # everything except first

            input_ids = torch.tensor(self.vocab.encode(input_seq))
            target_ids = torch.tensor(self.vocab.encode(target_seq))

            self.data.append((input_ids, target_ids))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]


# === Positional Encoding + Transformer Model ===
class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 500):
        super().__init__()
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-torch.log(torch.tensor(10000.0)) / d_model))
        pe = torch.zeros(max_len, d_model)
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.pe[:x.size(1)]

class MolecularActionTransformer(nn.Module):
    def __init__(self, vocab_size: int, d_model: int = 512, nhead: int = 8, 
                 num_layers: int = 6, dropout: float = 0.1):
        super().__init__()
        self.d_model = d_model
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model)
        encoder_layers = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward=4*d_model, dropout=dropout)
        self.transformer = nn.TransformerEncoder(encoder_layers, num_layers)
        self.fc_out = nn.Linear(d_model, vocab_size)
        self.init_weights()

    def init_weights(self):
        initrange = 0.1
        self.embedding.weight.data.uniform_(-initrange, initrange)
        self.fc_out.bias.data.zero_()
        self.fc_out.weight.data.uniform_(-initrange, initrange)

    def forward(self, src: torch.Tensor, src_mask: torch.Tensor = None) -> torch.Tensor:
        if src.is_nested:
            # Get lengths and convert to padded tensor
            src_lengths = [t.size(0) for t in src.unbind()]
            max_len = max(src_lengths)
            
            # Convert to padded tensor for processing
            src_padded = torch.nested.to_padded_tensor(src, padding=0)
            
            # Standard processing on padded tensor
            src_embed = self.embedding(src_padded) * self.d_model**0.5
            src_embed = self.pos_encoder(src_embed)
            
            # Transpose to (seq_len, batch_size, d_model)
            src_embed = src_embed.transpose(0, 1)
            
            # Process through transformer
            out = self.transformer(src_embed, src_mask)
            
            # Transpose back and convert to nested if needed
            out = out.transpose(0, 1)
            return self.fc_out(out)
        else:
            # Original non-nested processing
            src = self.embedding(src) * self.d_model**0.5
            src = self.pos_encoder(src)
            src = src.transpose(0, 1)
            out = self.transformer(src, src_mask)
            out = out.transpose(0, 1)
            return self.fc_out(out)

    def generate_square_subsequent_mask(self, sz: int) -> torch.Tensor:
        return torch.triu(torch.full((sz, sz), float('-inf')), diagonal=1)

class ScriptableMolecularActionTransformer(nn.Module):
    """TorchScript-friendly version without nested tensor support"""
    def __init__(self, vocab_size: int, d_model: int = 512, nhead: int = 8, 
                 num_layers: int = 6, dropout: float = 0.1):
        super().__init__()
        self.d_model = d_model
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model)
        encoder_layers = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward=4*d_model, dropout=dropout)
        self.transformer = nn.TransformerEncoder(encoder_layers, num_layers)
        self.fc_out = nn.Linear(d_model, vocab_size)
        self.init_weights()

    def init_weights(self):
        initrange = 0.1
        self.embedding.weight.data.uniform_(-initrange, initrange)
        self.fc_out.bias.data.zero_()
        self.fc_out.weight.data.uniform_(-initrange, initrange)

    def forward(self, src: torch.Tensor, src_mask: torch.Tensor = None) -> torch.Tensor:
        src_embed = self.embedding(src) * (self.d_model ** 0.5)
        src_embed = self.pos_encoder(src_embed)
        src_embed = src_embed.transpose(0, 1)
        out = self.transformer(src_embed, src_mask)
        out = out.transpose(0, 1)
        return self.fc_out(out)

    def generate_square_subsequent_mask(self, sz: int) -> torch.Tensor:
        return torch.triu(torch.full((sz, sz), float('-inf')), diagonal=1)


def generate_sequence(model, vocab_builder:ActionVocab, num_samples:int, max_len=30, temperature=2.0, greedy=False, device='cpu'):
    model.eval()
    start_token = vocab_builder.get_vocab()['<START>']
    end_token = vocab_builder.get_vocab()['<END>']

    action_seqs = []
    for _ in range(num_samples):
        # Start with <START>
        generated = [start_token]

        for _ in range(max_len):
            # Convert to regular tensor instead of nested tensor
            input_seq = torch.tensor(generated, dtype=torch.long).unsqueeze(0).to(device)  # (1, seq_len)
            
            # Generate causal mask
            src_mask = model.generate_square_subsequent_mask(input_seq.size(1)).to(device)

            with torch.no_grad():
                output = model(input_seq, src_mask=src_mask)  # (1, seq_len, vocab_size)
                # No need for to_padded_tensor since we're using regular tensors

            # Get last token's logits
            logits = output[0, -1] / temperature

            if greedy:
                next_token = torch.argmax(logits).item()
            else:
                probabilities = torch.softmax(logits, dim=-1)
                next_token = torch.multinomial(probabilities, 1).item()

            generated.append(next_token)
            
            if next_token == end_token:
                break

        # Decode and clean up the sequence
        decoded = vocab_builder.decode(generated)
        # Remove <START> and anything after <END> if present
        if "<END>" in decoded:
            decoded = decoded[:decoded.index("<END>")+1]  # Include the <END> token

        
        action_seqs.append(decoded)

    return action_seqs

if __name__=="__main__":
    """ Generate list of actions for the smiles dataset """
    import pandas as pd
    from torch.nn.utils.rnn import pad_sequence
    import torch

    rdkit_mol_action_generator = RDKitMolDFSActionGenerator()

    # === Initialize SaveRun ===
    token_weghting_type= 'constant'
    
    output_folder = "/home/meisam/GitHub_codes/eDeriv2/action_seqs_training_results"
    save_run = SaveRun(output_folder,folder_suffix=token_weghting_type+"_"+"weighting",)

    # === 1. Load the actions dataset from a chached file ===
    save_run.log_training_info("Loading dataset actions from cached file...")

    # Adjust the BASE_PATH to your dataset location
    BASE_PATH = "/home/meisam/GitHub_codes/eDeriv2/assets/datasets/"
    # BASE_PATH = "/home/magesh/eDeriv/graph_variation/"
    
    dataset_filenames = {
        "train_pen": "graph_emolfrag_train_non_pen_data.pkl",
        "dude": "graph_emolfrag_all_dude_data.pkl",
        "test-pen": "graph_emolfrag_test_pen_data.pkl",
        "zinc-all": "df_zinc_dedup_fragments_final.pkl",
    }  
    save_run.log_training_info(f"Dataset files to load: {dataset_filenames}")   
    
    # Efficiently load and concatenate datasets, filter fragment SMILES
    dfs = [pd.read_pickle(os.path.join(BASE_PATH, dataset_filenames[key])) for key in dataset_filenames]  
    df_final = pd.concat(dfs, ignore_index=True)  # Only train, dude, test

    # Check if 'fragments' column exists and print some samples for debugging
    if 'fragments' not in df_final.columns:
        raise KeyError("'fragments' column not found in the loaded DataFrames.")

    frag_smiles = [x for x in df_final['fragments'] if isinstance(x, str) and len(x) > 1]
    print(f"Number of fragment SMILES found: {len(frag_smiles)}")
    smiles_dataset_action_gen=SmilesDatasetActionGenerator( rdkit_mol_action_generator)
    dfs_kwargs={'action_format': 'short','include_atoms': False,'include_bonds': True}
    cache_folder="/home/meisam/GitHub_codes/eDeriv2/assets/seq_actions"
    h_flag=True
    cached_file = os.path.join(
        cache_folder,
        f"smiles_actions_{'_'.join(dataset_filenames.keys())}_"
        f"action_format-{dfs_kwargs['action_format']}_atoms-{dfs_kwargs['include_atoms']}_"
        f"bonds-{dfs_kwargs['include_bonds']}_hflag_{h_flag}.pkl"
        )  
    cached_data=smiles_dataset_action_gen.generate(frag_smiles, dfs_kwargs, dfs_type='single',
                                                   h_flag=h_flag, cache_file=cached_file)
    dataset_actions = cached_data.get('actions', [])
       
    save_run.log_training_info(f"Loaded/Generated {len(dataset_actions)} action sequences from cached file {cached_file}.")
    
    action_counts = Counter([a for seq in dataset_actions for a in seq])
    save_run.log_training_info(f"Most common actions: {action_counts.most_common(10)}")
    
    # === 2. Build vocabulary ===
    save_run.log_training_info("Building vocabulary from dataset actions...")

    actions_vocab = ActionVocab(dataset_actions)
    pad_idx = actions_vocab.get_vocab()['<PAD>']
    start_idx = actions_vocab.get_vocab()['<START>']
    end_idx = actions_vocab.get_vocab()['<END>']
    
    save_run.log_training_info(f"Vocabulary built with size: {len(actions_vocab)}")
    
    # Count token frequencies
    all_tokens = [token for seq in dataset_actions for token in actions_vocab.encode(seq)]
    token_counts = Counter(all_tokens)
    # compute sequence length statistics
    seq_lengths = [len(seq) for seq in dataset_actions]
    lengths_arr = np.array(seq_lengths)
    mean_len = float(lengths_arr.mean())
    std_len = float(lengths_arr.std())
    median_len = float(np.median(lengths_arr))
    min_len = int(lengths_arr.min())
    max_len = int(lengths_arr.max())

    save_run.log_training_info(
        f"Action sequence length stats - "
        f"mean: {mean_len:.2f}, std: {std_len:.2f}, "
        f"median: {median_len:.0f}, min: {min_len}, max: {max_len}"
    )
    vocab_size = len(actions_vocab)
    weights = torch.ones(vocab_size)

    # Choose a weighting function
    weighting_function = get_weighting_function(token_weghting_type)  # Replace 'inverse' with desired weighting type
    for token, idx in actions_vocab.get_vocab().items():
        freq = token_counts.get(idx, 1)
        # Apply the weighting function to calculate weights
        weights[idx] = weighting_function(freq)  

    save_run.log_training_info(f"Token weights calculated using {token_weghting_type} weighting function.")
    # Normalize weights
    weights = weights / weights.sum() * vocab_size 
    min_weight = 0.1
    max_weight = 5.0
    weights = torch.clamp(weights, min=min_weight, max=max_weight)
    
    # === DataLoader for batch processing the data ===
    batch_size=256
    dataset = ActionSequenceDataset(dataset_actions, actions_vocab)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, collate_fn=CollateFunctionFactory.get_collate_function("transformer_nested"))

    save_run.log_training_info(f"DataLoader initialized with batch size {batch_size} and {len(dataset)} samples.")
    save_run.log_training_info(f"Vocabulary size: {len(actions_vocab)}")
    # === Setting Hyperparameters ===
    training_hyperparams = {
        "total_epochs": 1,
        "model_dim": 512,
        "num_heads": 8,
        "num_layers": 4,
        "dropout": 0.1,
        "batch_size": batch_size,
        "learning_rate": 5e-5,
        "pad_idx": pad_idx,
        "start_idx": start_idx,
        "end_idx": end_idx,
        "weights": weights.tolist(),
        "label_smoothing": 0.1,
    }
    save_run.log_training_info(f"Training hyperparameters: {training_hyperparams}")

    # === Instantiate model ===
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model=MolecularActionTransformer(
        vocab_size=len(actions_vocab),
        d_model=training_hyperparams["model_dim"],
        nhead=training_hyperparams["num_heads"],
        num_layers=training_hyperparams["num_layers"],
        dropout=training_hyperparams["dropout"]
    ).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=training_hyperparams["learning_rate"])
    scheduler = ReduceLROnPlateau(optimizer, 'min', patience=4, factor=0.5)
    loss_fn = nn.CrossEntropyLoss(
        ignore_index=training_hyperparams["pad_idx"],
        label_smoothing=training_hyperparams["label_smoothing"],
        weight=torch.tensor(training_hyperparams["weights"], dtype=torch.float32).to(device)
    )

    save_run.model = model
    save_run.log_training_info("Model, optimizer, and loss function initialized.")
    save_run.log_training_info(f"Model architecture: {model}")
    save_run.log_training_info(f"Optimizer: {optimizer}")
    save_run.log_training_info(f"Loss function: {loss_fn}")
    save_run.log_training_info(f"Device: {device}")
    # === Model Training ===
    transformer_trainer=TransformerTrainer(model,optimizer,loss_fn,device, scheduler)
    training_losses=transformer_trainer.train(dataloader, epochs=training_hyperparams["total_epochs"], save_run=save_run)

    save_run.log_training_info(f"Training completed for {training_hyperparams['total_epochs']} epochs.")
    # === Log and Save Results ===
    save_run.log_training_info("Training completed successfully.")
    # Before saving, create scriptable version
    # scriptable_model = ScriptableMolecularActionTransformer(
    #     vocab_size=len(actions_vocab),
    #     d_model=training_hyperparams["model_dim"],
    #     nhead=training_hyperparams["num_heads"],
    #     num_layers=training_hyperparams["num_layers"],
    #     dropout=training_hyperparams["dropout"]
    # )
    # scriptable_model.load_state_dict(model.state_dict())
    # save_run.model = scriptable_model
    checkpoint = {
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'training_hyperparams': training_hyperparams,
                'epoch': training_hyperparams["total_epochs"],
                'loss': training_losses[-1] if training_losses else None
            }
    save_run.save_model(checkpoint, save_torchscript=False)
    save_run.log_training_info("Model saved successfully.")
    
    # Save training losses
    save_run.log_training_info("Saving training metrcis and params...")
    # Save and visualize (if needed) all logged metrics and parameters
    save_run.save_vis_outputs()
    save_run.log_training_info("Training metrcis and params saved successfully.")
    
    

    
    """=== Model Inference ==="""
    max_seq_len=max(len(seq) for seq in actions_vocab.sequences)
    inference_params={"num_samples": 1000, 
                      "temperature": 1.0, 
                      "max_len": max_seq_len, 
                      "greedy": False}  
    
    save_run.log_training_info(f"Starting inference with parameters: {inference_params}")
    
    action_seqs = generate_sequence(model, actions_vocab,
                                   num_samples=inference_params["num_samples"],
                                   temperature=inference_params["temperature"],
                                   max_len=inference_params["max_len"],
                                   greedy=inference_params["greedy"],
                                   device=device)
    
    save_run.log_training_info(f"Generated {len(action_seqs)} action sequences.")
    
    # Print the generated sequences
    save_run.log_training_info("Generated action sequences and smiles:")  

    # === Translate Sequences to SMILES ===
    smiles_handler= SmilesHandler(SmilesHandlingStrategyWithRDKIT())
    smiles_counter={"valid":[],"valid-new":[], "valid-unique":[], "valid-new-unique":[]}
    for i, seq in enumerate(action_seqs):
        save_run.log_training_info(f'Sequence[{i}]: {seq}')
        smiles = MolTranslator().to_smiles(seq)
        save_run.log_training_info(f'SMILES[{i}]: {smiles}')
        is_single_molecule = smiles_handler.is_single_molecule(smiles)
        if smiles is not None and is_single_molecule:
            smiles_counter["valid"].append(smiles)
            is_in_original_smiles = smiles_handler.is_smiles_in_list(smiles, frag_smiles)  
            save_run.log_training_info(f'SMILES[{i}] in original dataset: {is_in_original_smiles}')
            if not is_in_original_smiles:
                smiles_counter["valid-new"].append(smiles)
        else:
            save_run.log_training_info(f'SMILES[{i}] is None or invalid.')
            
    # Determine valid-unique and valid-new-unique lists
    smiles_counter["valid-unique"] = list(set(smiles_counter["valid"]))
    smiles_counter["valid-new-unique"] = list(set(smiles_counter["valid-new"]))# === Inference Conclusion ===
    save_run.log_training_info("Inference completed successfully.") 
    save_run.log_training_info(f"Final Report:")
    # Create a summary table for the SMILES counts
    smiles_summary = {
        "Total Sequences": len(action_seqs),
        "Valid": len(smiles_counter["valid"]),
        "Valid-Unique": len(smiles_counter["valid-unique"]),
        "Valid-New": len(smiles_counter["valid-new"]),
        "Valid-New-Unique": len(smiles_counter["valid-new-unique"]),
    }
    
    # Calculate ratios, handling division by zero
    total = len(action_seqs)
    valid = len(smiles_counter["valid"])
    valid_unique = len(smiles_counter["valid-unique"])
    valid_new = len(smiles_counter["valid-new"])
    valid_new_unique = len(smiles_counter["valid-new-unique"])

    smiles_summary["Valid/Total Seq"] = round(valid / total, 4) if total > 0 else 0.0
    smiles_summary["Valid-Unique/Valid"] = round(valid_unique / valid, 4) if valid > 0 else 0.0
    smiles_summary["Valid-New/Valid"] = round(valid_new / valid, 4) if valid > 0 else 0.0
    smiles_summary["Valid-New-Unique/Valid-New"] = round(valid_new_unique / valid_new, 4) if valid_new > 0 else 0.0

    # Log the summary table
    save_run.log_training_info("SMILES Summary Table:")
    save_run.log_training_info(f"{'Category':<20} | {'Count':<10}")
    save_run.log_training_info("-" * 35)
    for category, count in smiles_summary.items():
        save_run.log_training_info(f"{category:<20} | {count:<10}")  
    
    # Print the new SMILES that are not in the original dataset
    save_run.log_training_info("New unique SMILES not in the original dataset:")
    save_run.log_training_info(", ".join(smiles_counter["valid-new-unique"]))
    