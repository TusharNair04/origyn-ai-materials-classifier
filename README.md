# Origyn AI Materials Classifier

A powerful AI Agent tool that identifies Original Equipment Manufacturers (OEMs) and provides UNSPSC categorization for spare parts from material procurement datasets.

## Overview

Origyn uses advanced Agentic AI workflows to analyze part descriptions and numbers, identifying the correct manufacturer and standardized product classification according to the United Nations Standard Products and Services Code (UNSPSC) taxonomy.

## Features

- **OEM Identification**: Determines the original equipment manufacturer of parts
- **Part Categorization**: Identifies the specific category of industrial parts
- **UNSPSC Classification**: Provides standardized UNSPSC codes and family descriptions
- **Multi-language Support**: Translates non-English queries for analysis
- **Vector Search**: Utilizes semantic search for finding similar parts
- **LLM Integration**: Leverages large language models for information synthesis

## Installation

```bash
# Clone the repository
git clone https://github.com/TusharNair04/origyn-ai-materials-classifier.git
cd origyn-ai-materials-classifier

# Install the package
pip install -e .
```

## Configuration

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Configure the following environment variables in the `.env` file:

```
LLM_API_KEY=your_groq_api_key
LLM_MODEL=llama3-70b-8192
GOOGLE_TRANSLATE_API_KEY=your_google_translate_api_key
```

## Setting Up the Vector Database

Before using Origyn, you need to set up the UNSPSC vector database using the `setup_vectordb.py` script:

```bash
# Run the setup script with the provided UNSPSC data file
python -m origyn.scripts.setup_vectordb --unspsc-csv data/unspsc_master.csv --output-dir unspsc_vectorstore

# Optional parameters:
# --embedding-model or -e : Specify a different sentence-transformer model (default: all-MiniLM-L6-v2)
# --log-level : Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
```

The script performs the following operations:

1. Loads UNSPSC codes from the specified CSV file
2. Generates embeddings for each code using the sentence-transformer model
3. Stores the embeddings in a ChromaDB vector database
4. Runs a test query to verify the database functionality

The CSV file should contain at minimum the following columns:

- **key**: unique identifier for each entry
- **segment**: segment code
- **segment_title**: segment name
- **family**: family code
- **family_title**: family name
- **class**: class code
- **class_title**: class name
- **commodity**: commodity code
- **commodity_title**: commodity name

## Usage

### Command Line Interface

```bash
# Basic usage with a part query
python -m origyn "SKF 6205 bearing"

# Output to JSON file
python -m origyn "SKF 6205 bearing" --output results.json

# Pretty-print JSON output
python -m origyn "SKF 6205 bearing" --json --pretty

# Set custom logging
python -m origyn "SKF 6205 bearing" --log-level DEBUG --log-file debug.log
```

### Python API

```python
from origyn.workflows import create_oem_workflow

# Create workflow instance
workflow = create_oem_workflow()

# Process a part query
result = workflow.run("SKF 6205 bearing")

# Access the results
print(f"OEM: {result.oem}")
print(f"Part Category: {result.part_category}")
print(f"UNSPSC Code: {result.unspsc_code}")
print(f"UNSPSC Family: {result.unspsc_family}")
```

## Architecture

Origyn uses a modular workflow architecture based on LangGraph:

1. **Translation Agent**: Translates non-English queries to English
2. **Search Agent**: Retrieves relevant information about the part
3. **LLM Agent**: Synthesizes the information to identify the OEM and part category
4. **Vector Search Agent**: Matches part information to UNSPSC codes using vector embeddings

## Requirements

- Python 3.8 or higher
- Dependencies (automatically installed):
  - langchain-core
  - groq
  - google-cloud-translate
  - langgraph
  - sentence-transformers
  - chromadb
  - pydantic
  - python-dotenv