# file_watcher.py
import asyncio
from pathlib import Path
import time
from typing import AsyncGenerator, Dict, Set, Optional, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
import logging
from asyncio import Queue
from threading import Event
from streaming_extractor import StreamingRelationExtractor

class DocumentFileHandler(FileSystemEventHandler):
    """Handles file system events for new document files."""
    
    def __init__(self, file_queue: asyncio.Queue, file_pattern: str = "*.txt"):
        self.file_queue = file_queue
        self.file_pattern = file_pattern
        self.processed_files: Set[str] = set()
        self.logger = logging.getLogger(__name__)

    def on_created(self, event):
        if not isinstance(event, FileCreatedEvent):
            return
            
        file_path = Path(event.src_path)
        if not file_path.match(self.file_pattern):
            return
            
        if str(file_path) in self.processed_files:
            return
            
        # Wait briefly to ensure file is completely written
        time.sleep(0.5)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            asyncio.run_coroutine_threadsafe(
                self.file_queue.put({
                    'id': file_path.stem,
                    'text': content,
                    'path': str(file_path)
                }),
                asyncio.get_event_loop()
            )
            self.processed_files.add(str(file_path))
            self.logger.info(f"Queued new file: {file_path.name}")
            
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {str(e)}")

class DirectoryWatcher:
    """Watches a directory for new files and streams them for processing."""
    
    def __init__(self, 
                 input_dir: str, 
                 file_pattern: str = "*.txt",
                 queue_size: int = 1000):
        self.input_dir = Path(input_dir)
        self.file_pattern = file_pattern
        self.file_queue = asyncio.Queue(maxsize=queue_size)
        self.stop_event = Event()
        self.observer = None
        self.logger = logging.getLogger(__name__)

    def start(self):
        """Start watching the directory."""
        self.input_dir.mkdir(parents=True, exist_ok=True)
        
        # Process existing files first
        asyncio.create_task(self._process_existing_files())
        
        # Start watching for new files
        self.observer = Observer()
        handler = DocumentFileHandler(self.file_queue, self.file_pattern)
        self.observer.schedule(handler, str(self.input_dir), recursive=False)
        self.observer.start()
        self.logger.info(f"Started watching directory: {self.input_dir}")

    def stop(self):
        """Stop watching the directory."""
        self.stop_event.set()
        if self.observer:
            self.observer.stop()
            self.observer.join()
        self.logger.info("Stopped watching directory")

    async def _process_existing_files(self):
        """Process any existing files in the directory."""
        for file_path in self.input_dir.glob(self.file_pattern):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                await self.file_queue.put({
                    'id': file_path.stem,
                    'text': content,
                    'path': str(file_path)
                })
                self.logger.info(f"Queued existing file: {file_path.name}")
                
            except Exception as e:
                self.logger.error(f"Error reading existing file {file_path}: {str(e)}")

    async def stream_documents(self) -> AsyncGenerator[Dict[str, str], None]:
        """Stream documents from the watched directory."""
        while not self.stop_event.is_set() or not self.file_queue.empty():
            try:
                # Wait for new documents with timeout
                doc = await asyncio.wait_for(self.file_queue.get(), timeout=0.1)
                yield doc
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error streaming document: {str(e)}")
                continue

# Update the streaming extractor process_stream method signature
async def process_stream(self, 
                        document_stream: AsyncGenerator[Dict[str, str], None],
                        output_dir: Optional[str] = None) -> AsyncGenerator[Dict[str, Any], None]:
    """Process a stream of documents asynchronously."""
    if not self.processing_thread or not self.processing_thread.is_alive():
        self.stop_event.clear()
        self.processing_thread = Thread(target=self._process_queue)
        self.processing_thread.start()

    try:
        async for document in document_stream:
            doc_id = document.get('id', str(datetime.now().timestamp()))
            text = document.get('text', '').strip()
            
            if not text:
                self.logger.warning(f"Empty document received: {doc_id}")
                continue

            src_lang = self.detect_language(text)
            segments = self.segment_document(text)
            
            for segment in segments:
                self.input_queue.put({
                    'doc_id': doc_id,
                    'segment': segment,
                    'src_lang': src_lang
                })
            
            doc_results = []
            segments_processed = 0
            
            while segments_processed < len(segments):
                result = await self._get_result()
                if result and result['doc_id'] == doc_id:
                    doc_results.extend(result.get('triplets', []))
                    segments_processed += 1
            
            final_result = {
                'doc_id': doc_id,
                'language': src_lang,
                'triplets': doc_results,
                'num_segments': len(segments),
                'path': document.get('path')
            }
            
            if output_dir:
                self._save_document_results(final_result, output_dir)
            
            yield final_result

    except Exception as e:
        self.logger.error(f"Error processing stream: {str(e)}")
        raise
    finally:
        self.stop_event.set()
        if self.processing_thread:
            self.processing_thread.join()

# Example usage
async def main():
    input_dir = "data/input_documents"
    output_dir = "data/processed_documents"
    
    # Initialize the watcher and extractor
    watcher = DirectoryWatcher(input_dir)
    
    try:
        # Try CPU first
        extractor = StreamingRelationExtractor(
            model_name='Babelscape/mrebel-large-32',
            device=0,  # Use CPU
            max_length=1024,
            batch_size=8
        )
    except Exception as e:
        logging.error(f"Failed to initialize extractor: {str(e)}")
        return
    
    try:
        # Start watching the directory
        watcher.start()
        
        # Process documents as they arrive
        async for result in extractor.process_stream(
            watcher.stream_documents(),
            output_dir=output_dir
        ):
            print(f"\nProcessed document: {result['doc_id']}")
            print(f"Found {len(result['triplets'])} relations")
            
            # Optional: Archive or move processed file
            input_file = Path(result.get('path', ''))
            if input_file.exists():
                archive_dir = Path("data/archived_documents")
                archive_dir.mkdir(exist_ok=True)
                input_file.rename(archive_dir / input_file.name)
                
    except KeyboardInterrupt:
        print("\nStopping document processing...")
    finally:
        watcher.stop()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    asyncio.run(main())