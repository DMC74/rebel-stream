import pytest
import asyncio
from typing import AsyncGenerator, Dict, Any
from src.streaming_extractor import StreamingRelationExtractor
import tempfile
from pathlib import Path

@pytest.fixture
def streaming_extractor():
    return StreamingRelationExtractor(
        device=-1,
        batch_size=2,
        queue_size=10
    )

@pytest.fixture
async def sample_document_stream():
    async def generate_documents():
        documents = [
            {
                'id': 'doc1',
                'text': 'Apple Inc. is headquartered in Cupertino, California.'
            },
            {
                'id': 'doc2',
                'text': 'Microsoft was founded by Bill Gates.'
            }
        ]
        for doc in documents:
            yield doc
    return generate_documents()

class TestStreamingExtractor:
    @pytest.mark.asyncio
    async def test_initialization(self, streaming_extractor):
        assert streaming_extractor is not None
        assert streaming_extractor.batch_size == 2
        assert not streaming_extractor.stop_event.is_set()

    @pytest.mark.asyncio
    async def test_process_stream(self, streaming_extractor, sample_document_stream):
        results = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            async for result in streaming_extractor.process_stream(
                sample_document_stream,
                output_dir=temp_dir
            ):
                results.append(result)
        
        assert len(results) == 2
        assert all(isinstance(r, dict) for r in results)
        assert all('doc_id' in r for r in results)
        assert all('triplets' in r for r in results)

    @pytest.mark.asyncio
    async def test_empty_stream(self, streaming_extractor):
        async def empty_stream():
            if False:
                yield  # Empty generator
                
        results = []
        async for result in streaming_extractor.process_stream(empty_stream()):
            results.append(result)
        
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_error_handling(self, streaming_extractor):
        async def error_stream():
            yield {'id': 'error_doc', 'text': None}
            
        results = []
        async for result in streaming_extractor.process_stream(error_stream()):
            results.append(result)
        
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_batch_processing(self, streaming_extractor):
        async def large_stream():
            for i in range(5):
                yield {
                    'id': f'doc{i}',
                    'text': f'This is test document {i}.'
                }
        
        results = []
        async for result in streaming_extractor.process_stream(large_stream()):
            results.append(result)
        
        assert len(results) == 5
        assert all(r['doc_id'].startswith('doc') for r in results)

    @pytest.mark.asyncio
    async def test_output_saving(self, streaming_extractor, sample_document_stream):
        with tempfile.TemporaryDirectory() as temp_dir:
            async for _ in streaming_extractor.process_stream(
                sample_document_stream,
                output_dir=temp_dir
            ):
                pass
            
            # Check if files were created
            output_path = Path(temp_dir)
            json_files = list(output_path.glob('*.json'))
            assert len(json_files) == 2