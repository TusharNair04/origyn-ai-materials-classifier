"""OEM workflow implementation for the Origyn application."""

import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from ..models import PartInfoState, OEMResult, OEMOutput
from ..agents.translation_agent import translating_agent_node
from ..agents.search_agent import web_search_agent_node
from ..agents.llm_agent import synthesize_oem_info_node, parse_llm_output_node
from ..agents.vector_search_agent import vector_search_agent_node

logger = logging.getLogger(__name__)

class OEMWorkflow:
    """Workflow for OEM identification."""
    
    def __init__(self):
        """Initialize the OEM workflow."""
        logger.info("Initializing OEM workflow")
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
    
    def _build_workflow(self) -> StateGraph:
        """
        Build the workflow graph.
        
        Returns:
            StateGraph: The compiled workflow.
        """
        workflow = StateGraph(PartInfoState)
        
        # Add nodes
        logger.debug("Adding nodes to workflow")
        workflow.add_node("translate", translating_agent_node)
        workflow.add_node("search", web_search_agent_node)
        workflow.add_node("synthesize", synthesize_oem_info_node)
        workflow.add_node("parse_output", parse_llm_output_node)
        workflow.add_node("vector_search", vector_search_agent_node)
        
        # Set entry point
        workflow.set_entry_point("translate")
        
        # Add edges
        logger.debug("Adding edges to workflow")
        workflow.add_edge("translate", "search")
        workflow.add_edge("search", "synthesize")
        workflow.add_edge("synthesize", "parse_output")
        workflow.add_edge("parse_output", "vector_search")
        workflow.add_edge("vector_search", END)
        
        return workflow
    
    def run(self, part_query: str) -> OEMResult:
        """
        Run the OEM workflow.
        
        Args:
            part_query: The part query to process.
            
        Returns:
            OEMResult: The result of the workflow.
        """
        logger.info(f"Running OEM workflow for query: {part_query}")
        
        inputs = {"original_query": part_query}
        final_state = self.app.invoke(inputs)
        
        # Check for errors
        if final_state.get("error"):
            logger.warning(f"Workflow completed with error: {final_state['error']}")
        else:
            logger.info("Workflow completed successfully")
        
        # Create result object
        result = OEMResult.from_state(final_state)
        logger.info(f"OEM result: {result}")
        
        return result

def create_oem_workflow() -> OEMWorkflow:
    """
    Create and return an OEM workflow instance.
    
    Returns:
        OEMWorkflow: An initialized workflow instance.
    """
    return OEMWorkflow()