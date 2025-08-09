"""A module to generate vocabulary dictionary used for different goals"""



from typing import Any
from src.input_tools.transformers.action_gen import  RDKitMolDFSActionGenerator, SmilesDatasetActionGenerator


class ActionVocab:
    def __init__(self, sequences, special_tokens=None):
        """
        sequences: List of lists of action strings (action sequences).
        special_tokens: Optional list of reserved tokens, like ['<PAD>', '<START>', '<END>', '<UNK>']
        """
        self.sequences = sequences
        self.special_tokens = special_tokens or ['<PAD>', '<START>', '<END>', '<UNK>']
        self._build_vocab()
        
        

    def _build_vocab(self):
        # Flatten all actions and remove duplicates
        unique_actions = set(action for seq in self.sequences for action in seq)

        # Ensure special tokens don’t get duplicated if already in data
        unique_actions -= set(self.special_tokens)

        # Final token list with special tokens first
        self.idx2action = self.special_tokens + sorted(unique_actions)
        self.action2idx = {action: idx for idx, action in enumerate(self.idx2action)}
        

    def encode(self, sequence):
        """
        Convert sequence of actions to list of indices.
        Unknown actions are mapped to <UNK>.
        """
        return [self.action2idx.get(action, self.action2idx["<UNK>"]) for action in sequence]

    def decode(self, indices):
        """
        Convert list of indices back to action strings.
        """
        return [self.idx2action[idx] for idx in indices]

    def vocab_size(self):
        return len(self.idx2action)

    def get_vocab(self):
        return self.action2idx

    def get_index_to_action_map(self):
        return self.idx2action
    
    def __len__(self):
        if not self.idx2action:
            raise ValueError("Unique actions do not exist!")
        return len(self.idx2action)



if __name__=="__main__":
    """ Generate list of actions for the smiles dataset """
    import pandas as pd
    
    rdkit_mol_action_generator = RDKitMolDFSActionGenerator()
    
    BASE_PATH = "/home/meisam/GitHub_codes/eDeriv2/assets/datasets/"
    # BASE_PATH = "/home/magesh/eDeriv/graph_variation/"
    
    dataset_filenames=['graph_emolfrag_train_non_pen_data.pkl','graph_emolfrag_all_dude_data.pkl',
                       'graph_emolfrag_test_pen_data.pkl']
    
    df_train = pd.read_pickle(BASE_PATH + 'graph_emolfrag_train_non_pen_data.pkl')
    df_train_dude = pd.read_pickle(BASE_PATH + 'graph_emolfrag_all_dude_data.pkl')
    df_test = pd.read_pickle(BASE_PATH + 'graph_emolfrag_test_pen_data.pkl')

    final = [df_train, df_train_dude, df_test]
    df_final = pd.concat(final)
    frag_smiles = df_final['fragments'].tolist()
    frag_smiles = [x for x in frag_smiles if len(x) > 1]
    h_flag=False
    smiles_dataset_action_gen=SmilesDatasetActionGenerator(frag_smiles, rdkit_mol_action_generator)
    dfs_kwargs={'action_format': 'short','include_atoms': False,'include_bonds': True}
    dataset_actions=smiles_dataset_action_gen.generate(dfs_kwargs)
    
    # Build the vocabulary from the list of actions
    action_vocab_builder=ActionVocab(sequences=dataset_actions)
    print(len(action_vocab_builder))
    print(f'Generated dict for the molecular actions:\n {action_vocab_builder.idx2action}')
    
    
