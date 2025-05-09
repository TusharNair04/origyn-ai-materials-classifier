"""Vector search agent for UNSPSC classification."""

import logging
from sentence_transformers import SentenceTransformer
import chromadb
from ..models import PartInfoState
from ..config import get_vectordb_path

logger = logging.getLogger(__name__)

class VectorSearchAgent:
    """Agent for performing vector search operations."""
    
    def __init__(self, vectordb_path: str):
        """
        Initialize the vector search agent.
        
        Args:
            vectordb_path: Path to the vector database.
        """
        self.vectordb_path = vectordb_path
        self.client = chromadb.PersistentClient(path=vectordb_path)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def search(self, query: str, collection_name: str = "unspsc_vectorstore", n_results: int = 5):
        """
        Perform vector search.
        
        Args:
            query: The search query.
            collection_name: Name of the collection to search.
            n_results: Number of results to return.
            
        Returns:
            Search results.
        """
        collection = self.client.get_collection(name=collection_name)
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=['documents', 'metadatas', 'distances']
        )
        
        return results

def vector_search_agent_node(state: PartInfoState) -> PartInfoState:
    """
    Perform vector search for UNSPSC classification.
    
    Args:
        state: The current workflow state.
        
    Returns:
        Updated workflow state with UNSPSC classification.
    """
    if state.get("error") and not state.get("parsed_oem_info"):
        logger.warning(f"Skipping vector search due to previous error: {state['error']}")
        return state

    try:
        vectordb_path = get_vectordb_path()
        agent = VectorSearchAgent(vectordb_path)
        
        part_category = state.get("parsed_oem_info").part_category if state.get("parsed_oem_info") else "na"
        logger.info(f"Performing vector search for part category: {part_category}")
        
        if part_category == "na":
            logger.warning("No valid part category for vector search")
            return {**state, "unspsc_code": "na", "unspsc_family": "na", "error": state.get("error") or "No valid part category"}
        
        else:
            results = agent.search(part_category)
            
            if not results or not results['metadatas'] or not results['metadatas'][0]:
                logger.warning("No vector search results found")
                return {**state, "unspsc_code": "na", "unspsc_family": "na", "error": state.get("error")}
            
            family_code = results['metadatas'][0][0].get('family', 'na')
            family_title = results['metadatas'][0][0].get('family_title', 'na')
            
            logger.info(f"Found UNSPSC: {family_code} - {family_title}")
            
            return {**state, "unspsc_code": family_code, "unspsc_family": family_title, "error": state.get("error")}
    
    except Exception as e:
        error_msg = f"Vector search error: {str(e)}"
        logger.error(error_msg)
        return {**state, "error": state.get("error") or error_msg}