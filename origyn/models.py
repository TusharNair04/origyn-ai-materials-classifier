"""Data models for the Origyn application."""

from typing import TypedDict, Optional, Dict, Any, List
from pydantic import BaseModel, Field
import json

class OEMOutput(BaseModel):
    """Output model for OEM information."""
    
    oem: str = Field(
        title="oem",
        description="The name of the Original Equipment Manufacturer (OEM) else NA"
    )
    part_category: str = Field(
        title="part_category",
        description="The category of the part, such as bearings, lubricants etc."
    )

class PartInfoState(TypedDict):
    """State model for the OEM workflow."""
    
    original_query: str
    translated_query: Optional[str]
    search_results: Optional[str]
    llm_response_json: Optional[str]
    parsed_oem_info: Optional[OEMOutput]
    unspsc_family: Optional[str]
    unspsc_code: Optional[str]
    error: Optional[str]

class OEMResult(BaseModel):
    """Final result model returned to users."""
    
    original_query: str
    oem: str
    part_category: str
    unspsc_code: str
    unspsc_family: str
    
    @classmethod
    def from_state(cls, state: PartInfoState) -> "OEMResult":
        """Create an OEMResult from a PartInfoState."""
        oem_info = state.get("parsed_oem_info")
        
        return cls(
            original_query=state["original_query"],
            oem=oem_info.oem if oem_info else "NA",
            part_category=oem_info.part_category if oem_info else "NA",
            unspsc_code=state.get("unspsc_code", "NA"),
            unspsc_family=state.get("unspsc_family", "NA"),
        )

def get_oem_json_schema() -> Dict[str, Any]:
    """Get the JSON schema for OEMOutput."""
    schema_dict = {k: v for k, v in OEMOutput.model_json_schema().items()}
    return {
        "properties": schema_dict["properties"],
        "required": schema_dict["required"]
    }

def get_formatted_json_schema() -> str:
    """Get the formatted JSON schema for OEMOutput."""
    return json.dumps(get_oem_json_schema(), indent=2)