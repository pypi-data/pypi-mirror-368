
from abc import ABC, abstractmethod
import warnings

import torch
from transformers import BertTokenizer, BertModel


class BERTObject(ABC):
    """ The base class for BERT model that contains the embedding model and the tokenizer.

    For more information, please refer to the following paper:

    Jacob Devlin, Ming-Wei Chang, Kenton Lee, Kristina Toutanova, "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding," arXiv:1810.04805 (2018). [`arXiv
    <https://arxiv.org/abs/1810.04805>`_]

    """
    def __init__(self, model=None, tokenizer=None, trainable=False, device='cpu'):
        """ The base class for BERT model that contains the embedding model and the tokenizer.

        :param model: BERT model (default: None, with model `bert-base-uncase` to be used)
        :param tokenizer: BERT tokenizer (default: None, with model `bert-base-uncase` to be used)
        :param device: device the language model is stored (default: `cpu`)
        :type model: str
        :type tokenizer: str
        :type device: str
        """
        if device == 'cuda':
            if torch.cuda.is_available():
                self.device = torch.device('cuda')
            else:
                warnings.warn("CUDA is not available. Device set to 'cpu'.")
                self.device = torch.device('cpu')
        else:
            self.device = torch.device(device)

        self.trainable = trainable

        if model is None:
            self.model = BertModel.from_pretrained('bert-base-uncased',
                                                   output_hidden_states=True)\
                            .to(self.device)
        else:
            self.model = model.to(self.device)

        if self.trainable:
            self.model.train()

        if tokenizer is None:
            self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)
        else:
            self.tokenizer = tokenizer

        self.number_hidden_layers = self.model.config.num_hidden_layers

    @abstractmethod
    def encode_sentences(self, sentences, numpy=False):
        raise NotImplemented()
