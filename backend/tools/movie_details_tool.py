from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from backend.graphrag.neo4j_client import Neo4jClient

class MovieDetailsInput(BaseModel):
    """Input for movie details tool"""
    movie_title: str = Field(description="Exact title of the movie to get details for")

class MovieDetailsTool(BaseTool):
    name: str = "get_movie_details"
    description: str = """
    Retrieve comprehensive information about a specific movie, including its cast, director, genres, studios, and keywords.
    Use this when you have a specific movie title and need more context.
    """
    args_schema: Type[BaseModel] = MovieDetailsInput
    neo4j_client: Neo4jClient = Field(exclude=True)
    
    def _run(self, movie_title: str) -> str:
        """Retrieve movie details"""
        try:
            cypher_query = """
                MATCH (m:Movie)
                WHERE m.title =~ $title_regex
                OPTIONAL MATCH (p:Person)-[r:ACTED_IN]->(m)
                WITH m, collect({name: p.name, role: r.role}) as actors
                OPTIONAL MATCH (d:Person)-[:DIRECTED]->(m)
                WITH m, actors, collect(d.name) as directors
                OPTIONAL MATCH (m)-[:HAS_GENRE]->(g:Genre)
                WITH m, actors, directors, collect(g.name) as genres
                OPTIONAL MATCH (m)-[:PRODUCED_BY]->(s:Studio)
                WITH m, actors, directors, genres, collect(s.name) as studios
                OPTIONAL MATCH (m)-[:HAS_KEYWORD]->(k:Keyword)
                RETURN m {.*, 
                    embedding: null,
                    actors: actors, 
                    directors: directors, 
                    genres: genres, 
                    studios: studios,
                    keywords: collect(k.term)
                } as details
            """
            # Case-insensitive partial match
            title_regex = f"(?i).*{movie_title}.*"
            results = self.neo4j_client.execute_cypher(cypher_query, {"title_regex": title_regex})
            
            if not results:
                return f"No movie found matching '{movie_title}'"
            
            return f"Movie details: {results[0]['details']}"
        except Exception as e:
            return f"Error retrieving movie details: {str(e)}"
