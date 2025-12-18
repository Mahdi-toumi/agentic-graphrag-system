from typing import TypedDict, List, Optional, Annotated
from operator import add

class AgentState(TypedDict):
    """State for the agent workflow"""
    
    # Input
    query: str
    
    # Processing
    messages: Annotated[List[dict], add]
    tool_calls: Annotated[List[dict], add]
    
    # Graph retrieval
    graph_context: Optional[str]
    vector_results: Optional[List[dict]]
    cypher_results: Optional[List[dict]]
    
    # Tool results
    search_results: Optional[str]
    calculation_results: Optional[str]
    
    # Output
    final_answer: Optional[str]
    
    # Metadata
    iteration: int
    reasoning: List[str]
