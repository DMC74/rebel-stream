# streaming_extractor.py
import os
from pathlib import Path
import json
from typing import AsyncGenerator, Dict, Any, Optional
from queue import Queue
from threading import Thread, Event
import asyncio
from datetime import datetime
from base_extractor import BaseRelationExtractor

class StreamingRelationExtractor(BaseRelationExtractor):
    """Streaming version of the relation extractor."""
    
    def __init__(self, 
                 model_name: str = 'Babelscape/mrebel-large-32', 
                 device: int = 0,
                 max_length: int = 1024,
                 batch_size: int = 8,
                 queue_size: int = 1000):
        super().__init__(model_name, device, max_length)
        
        self.batch_size = batch_size
        self.input_queue = Queue(maxsize=queue_size)
        self.output_queue = Queue()
        self.stop_event = Event()
        self.processing_thread = None

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

    def _process_queue(self):
        """Background thread for processing segments from the queue."""
        while not self.stop_event.is_set() or not self.input_queue.empty():
            batch = []
            batch_ids = []
            
            while len(batch) < self.batch_size and not self.input_queue.empty():
                try:
                    item = self.input_queue.get_nowait()
                    batch.append(item)
                    batch_ids.append(item['doc_id'])
                except:
                    break
                    
            if not batch:
                if self.stop_event.is_set():
                    break
                continue
                
            try:
                for item in batch:
                    triplets = self.process_segment(item['segment'], item['src_lang'])
                    self.output_queue.put({
                        'doc_id': item['doc_id'],
                        'triplets': triplets
                    })
            except Exception as e:
                self.logger.error(f"Error processing batch: {str(e)}")
                for doc_id in batch_ids:
                    self.output_queue.put({
                        'doc_id': doc_id,
                        'triplets': []
                    })

    async def _get_result(self) -> Optional[Dict[str, Any]]:
        """Get result from output queue asynchronously."""
        while True:
            try:
                return self.output_queue.get_nowait()
            except:
                await asyncio.sleep(0.1)
                if self.stop_event.is_set() and self.output_queue.empty():
                    return None

    def _save_document_results(self, result: Dict[str, Any], output_dir: str):
        """Save individual document results to file."""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            output_file = output_path / f"{result['doc_id']}_relations.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving document results: {str(e)}")

# Example usage
async def main():
    """Example of how to use the streaming relation extractor."""
    # Create sample document stream
    def document_stream():
        documents = [
            {
                'id': 'doc1',
                'text': 'Apple Inc. is headquartered in Cupertino, California. '
                        'The company was founded by Steve Jobs and Steve Wozniak.'
            },
            {
                'id': 'doc2',
                'text': 'Tesla, led by Elon Musk, manufactures electric vehicles in Fremont. '
                        'The company has expanded its operations globally.'
            }
        ]
        for doc in documents:
            yield doc

    # Initialize streaming extractor
    extractor = StreamingRelationExtractor(
        model_name='Babelscape/mrebel-large-32',
        device=0,
        max_length=1024,
        batch_size=8,
        queue_size=1000
    )

    # Process stream with output directory
    output_dir = "streaming_results"
    async for result in extractor.process_stream(document_stream(), output_dir):
        print(f"\nProcessed document {result['doc_id']}:")
        print(f"Language: {result['language']}")
        print(f"Number of triplets: {len(result['triplets'])}")
        
        # Print first few triplets as example
        for i, triplet in enumerate(result['triplets'][:3]):
            print(f"\nTriplet {i + 1}:")
            print(f"Head: {triplet['head']} ({triplet['head_type']})")
            print(f"Relation: {triplet['type']}")
            print(f"Tail: {triplet['tail']} ({triplet['tail_type']})")

if __name__ == "__main__":
    asyncio.run(main())

