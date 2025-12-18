from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from backend.graphrag.neo4j_client import Neo4jClient

class GraphQueryInput(BaseModel):
    """Input for graph query tool"""
    cypher_query: str = Field(description="Cypher query to execute")

class GraphQueryTool(BaseTool):
    name: str = "graph_query"
    description: str = """
    Execute Cypher queries against the Neo4j knowledge graph.
    Use this to find specific relationships, patterns, or aggregate data.
    
    Example queries:
    - Find movies by actor: MATCH (p:Person {name: 'Keanu Reeves'})-[:ACTED_IN]->(m:Movie) RETURN m.title
    - Find similar movies: MATCH (m1:Movie {title: 'The Matrix'})-[:SIMILAR_TO]->(m2:Movie) RETURN m2.title, m2.rating
    """
    args_schema: Type[BaseModel] = GraphQueryInput
    neo4j_client: Neo4jClient = Field(exclude=True)
    
    def _run(self, cypher_query: str) -> str:
        """Execute the Cypher query"""
        try:
            results = self.neo4j_client.execute_cypher(cypher_query)
            return f"Query results: {results}"
        except Exception as e:
            return f"Error executing query: {str(e)}"
