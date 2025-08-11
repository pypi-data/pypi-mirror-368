import unittest
from unittest.mock import Mock, patch
import torch
from shorttext_bert.bertobj import BERTObject


class TestBERTObject(unittest.TestCase):

    def test_abstract_class_cannot_be_instantiated(self):
        """Test that BERTObject cannot be instantiated directly since it's abstract"""
        with self.assertRaises(TypeError):
            BERTObject()

    @patch('shorttext_bert.bertobj.BertModel')
    @patch('shorttext_bert.bertobj.BertTokenizer')
    def test_init_with_default_values(self, mock_tokenizer, mock_model):
        """Test initialization with default values"""
        # Setup mocks
        mock_model_instance = Mock()
        mock_model_instance.config.num_hidden_layers = 12
        mock_model.from_pretrained.return_value = mock_model_instance
        
        mock_tokenizer_instance = Mock()
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        # Create a concrete implementation for testing
        class ConcreteBERTObject(BERTObject):
            def encode_sentences(self, sentences, numpy=False):
                pass
        
        # Test with default values
        bert_obj = ConcreteBERTObject()
        
        # Assertions
        self.assertEqual(bert_obj.device, torch.device('cpu'))
        self.assertFalse(bert_obj.trainable)
        mock_model.from_pretrained.assert_called_with('bert-base-uncased', output_hidden_states=True)
        mock_tokenizer.from_pretrained.assert_called_with('bert-base-uncased', do_lower_case=True)

    @patch('shorttext_bert.bertobj.BertModel')
    @patch('shorttext_bert.bertobj.BertTokenizer')
    def test_init_with_custom_model_and_tokenizer(self, mock_tokenizer, mock_model):
        """Test initialization with custom model and tokenizer"""
        # Setup mocks
        mock_model_instance = Mock()
        mock_model_instance.config.num_hidden_layers = 12
        mock_model_instance.to.return_value = mock_model_instance
        
        mock_tokenizer_instance = Mock()
        
        # Create a concrete implementation for testing
        class ConcreteBERTObject(BERTObject):
            def encode_sentences(self, sentences, numpy=False):
                pass
        
        # Test with custom model and tokenizer
        bert_obj = ConcreteBERTObject(model=mock_model_instance, tokenizer=mock_tokenizer_instance)
        
        # Assertions
        self.assertEqual(bert_obj.model, mock_model_instance)
        self.assertEqual(bert_obj.tokenizer, mock_tokenizer_instance)

    @patch('shorttext_bert.bertobj.torch.cuda.is_available')
    @patch('shorttext_bert.bertobj.BertModel')
    @patch('shorttext_bert.bertobj.BertTokenizer')
    def test_init_with_cuda_device_when_available(self, mock_tokenizer, mock_model, mock_cuda_available):
        """Test initialization with CUDA device when available"""
        # Setup mocks
        mock_cuda_available.return_value = True
        mock_model_instance = Mock()
        mock_model_instance.config.num_hidden_layers = 12
        mock_model.from_pretrained.return_value = mock_model_instance
        
        mock_tokenizer_instance = Mock()
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        # Create a concrete implementation for testing
        class ConcreteBERTObject(BERTObject):
            def encode_sentences(self, sentences, numpy=False):
                pass
        
        # Test with CUDA device
        bert_obj = ConcreteBERTObject(device='cuda')
        
        # Assertions
        self.assertEqual(bert_obj.device, torch.device('cuda'))

    @patch('shorttext_bert.bertobj.torch.cuda.is_available')
    @patch('shorttext_bert.bertobj.BertModel')
    @patch('shorttext_bert.bertobj.BertTokenizer')
    def test_init_with_cuda_device_when_not_available(self, mock_tokenizer, mock_model, mock_cuda_available):
        """Test initialization with CUDA device when not available"""
        # Setup mocks
        mock_cuda_available.return_value = False
        mock_model_instance = Mock()
        mock_model_instance.config.num_hidden_layers = 12
        mock_model.from_pretrained.return_value = mock_model_instance
        
        mock_tokenizer_instance = Mock()
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        # Create a concrete implementation for testing
        class ConcreteBERTObject(BERTObject):
            def encode_sentences(self, sentences, numpy=False):
                pass
        
        # Test with CUDA device when not available
        with self.assertWarns(UserWarning):
            bert_obj = ConcreteBERTObject(device='cuda')
        
        # Assertions
        self.assertEqual(bert_obj.device, torch.device('cpu'))

    @patch('shorttext_bert.bertobj.BertModel')
    @patch('shorttext_bert.bertobj.BertTokenizer')
    def test_init_with_trainable_flag(self, mock_tokenizer, mock_model):
        """Test initialization with trainable flag"""
        # Setup mocks
        mock_model_instance = Mock()
        mock_model_instance.config.num_hidden_layers = 12
        mock_model_instance.train = Mock()
        mock_model.from_pretrained.return_value = mock_model_instance
        
        mock_tokenizer_instance = Mock()
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        # Create a concrete implementation for testing
        class ConcreteBERTObject(BERTObject):
            def encode_sentences(self, sentences, numpy=False):
                pass
        
        # Test with trainable flag
        bert_obj = ConcreteBERTObject(trainable=True)
        
        # Assertions
        self.assertTrue(bert_obj.trainable)
        mock_model_instance.train.assert_called_once()


if __name__ == '__main__':
    unittest.main()