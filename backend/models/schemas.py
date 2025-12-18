from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class QueryRequest(BaseModel):
    """Request model for /ask endpoint"""
    query: str = Field(..., description="User query")
    top_k: int = Field(5, description="Number of results to retrieve")

class QueryResponse(BaseModel):
    """Response model for /ask endpoint"""
    answer: str
    tool_calls: List[Dict[str, Any]]
    reasoning: List[str]
    context_used: int
    execution_time: float

class GraphStatsResponse(BaseModel):
    """Response model for /graph-info endpoint"""
    total_movies: int
    total_people: int
    total_genres: int
    total_relationships: int

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    neo4j_connected: bool
    llm_available: bool
