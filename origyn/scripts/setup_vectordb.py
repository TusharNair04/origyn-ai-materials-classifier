#!/usr/bin/env python3
"""
Script to initialize and populate the UNSPSC vector database.

This script downloads UNSPSC codes or loads them from a CSV file,
generates embeddings, and stores them in a ChromaDB database.
"""

import argparse
import csv
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import chromadb
import pandas as pd
from sentence_transformers import SentenceTransformer

# Add parent directory to path to import module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from oem_finder.utils.logging_utils import setup_logging


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Initialize and populate the UNSPSC vector database."
    )
    
    parser.add_argument(
        "--unspsc-csv",
        "-u",
        help="Path to CSV file with UNSPSC codes",
        type=str,
        required=True,
    )
    
    parser.add_argument(
        "--output-dir",
        "-o",
        help="Output directory for the vector database",
        type=str,
        default="./vectordb",
    )
    
    parser.add_argument(
        "--log-level",
        help="Set the logging level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
    )
    
    parser.add_argument(
        "--embedding-model",
        "-e",
        help="Name of the sentence transformer model to use for embeddings",
        type=str,
        default="all-MiniLM-L6-v2",
    )
    
    return parser.parse_args()


def load_unspsc_codes(csv_path: str) -> List[Dict]:
    """
    Load UNSPSC codes from a CSV file.
    
    Args:
        csv_path: Path to the CSV file.
        
    Returns:
        List of dictionaries with UNSPSC code data.
    """
    logging.info(f"Loading UNSPSC codes from {csv_path}")
    
    try:
        df = pd.read_csv(csv_path)
        
        # Check required columns
        required_columns = ["family", "family_title", "description"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(
                f"CSV file is missing required columns: {', '.join(missing_columns)}"
            )
        
        # Convert to list of dictionaries
        unspsc_data = df.to_dict(orient="records")
        logging.info(f"Loaded {len(unspsc_data)} UNSPSC codes")
        
        return unspsc_data
    
    except Exception as e:
        logging.error(f"Error loading UNSPSC codes: {str(e)}")
        raise


def create_vectordb(
    unspsc_data: List[Dict],
    output_dir: str,
    embedding_model_name: str
) -> Tuple[chromadb.PersistentClient, chromadb.Collection]:
    """
    Create and populate the vector database.
    
    Args:
        unspsc_data: List of dictionaries with UNSPSC code data.
        output_dir: Output directory for the vector database.
        embedding_model_name: Name of the sentence transformer model.
        
    Returns:
        Tuple of (client, collection).
    """
    logging.info(f"Creating vector database in {output_dir}")
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(path=output_dir)
        
        # Create or get collection
        collection_name = "unspsc_vectorstore"
        
        # If collection exists, delete it and recreate
        try:
            client.delete_collection(collection_name)
            logging.info(f"Deleted existing collection: {collection_name}")
        except:
            pass
        
        collection = client.create_collection(name=collection_name)
        logging.info(f"Created collection: {collection_name}")
        
        # Load embedding model
        logging.info(f"Loading embedding model: {embedding_model_name}")
        embedding_model = SentenceTransformer(embedding_model_name)
        
        # Prepare data for embedding
        ids = []
        documents = []
        metadatas = []
        
        for i, item in enumerate(unspsc_data):
            ids.append(str(i))
            
            # Create document text from family title and description
            doc_text = (
                f"{item['family_title']} - {item.get('description', '')}"
            )
            documents.append(doc_text)
            
            # Create metadata
            metadata = {
                "family": item["family"],
                "family_title": item["family_title"],
                "description": item.get("description", "")
            }
            metadatas.append(metadata)
        
        # Generate embeddings in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch_ids = ids[i:i+batch_size]
            batch_docs = documents[i:i+batch_size]
            batch_meta = metadatas[i:i+batch_size]
            
            batch_embeddings = embedding_model.encode(batch_docs)
            
            # Add to collection
            collection.add(
                ids=batch_ids,
                documents=batch_docs,
                metadatas=batch_meta,
                embeddings=batch_embeddings.tolist()
            )
            
            logging.info(f"Added batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1} to collection")
        
        logging.info(f"Vector database creation complete: {len(documents)} items added")
        
        return client, collection
    
    except Exception as e:
        logging.error(f"Error creating vector database: {str(e)}")
        raise


def main():
    """Main function."""
    args = parse_args()
    
    # Set up logging
    log_level = getattr(logging, args.log_level)
    setup_logging(level=log_level)
    
    try:
        # Load UNSPSC codes
        unspsc_data = load_unspsc_codes(args.unspsc_csv)
        
        # Create vector database
        client, collection = create_vectordb(
            unspsc_data,
            args.output_dir,
            args.embedding_model
        )
        
        # Test query
        query_text = "bearings"
        logging.info(f"Testing query: '{query_text}'")
        
        embedding_model = SentenceTransformer(args.embedding_model)
        query_embedding = embedding_model.encode([query_text])[0].tolist()
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
            include=["documents", "metadatas", "distances"]
        )
        
        logging.info("Query results:")
        for i, (doc, meta, dist) in enumerate(zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        )):
            logging.info(f"Result {i+1}:")
            logging.info(f"  Family: {meta['family']} - {meta['family_title']}")
            logging.info(f"  Description: {meta['description']}")
            logging.info(f"  Distance: {dist}")
        
        logging.info(f"Vector database created successfully at {args.output_dir}")
        
        return 0
    
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())