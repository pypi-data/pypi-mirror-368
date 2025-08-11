"""
Test fixtures and helper functions for unit tests.
"""
import torch
import numpy as np


def create_mock_model_output(batch_size=1, seq_length=3, hidden_size=2, num_hidden_layers=12):
    """
    Create a mock model output for testing.
    
    :param batch_size: Number of sentences in batch
    :param seq_length: Length of token sequence
    :param hidden_size: Size of hidden layer
    :param num_hidden_layers: Number of hidden layers
    :return: Mock model output tuple
    """
    # last_hidden_state: [batch_size, seq_length, hidden_size]
    last_hidden_state = torch.randn(batch_size, seq_length, hidden_size)
    
    # pooler_output: [batch_size, hidden_size]
    pooler_output = torch.randn(batch_size, hidden_size)
    
    # hidden_states: List of [batch_size, seq_length, hidden_size] tensors
    hidden_states = [torch.randn(batch_size, seq_length, hidden_size) for _ in range(num_hidden_layers + 1)]
    
    return (last_hidden_state, pooler_output, hidden_states)


def create_mock_tokenizer_output(input_ids=None, attention_mask=None):
    """
    Create a mock tokenizer output for testing.
    
    :param input_ids: Input IDs tensor
    :param attention_mask: Attention mask tensor
    :return: Mock tokenizer output dictionary
    """
    if input_ids is None:
        input_ids = torch.tensor([[101, 2023, 102]])  # [CLS] hello [SEP]
    
    if attention_mask is None:
        attention_mask = torch.ones_like(input_ids)
    
    return {
        'input_ids': input_ids,
        'attention_mask': attention_mask
    }


def create_sample_sentences():
    """
    Create sample sentences for testing.
    
    :return: List of sample sentences
    """
    return [
        "Hello world",
        "Goodbye world",
        "This is a test sentence",
        "BERT is a powerful language model"
    ]


def create_sample_tokenized_texts():
    """
    Create sample tokenized texts for testing.
    
    :return: List of sample tokenized texts
    """
    return [
        ['[CLS]', 'hello', 'world', '[SEP]'],
        ['[CLS]', 'goodbye', 'world', '[SEP]'],
        ['[CLS]', 'this', 'is', 'a', 'test', 'sentence', '[SEP]'],
        ['[CLS]', 'bert', 'is', 'a', 'powerful', 'language', 'model', '[SEP]']
    ]


def assert_tensors_equal(tensor1, tensor2, tolerance=1e-6):
    """
    Assert that two tensors are equal within a tolerance.
    
    :param tensor1: First tensor
    :param tensor2: Second tensor
    :param tolerance: Tolerance for comparison
    """
    assert torch.allclose(tensor1, tensor2, atol=tolerance), f"Tensors not equal within tolerance {tolerance}"


def assert_arrays_equal(array1, array2, tolerance=1e-6):
    """
    Assert that two numpy arrays are equal within a tolerance.
    
    :param array1: First array
    :param array2: Second array
    :param tolerance: Tolerance for comparison
    """
    assert np.allclose(array1, array2, atol=tolerance), f"Arrays not equal within tolerance {tolerance}"