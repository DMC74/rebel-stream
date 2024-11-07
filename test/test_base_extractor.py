import pytest
import torch
from typing import List, Dict
from src.base_extractor import BaseRelationExtractor

@pytest.fixture
def base_extractor():
    return BaseRelationExtractor(device=-1)  # Use CPU for testing

@pytest.fixture
def sample_texts():
    return {
        'en': 'Apple Inc. is headquartered in Cupertino, California.',
        'es': 'Madrid es la capital de España.',
        'fr': 'Paris est la capitale de la France.',
        'de': 'Berlin ist die Hauptstadt von Deutschland.',
        'empty': '',
        'short': 'Hi',
    }

class TestBaseExtractor:
    def test_initialization(self, base_extractor):
        assert base_extractor is not None
        assert base_extractor.model_name == 'Babelscape/mrebel-large-32'
        assert base_extractor.device == -1
        assert base_extractor.max_length > 0

    def test_language_detection(self, base_extractor, sample_texts):
        assert base_extractor.detect_language(sample_texts['en']) == 'en_XX'
        assert base_extractor.detect_language(sample_texts['es']) == 'es_XX'
        assert base_extractor.detect_language(sample_texts['fr']) == 'fr_XX'
        assert base_extractor.detect_language(sample_texts['de']) == 'de_DE'
        
        # Test empty and short texts
        assert base_extractor.detect_language(sample_texts['empty']) == 'en_XX'
        assert base_extractor.detect_language(sample_texts['short']) == 'en_XX'

    def test_token_length(self, base_extractor):
        text = "This is a test sentence."
        length = base_extractor.get_token_length(text)
        assert isinstance(length, int)
        assert length > 0

    def test_segment_document(self, base_extractor):
        # Test with short text
        short_text = "This is a short text."
        segments = base_extractor.segment_document(short_text)
        assert isinstance(segments, list)
        assert len(segments) == 1
        assert segments[0] == short_text

        # Test with long text
        long_text = " ".join(["This is sentence number " + str(i) + "." for i in range(100)])
        segments = base_extractor.segment_document(long_text)
        assert isinstance(segments, list)
        assert len(segments) > 1
        assert all(base_extractor.get_token_length(seg) <= base_extractor.safe_length 
                  for seg in segments)

    def test_process_segment(self, base_extractor):
        text = "Apple Inc. is headquartered in Cupertino, California."
        lang = "en_XX"
        results = base_extractor.process_segment(text, lang)
        
        assert isinstance(results, list)
        for relation in results:
            assert isinstance(relation, dict)
            assert 'head' in relation
            assert 'head_type' in relation
            assert 'type' in relation
            assert 'tail' in relation
            assert 'tail_type' in relation

    def test_error_handling(self, base_extractor):
        # Test with None input
        with pytest.raises(Exception):
            base_extractor.detect_language(None)
        
        # Test with invalid language
        with pytest.raises(Exception):
            base_extractor.process_segment("Test text", "invalid_lang")

    @pytest.mark.skipif(not torch.cuda.is_available(), 
                       reason="GPU not available")
    def test_gpu_support(self):
        gpu_extractor = BaseRelationExtractor(device=0)
        assert gpu_extractor.device == 0
        
        # Test processing on GPU
        text = "Apple Inc. is headquartered in Cupertino."
        results = gpu_extractor.process_segment(text, "en_XX")
        assert isinstance(results, list)