"""LLM agent for synthesizing OEM information."""

import logging
import json
from typing import List, Dict, Any
import groq
from langchain_core.output_parsers import PydanticOutputParser
from ..models import PartInfoState, OEMOutput, get_formatted_json_schema
from ..config import LLM_API_KEY, LLM_MODEL, SYNTHESIZER_INSTRUCTIONS_TEMPLATE

logger = logging.getLogger(__name__)

class LLMAgent:
    """Agent for handling LLM-based operations."""
    
    def __init__(self):
        """Initialize the LLM agent."""
        self.client = groq.Groq(api_key=LLM_API_KEY)
        self.parser = PydanticOutputParser(pydantic_object=OEMOutput)
        self.json_schema = get_formatted_json_schema()
        self.instructions = SYNTHESIZER_INSTRUCTIONS_TEMPLATE.format(schema=self.json_schema)
    
    def create_messages(self, content: str) -> List[Dict[str, str]]:
        """
        Create messages for the LLM.
        
        Args:
            content: The content to include in the user message.
            
        Returns:
            List of message dictionaries.
        """
        return [
            {"role": "system", "content": self.instructions},
            {"role": "user", "content": content}
        ]
    
    def generate_completion(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate a completion from the LLM.
        
        Args:
            messages: The messages to send to the LLM.
            
        Returns:
            The LLM's response.
        """
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=LLM_MODEL,
            temperature=0.00001,
            response_format={"type": "json_object"}
        )
        return chat_completion.choices[0].message.content
    
    def parse_response(self, response: str) -> OEMOutput:
        """
        Parse the LLM response into the OEMOutput model.
        
        Args:
            response: The LLM's response string.
            
        Returns:
            Parsed OEMOutput object.
        """
        return self.parser.parse(response)

def synthesize_oem_info_node(state: PartInfoState) -> PartInfoState:
    """
    Use LLM to synthesize OEM information from search results.
    
    Args:
        state: The current workflow state.
        
    Returns:
        Updated workflow state with LLM response.
    """
    if state.get("error"):
        logger.warning(f"Skipping synthesis due to previous error: {state['error']}")
        return state

    search_results_content = state.get("search_results")
    if not search_results_content or "Error performing search" in search_results_content or "No search results found" in search_results_content:
        logger.warning("No valid search results for synthesis")
        na_output = OEMOutput(oem="NA", part_category="NA")
        return {**state, "llm_response_json": na_output.model_dump_json(), "parsed_oem_info": na_output, "error": "No valid search results for synthesis."}

    try:
        logger.info("Synthesizing OEM information from search results")
        llm_agent = LLMAgent()
        messages = llm_agent.create_messages(search_results_content)
        llm_response = llm_agent.generate_completion(messages)
        
        logger.info(f"Received LLM response: {llm_response}")
        return {**state, "llm_response_json": llm_response, "error": None}
    except Exception as e:
        error_msg = f"LLM synthesis error: {str(e)}"
        logger.error(error_msg)
        return {**state, "error": error_msg}

def parse_llm_output_node(state: PartInfoState) -> PartInfoState:
    """
    Parse the LLM output into a structured format.
    
    Args:
        state: The current workflow state.
        
    Returns:
        Updated workflow state with parsed OEM info.
    """
    if state.get("error") and state.get("llm_response_json") is None:
        logger.warning(f"Skipping parsing due to previous error: {state['error']}")
        return state

    llm_json_response = state.get("llm_response_json")
    if not llm_json_response:
        error_msg = "No LLM response to parse."
        logger.error(error_msg)
        return {**state, "error": error_msg} 

    parser = PydanticOutputParser(pydantic_object=OEMOutput)
    try:
        logger.info("Parsing LLM response")
        parsed_data = parser.parse(llm_json_response)
        logger.info(f"Parsed OEM info: {parsed_data}")
        return {**state, "parsed_oem_info": parsed_data, "error": state.get("error")}
    except Exception as e:
        error_msg = f"Parsing error: {str(e)}. Original LLM response: {llm_json_response}"
        logger.error(error_msg)
        return {**state, "error": error_msg}