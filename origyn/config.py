"""Configuration management for the Origyn application."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LLM Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
LLM_API_KEY = os.getenv("LLM_API_KEY")

# Google Search Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CX")

# Google Cloud Translation
GOOGLE_SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH")

# Vector Database
VECTORDB_PATH = os.getenv("VECTORDB_PATH")

# JSON Schema Template
SYNTHESIZER_INSTRUCTIONS_TEMPLATE = """
You are an AI assistant specialized in identifying the Original Equipment Manufacturer (OEM) for spare parts. Your primary objective is to determine the company that originally manufactured a specific part based on the web search results provided to you by the Web Search Agent.

Follow these steps systematically:

    1. Analyze Input: Carefully read the web search results to extract key information. This may include part numbers, model numbers, product types, or other relevant details in any language.
    2. Analyze Search Results: Review the titles, snippets, and URLs returned by the Web Search Agent.
    3. Synthesize Findings and Determine OEM: Based primarily on the analysis of the search results, identify the most likely OEM, ensuring you distinguish the original manufacturer from distributors, resellers, or different brands owned by the same parent company.
    4. Do not return any preamble or explanations and the output language should be english and in lowercase, regardless of the language of the input.
    
As an example, for the schema {{"properties": {{"foo": {{"title": "Foo", "description": "a list of strings", "type": "array", "items": {{"type": "string"}}}}}}, "required": ["foo"]}}
the object {{"foo": ["bar", "baz"]}} is a well-formatted instance of the schema. The object {{"properties": {{"foo": ["bar", "baz"]}}}} is not well-formatted.

Here is the output schema:

{schema}
    5. Provide the Answer in the above JSON format. Do not return any preamble or explanations, return only a pure JSON string
"""

def get_service_account_path() -> str:
    """Get the full path to the service account credentials file."""
    service_account_path = GOOGLE_SERVICE_ACCOUNT_PATH
    if not service_account_path:
        raise ValueError(
            "GOOGLE_SERVICE_ACCOUNT_PATH is not set in the environment variables."
        )
    
    return service_account_path

def get_vectordb_path() -> str:
    """Get the full path to the vector database."""
    vectordb_path = VECTORDB_PATH
    if not vectordb_path:
        raise ValueError("VECTORDB_PATH is not set in the environment variables.")
    
    return vectordb_path

def validate_config() -> bool:
    """Validate that all required configuration values are set."""
    required_vars = [
        ("LLM_API_KEY", LLM_API_KEY),
        ("GOOGLE_API_KEY", GOOGLE_API_KEY),
        ("GOOGLE_CX", GOOGLE_CX),
        ("GOOGLE_SERVICE_ACCOUNT_PATH", GOOGLE_SERVICE_ACCOUNT_PATH),
        ("VECTORDB_PATH", VECTORDB_PATH),
    ]
    
    missing_vars = [name for name, value in required_vars if not value]
    
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
    
    return True