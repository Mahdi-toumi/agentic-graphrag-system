from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, List
from sentence_transformers import SentenceTransformer
from backend.graphrag.neo4j_client import Neo4jClient

class VectorSearchInput(BaseModel):
    """Input for vector search tool"""
    query: str = Field(description="Natural language query to find similar movies")
    top_k: int = Field(default=5, description="Number of results to return")

class VectorSearchTool(BaseTool):
    name: str = "vector_search_movies"
    description: str = """
    Perform a semantic search for movies based on a natural language query.
    Use this when the user is looking for movies with specific themes, plots, or "vibe".
    """
    args_schema: Type[BaseModel] = VectorSearchInput
    neo4j_client: Neo4jClient = Field(exclude=True)
    model: SentenceTransformer = Field(exclude=True)
    
    def _run(self, query: str, top_k: int = 5) -> str:
        """Execute the vector search"""
        try:
            # Generate embedding for the query
            query_embedding = self.model.encode(query).tolist()
            
            # Execute vector search pass in Cypher
            cypher_query = """
                CALL db.index.vector.queryNodes('movie_embeddings', $top_k, $query_embedding)
                YIELD node, score
                RETURN node.title as title, node.overview as overview, score
            """
            results = self.neo4j_client.execute_cypher(cypher_query, {
                "top_k": top_k,
                "query_embedding": query_embedding
            })
            
            return f"Semantic search results: {results}"
        except Exception as e:
            return f"Error performing vector search: {str(e)}"
