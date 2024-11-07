import os
from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
def read_requirements(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file if line.strip() and not line.startswith('#')]

requirements = read_requirements('requirements.txt')

# Package metadata
setup(
    name="rebel-stream",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Real-time streaming implementation of REBEL relation extraction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/rebel-stream",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/rebel-stream/issues",
        "Documentation": "https://github.com/yourusername/rebel-stream/docs",
        "Source Code": "https://github.com/yourusername/rebel-stream",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "rebel_stream": [
            "py.typed",
            "data/*",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
        "Typing :: Typed",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-asyncio>=0.21.0',
            'pytest-cov>=4.1.0',
            'black>=23.3.0',
            'isort>=5.12.0',
            'flake8>=6.0.0',
            'mypy>=1.3.0',
        ],
        'docs': [
            'mkdocs>=1.4.3',
            'mkdocs-material>=9.1.15',
        ],
        'gpu': [
            'torch>=2.0.0+cu118',  # CUDA 11.8
        ],
    },
    entry_points={
        "console_scripts": [
            "rebel-stream=rebel_stream.file_watcher:main",
        ],
    },
    # Testing
    test_suite="tests",
    tests_require=[
        'pytest>=7.4.0',
        'pytest-asyncio>=0.21.0',
        'pytest-cov>=4.1.0',
    ],
    # Make the package pip installable
    zip_safe=False,
    # Include type hints
    package_data={"rebel_stream": ["py.typed"]},
)

# Additional setup configurations
if __name__ == "__main__":
    # Print Python version info
    import sys
    print(f"Setting up rebel-stream using Python {sys.version}")

    # Check for CUDA availability
    try:
        import torch
        if torch.cuda.is_available():
            print(f"CUDA is available: {torch.cuda.get_device_name(0)}")
        else:
            print("CUDA is not available, using CPU only")
    except ImportError:
        print("PyTorch not found, will be installed as dependency")

    # Setup type hints file
    type_hints_file = os.path.join("src", "rebel_stream", "py.typed")
    os.makedirs(os.path.dirname(type_hints_file), exist_ok=True)
    open(type_hints_file, "w").close()