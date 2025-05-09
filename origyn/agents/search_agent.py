"""Web search agent for the Origyn application."""

import logging
import requests
from ..models import PartInfoState
from ..config import GOOGLE_API_KEY, GOOGLE_CX

logger = logging.getLogger(__name__)

def web_search_agent_node(state: PartInfoState) -> PartInfoState:
    """
    Perform web search to find information about the part.
    
    Args:
        state: The current workflow state.
        
    Returns:
        Updated workflow state with search results.
    """
    if state.get("error"):
        logger.warning(f"Skipping search due to previous error: {state['error']}")
        return state
        
    part_query = state.get("translated_query")
    if not part_query:
        error_msg = "No translated query available for search."
        logger.error(error_msg)
        return {**state, "error": error_msg}

    try:
        query = f"{part_query} manufacturer"
        logger.info(f"Searching for: {query}")
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CX,
            "q": query,
            "num": 5
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        search_data = response.json()
        
        formatted_results = f"Search results for part query: {part_query}\n\n"
        if "items" in search_data and search_data["items"]:
            for i, item in enumerate(search_data["items"], 1):
                formatted_results += f"Result {i}:\n"
                formatted_results += f"Title: {item.get('title', 'N/A')}\n"
                formatted_results += f"URL: {item.get('link', 'N/A')}\n"
                formatted_results += f"Snippet: {item.get('snippet', 'N/A')}\n\n"
            
            logger.info(f"Found {len(search_data['items'])} search results")
        else:
            formatted_results += "No search results found."
            logger.warning("No search results found")
            
        return {**state, "search_results": formatted_results, "error": None}
    except Exception as e:
        error_msg = f"Search error: {str(e)}"
        logger.error(error_msg)
        return {**state, "search_results": f"Error performing search: {str(e)}", "error": error_msg}