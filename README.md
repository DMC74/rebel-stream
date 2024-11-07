# Rebel Stream

A real-time streaming implementation of the REBEL (Relation Extraction By End-to-end Language generation) model that processes documents as they arrive and extracts structured relations.

## Features

- Real-time document processing
- Streaming architecture for efficient processing
- Support for multiple languages
- Automatic language detection
- Batch processing for optimal performance
- Asynchronous file watching and processing
- Structured output in JSON format
- Automatic file archiving

## Requirements

- Python 3.10+
- Anaconda or Miniconda
- 8GB RAM minimum (16GB recommended)
- CPU or NVIDIA GPU (optional)

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/rebel-stream.git
cd rebel-stream
```

2. Set up the environment:
```bash
chmod +x scripts/setup_environment.sh
./scripts/setup_environment.sh
```

3. Start the processor:
```bash
chmod +x scripts/start_processor.sh
./scripts/start_processor.sh
```

4. Add documents to process:
```bash
cp your_document.txt data/input_documents/
```

The processed results will appear in `data/processed_documents/` and the original files will be moved to `data/archived_documents/`.

## Directory Structure

- `data/input_documents/`: Place documents here for processing
- `data/processed_documents/`: Contains extracted relations in JSON format
- `data/archived_documents/`: Contains processed input files
- `src/`: Source code
- `scripts/`: Utility scripts
- `docs/`: Documentation
- `tests/`: Test files

## Output Format

The extracted relations are saved in JSON format:
```json
{
    "doc_id": "example",
    "language": "en_XX",
    "triplets": [
        {
            "head": "Company",
            "head_type": "ORGANIZATION",
            "type": "headquarters_location",
            "tail": "City",
            "tail_type": "LOCATION"
        }
    ]
}
```

## Configuration

You can configure the processor by modifying the following environment variables:
- `REBEL_BATCH_SIZE`: Number of segments to process at once (default: 8)
- `REBEL_MAX_LENGTH`: Maximum sequence length (default: 1024)
- `REBEL_DEVICE`: GPU device ID or -1 for CPU (default: -1)

## Documentation

Detailed documentation is available in the `docs/` directory:
- [Installation Guide](docs/installation.md)
- [Usage Guide](docs/usage.md)
- [API Reference](docs/api.md)

## Testing

Run the test suite:
```bash
pytest tests/
```

## License

MIT License - see LICENSE file for details.

## Citation

If you use this software in your research, please cite:

```bibtex
@article{huguet2021rebel,
    title={REBEL: Relation Extraction By End-to-end Language generation},
    author={Huguet Cabot, Pere-Lluís and Navigli, Roberto},
    journal={arXiv preprint arXiv:2104.07650},
    year={2021}
}
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
