import unittest
from unittest.mock import Mock, patch
import torch
from shorttext_bert.scorer import BERTScorer


class TestBERTScorer(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        pass

    @patch('shorttext_bert.scorer.WrappedBERTEncoder')
    def test_init_with_default_values(self, mock_encoder):
        """Test initialization with default values"""
        # Setup mocks
        mock_encoder_instance = Mock()
        mock_encoder.return_value = mock_encoder_instance
        mock_encoder_instance.device = torch.device('cpu')
        
        # Test with default values
        scorer = BERTScorer()
        
        # Assertions
        self.assertIsInstance(scorer.encoder, Mock)
        mock_encoder.assert_called_once()

    @patch('shorttext_bert.scorer.WrappedBERTEncoder')
    def test_init_with_custom_parameters(self, mock_encoder):
        """Test initialization with custom parameters"""
        # Setup mocks
        mock_encoder_instance = Mock()
        mock_encoder.return_value = mock_encoder_instance
        mock_encoder_instance.device = torch.device('cpu')
        
        # Test with custom parameters
        scorer = BERTScorer(
            model='custom-model',
            tokenizer='custom-tokenizer',
            max_length=64,
            nbencodinglayers=6,
            device='cpu'
        )
        
        # Assertions
        mock_encoder.assert_called_once_with(
            model='custom-model',
            tokenizer='custom-tokenizer',
            max_length=64,
            nbencodinglayers=6,
            device='cpu'
        )

    @patch('shorttext_bert.scorer.WrappedBERTEncoder')
    @patch('shorttext_bert.scorer.torch.nn.CosineSimilarity')
    def test_compute_matrix(self, mock_cosine_similarity, mock_encoder):
        """Test compute_matrix method"""
        # Setup mocks
        mock_encoder_instance = Mock()
        mock_encoder.return_value = mock_encoder_instance
        mock_encoder_instance.device = torch.device('cpu')
        
        mock_cosine_instance = Mock()
        mock_cosine_similarity.return_value = mock_cosine_instance
        
        # Mock encoder behavior
        mock_embeddings = torch.tensor([[[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]])
        mock_encoder_instance.encode_sentences.side_effect = [
            (None, mock_embeddings, [['[CLS]', 'hello', '[SEP]']]),
            (None, mock_embeddings, [['[CLS]', 'world', '[SEP]']])
        ]
        
        # Mock cosine similarity behavior
        mock_cosine_instance.return_value = torch.tensor([0.8])
        
        # Create scorer
        scorer = BERTScorer()
        
        # Test compute_matrix
        similarity_matrix = scorer.compute_matrix("Hello", "World")
        
        # Assertions
        self.assertIsInstance(similarity_matrix, torch.Tensor)
        mock_encoder_instance.encode_sentences.assert_called()

    @patch('shorttext_bert.scorer.WrappedBERTEncoder')
    @patch('shorttext_bert.scorer.torch.nn.CosineSimilarity')
    def test_recall_bertscore(self, mock_cosine_similarity, mock_encoder):
        """Test recall_bertscore method"""
        # Setup mocks
        mock_encoder_instance = Mock()
        mock_encoder.return_value = mock_encoder_instance
        mock_encoder_instance.device = torch.device('cpu')
        
        mock_cosine_instance = Mock()
        mock_cosine_similarity.return_value = mock_cosine_instance
        
        # Mock encoder behavior
        mock_embeddings = torch.tensor([[[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]])
        mock_encoder_instance.encode_sentences.side_effect = [
            (None, mock_embeddings, [['[CLS]', 'hello', '[SEP]']]),
            (None, mock_embeddings, [['[CLS]', 'world', '[SEP]']])
        ]
        
        # Mock cosine similarity behavior
        mock_cosine_instance.return_value = torch.tensor([0.8])
        
        # Mock torch.max to return specific values
        with patch('src.shorttext_bert.scorer.torch.max') as mock_torch_max:
            mock_torch_max.return_value.values = torch.tensor([0.9])
            
            # Create scorer
            scorer = BERTScorer()
            
            # Test recall_bertscore
            recall_score = scorer.recall_bertscore("Hello", "World")
            
            # Assertions
            self.assertIsInstance(recall_score, float)
            self.assertEqual(recall_score, 0.9)

    @patch('shorttext_bert.scorer.WrappedBERTEncoder')
    @patch('shorttext_bert.scorer.torch.nn.CosineSimilarity')
    def test_precision_bertscore(self, mock_cosine_similarity, mock_encoder):
        """Test precision_bertscore method"""
        # Setup mocks
        mock_encoder_instance = Mock()
        mock_encoder.return_value = mock_encoder_instance
        mock_encoder_instance.device = torch.device('cpu')
        
        mock_cosine_instance = Mock()
        mock_cosine_similarity.return_value = mock_cosine_instance
        
        # Mock encoder behavior
        mock_embeddings = torch.tensor([[[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]])
        mock_encoder_instance.encode_sentences.side_effect = [
            (None, mock_embeddings, [['[CLS]', 'hello', '[SEP]']]),
            (None, mock_embeddings, [['[CLS]', 'world', '[SEP]']])
        ]
        
        # Mock cosine similarity behavior
        mock_cosine_instance.return_value = torch.tensor([0.8])
        
        # Mock torch.max to return specific values
        with patch('src.shorttext_bert.scorer.torch.max') as mock_torch_max:
            mock_torch_max.return_value.values = torch.tensor([0.7])
            
            # Create scorer
            scorer = BERTScorer()
            
            # Test precision_bertscore
            precision_score = scorer.precision_bertscore("Hello", "World")
            
            # Assertions
            self.assertIsInstance(precision_score, float)
            self.assertEqual(precision_score, 0.7)

    @patch('shorttext_bert.scorer.WrappedBERTEncoder')
    @patch('shorttext_bert.scorer.torch.nn.CosineSimilarity')
    def test_f1score_bertscore(self, mock_cosine_similarity, mock_encoder):
        """Test f1score_bertscore method"""
        # Setup mocks
        mock_encoder_instance = Mock()
        mock_encoder.return_value = mock_encoder_instance
        mock_encoder_instance.device = torch.device('cpu')
        
        mock_cosine_instance = Mock()
        mock_cosine_similarity.return_value = mock_cosine_instance
        
        # Mock encoder behavior
        mock_embeddings = torch.tensor([[[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]])
        mock_encoder_instance.encode_sentences.side_effect = [
            (None, mock_embeddings, [['[CLS]', 'hello', '[SEP]']]),
            (None, mock_embeddings, [['[CLS]', 'world', '[SEP]']])
        ]
        
        # Mock cosine similarity behavior
        mock_cosine_instance.return_value = torch.tensor([0.8])
        
        # Mock torch.max to return specific values
        with patch('src.shorttext_bert.scorer.torch.max') as mock_torch_max:
            mock_torch_max.return_value.values = torch.tensor([0.8])
            
            # Create scorer
            scorer = BERTScorer()
            
            # Test f1score_bertscore (with recall=0.8, precision=0.8, so F1 should be 0.8)
            f1_score = scorer.f1score_bertscore("Hello", "World")
            
            # Assertions
            self.assertIsInstance(f1_score, float)
            self.assertEqual(f1_score, 0.8)


if __name__ == '__main__':
    unittest.main()