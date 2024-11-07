import pytest
import asyncio
import tempfile
from pathlib import Path
import time
from src.file_watcher import DirectoryWatcher

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def watcher(temp_dir):
    watcher = DirectoryWatcher(temp_dir)
    yield watcher
    watcher.stop()

class TestDirectoryWatcher:
    @pytest.mark.asyncio
    async def test_initialization(self, watcher, temp_dir):
        assert watcher.input_dir == Path(temp_dir)
        assert not watcher.stop_event.is_set()
        assert watcher.file_pattern == "*.txt"

    @pytest.mark.asyncio
    async def test_file_detection(self, watcher, temp_dir):
        # Start watcher
        watcher.start()
        
        # Create test file
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("This is a test document.")
        
        # Wait for file processing
        time.sleep(1)
        
        # Get first document
        async def get_first_doc():
            async for doc in watcher.stream_documents():
                return doc
        
        doc = await asyncio.wait_for(get_first_doc(), timeout=5)
        
        assert doc is not None
        assert doc['id'] == "test"
        assert "This is a test document" in doc['text']

    @pytest.mark.asyncio
    async def test_multiple_files(self, watcher, temp_dir):
        watcher.start()
        
        # Create multiple files
        files = []
        for i in range(3):
            file_path = Path(temp_dir) / f"doc{i}.txt"
            file_path.write_text(f"Document {i} content")
            files.append(file_path)
        
        # Wait for file processing
        time.sleep(1)
        
        # Collect all documents
        docs = []
        async for doc in watcher.stream_documents():
            docs.append(doc)
            if len(docs) == 3:
                break
        
        assert len(docs) == 3
        assert all('doc' in doc['id'] for doc in docs)

    @pytest.mark.asyncio
    async def test_file_patterns(self, watcher, temp_dir):
        # Test with non-matching file
        watcher.start()
        
        wrong_file = Path(temp_dir) / "test.pdf"
        wrong_file.write_text("Wrong format")
        
        # Wait briefly
        time.sleep(1)
        
        # Should not detect any documents
        docs = []
        async def collect_docs():
            async for doc in watcher.stream_documents():
                docs.append(doc)
        
        try:
            await asyncio.wait_for(collect_docs(), timeout=2)
        except asyncio.TimeoutError:
            pass
        
        assert len(docs) == 0

    @pytest.mark.asyncio
    async def test_empty_files(self, watcher, temp_dir):
        watcher.start()
        
        # Create empty file
        empty_file = Path(temp_dir) / "empty.txt"
        empty_file.touch()
        
        # Wait briefly
        time.sleep(1)
        
        # Should handle empty file
        docs = []
        async for doc in watcher.stream_documents():
            docs.append(doc)
            break
        
        assert len(docs) == 1
        assert docs[0]['text'] == ''

    @pytest.mark.asyncio
    async def test_stop_watching(self, watcher, temp_dir):
        watcher.start()
        
        # Create initial file
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("Initial content")
        
        # Wait briefly
        time.sleep(1)
        
        # Stop watcher
        watcher.stop()
        
        # Create another file
        new_file = Path(temp_dir) / "new.txt"
        new_file.write_text("New content")
        
        # Should only get the first file
        docs = []
        async for doc in watcher.stream_documents():
            docs.append(doc)
        
        assert len(docs) == 1
        assert docs[0]['id'] == "test"