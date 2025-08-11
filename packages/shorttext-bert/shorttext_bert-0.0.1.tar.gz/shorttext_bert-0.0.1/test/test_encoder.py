import unittest
from unittest.mock import Mock, patch
import torch
import numpy as np
from shorttext_bert.encoder import WrappedBERTEncoder


class TestWrappedBERTEncoder(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        pass

    @patch('shorttext_bert.encoder.BertModel')
    @patch('shorttext_bert.encoder.BertTokenizer')
    def test_init_with_default_values(self, mock_tokenizer, mock_model):
        """Test initialization with default values"""
        # Setup mocks
        mock_model_instance = Mock()
        mock_model_instance.config.num_hidden_layers = 12
        mock_model.from_pretrained.return_value = mock_model_instance
        
        mock_tokenizer_instance = Mock()
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        # Test with default values
        encoder = WrappedBERTEncoder()
        
        # Assertions
        self.assertEqual(encoder.max_length, 48)
        self.assertEqual(encoder.nbencodinglayers, 4)
        mock_model.from_pretrained.assert_called_with('bert-base-uncased', output_hidden_states=True)
        mock_tokenizer.from_pretrained.assert_called_with('bert-base-uncased', do_lower_case=True)

    @patch('shorttext_bert.encoder.BertModel')
    @patch('shorttext_bert.encoder.BertTokenizer')
    def test_init_with_custom_parameters(self, mock_tokenizer, mock_model):
        """Test initialization with custom parameters"""
        # Setup mocks
        mock_model_instance = Mock()
        mock_model_instance.config.num_hidden_layers = 12
        mock_model_instance.to.return_value = mock_model_instance
        
        mock_tokenizer_instance = Mock()
        
        # Test with custom parameters
        encoder = WrappedBERTEncoder(
            model=mock_model_instance,
            tokenizer=mock_tokenizer_instance,
            max_length=64,
            nbencodinglayers=6,
            trainable=True,
            device='cpu'
        )
        
        # Assertions
        self.assertEqual(encoder.max_length, 64)
        self.assertEqual(encoder.nbencodinglayers, 6)
        self.assertTrue(encoder.trainable)
        self.assertEqual(encoder.model, mock_model_instance)
        self.assertEqual(encoder.tokenizer, mock_tokenizer_instance)

    @patch('shorttext_bert.encoder.BertModel')
    @patch('shorttext_bert.encoder.BertTokenizer')
    def test_encode_sentences_with_torch_output(self, mock_tokenizer, mock_model):
        """Test encode_sentences method with torch tensor output"""
        # Setup mocks
        mock_model_instance = Mock()
        mock_model_instance.config.num_hidden_layers = 12
        mock_model.from_pretrained.return_value = mock_model_instance
        
        mock_tokenizer_instance = Mock()
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        # Mock tokenizer behavior
        mock_encoded_dict = {'input_ids': torch.tensor([[101, 2023, 102]])}
        mock_tokenizer_instance.encode_plus.return_value = mock_encoded_dict
        mock_tokenizer_instance.tokenize.return_value = ['[CLS]', 'hello', '[SEP]']
        
        # Mock model output
        mock_model_output = (
            torch.tensor([[[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]]),  # last_hidden_state
            torch.tensor([[0.1, 0.2]]),  # pooler_output
            [torch.tensor([[[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]])] * 13  # hidden_states
        )
        mock_model_instance.return_value = mock_model_output
        
        # Create encoder
        encoder = WrappedBERTEncoder()
        
        # Test encode_sentences
        sentences = ["Hello world"]
        sentences_embeddings, token_embeddings, tokenized_texts = encoder.encode_sentences(sentences)
        
        # Assertions
        self.assertIsInstance(sentences_embeddings, torch.Tensor)
        self.assertIsInstance(token_embeddings, torch.Tensor)
        self.assertIsInstance(tokenized_texts, list)
        self.assertEqual(len(tokenized_texts), 1)

    @patch('shorttext_bert.encoder.BertModel')
    @patch('shorttext_bert.encoder.BertTokenizer')
    def test_encode_sentences_with_numpy_output(self, mock_tokenizer, mock_model):
        """Test encode_sentences method with numpy array output"""
        # Setup mocks
        mock_model_instance = Mock()
        mock_model_instance.config.num_hidden_layers = 12
        mock_model.from_pretrained.return_value = mock_model_instance
        
        mock_tokenizer_instance = Mock()
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        # Mock tokenizer behavior
        mock_encoded_dict = {'input_ids': torch.tensor([[101, 2023, 102]])}
        mock_tokenizer_instance.encode_plus.return_value = mock_encoded_dict
        mock_tokenizer_instance.tokenize.return_value = ['[CLS]', 'hello', '[SEP]']
        
        # Mock model output
        mock_model_output = (
            torch.tensor([[[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]]),  # last_hidden_state
            torch.tensor([[0.1, 0.2]]),  # pooler_output
            [torch.tensor([[[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]])] * 13  # hidden_states
        )
        mock_model_instance.return_value = mock_model_output
        
        # Create encoder
        encoder = WrappedBERTEncoder()
        
        # Test encode_sentences with numpy output
        sentences = ["Hello world"]
        sentences_embeddings, token_embeddings, tokenized_texts = encoder.encode_sentences(sentences, numpy=True)
        
        # Assertions
        self.assertIsInstance(sentences_embeddings, np.ndarray)
        self.assertIsInstance(token_embeddings, np.ndarray)
        self.assertIsInstance(tokenized_texts, list)

    @patch('shorttext_bert.encoder.BertModel')
    @patch('shorttext_bert.encoder.BertTokenizer')
    def test_encode_sentences_multiple_sentences(self, mock_tokenizer, mock_model):
        """Test encode_sentences method with multiple sentences"""
        # Setup mocks
        mock_model_instance = Mock()
        mock_model_instance.config.num_hidden_layers = 12
        mock_model.from_pretrained.return_value = mock_model_instance
        
        mock_tokenizer_instance = Mock()
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        # Mock tokenizer behavior
        mock_encoded_dict = {'input_ids': torch.tensor([[101, 2023, 102]])}
        mock_tokenizer_instance.encode_plus.return_value = mock_encoded_dict
        mock_tokenizer_instance.tokenize.return_value = ['[CLS]', 'hello', '[SEP]']
        
        # Mock model output
        mock_model_output = (
            torch.tensor([[[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]]),  # last_hidden_state
            torch.tensor([[0.1, 0.2]]),  # pooler_output
            [torch.tensor([[[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]])] * 13  # hidden_states
        )
        mock_model_instance.return_value = mock_model_output
        
        # Create encoder
        encoder = WrappedBERTEncoder()
        
        # Test encode_sentences with multiple sentences
        sentences = ["Hello world", "Goodbye world"]
        sentences_embeddings, token_embeddings, tokenized_texts = encoder.encode_sentences(sentences)
        
        # Assertions
        self.assertIsInstance(sentences_embeddings, torch.Tensor)
        self.assertIsInstance(token_embeddings, torch.Tensor)
        self.assertEqual(len(tokenized_texts), 2)


if __name__ == '__main__':
    unittest.main()