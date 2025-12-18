from neo4j import GraphDatabase
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='backend/.env')

class Neo4jClient:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "MahdiToumi"))
        )
    
    def close(self):
        self.driver.close()
    
    def execute_cypher(self, query: str, params: Dict = None) -> List[Dict]:
        """Execute Cypher query and return results"""
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return [dict(record) for record in result]
    
    def vector_search(self, embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Perform vector similarity search"""
        query = """
        CALL db.index.vector.queryNodes('movie_embeddings', $top_k, $embedding)
        YIELD node, score
        RETURN node.title as title, node.overview as overview, 
               node.rating as rating, score
        ORDER BY score DESC
        """
        return self.execute_cypher(query, {
            'embedding': embedding,
            'top_k': top_k
        })
    
    def fulltext_search(self, text: str, top_k: int = 5) -> List[Dict]:
        """Perform full-text search"""
        query = """
        CALL db.index.fulltext.queryNodes('movie_text', $text)
        YIELD node, score
        RETURN node.title as title, node.overview as overview, 
               node.rating as rating, score
        ORDER BY score DESC
        LIMIT $top_k
        """
        return self.execute_cypher(query, {'text': text, 'top_k': top_k})
    
    def get_movie_context(self, movie_title: str) -> Dict:
        """Get comprehensive context for a movie"""
        query = """
        MATCH (m:Movie)
        WHERE m.title =~ $title_regex
        OPTIONAL MATCH (m)-[:HAS_GENRE]->(g:Genre)
        OPTIONAL MATCH (p:Person)-[:DIRECTED]->(m)
        OPTIONAL MATCH (a:Person)-[:ACTED_IN]->(m)
        OPTIONAL MATCH (m)-[:SIMILAR_TO]->(similar:Movie)
        RETURN m.title as title, m.overview as overview, m.rating as rating,
               collect(DISTINCT g.name) as genres,
               collect(DISTINCT p.name) as directors,
               collect(DISTINCT a.name)[0..5] as actors,
               collect(DISTINCT similar.title)[0..3] as similar_movies
        """
        # Using case-insensitive partial match for robustness
        title_regex = f"(?i).*{movie_title}.*"
        results = self.execute_cypher(query, {'title_regex': title_regex})
        return results[0] if results else {}
    
    def get_graph_stats(self) -> Dict:
        """Get graph statistics"""
        stats_query = """
        MATCH (m:Movie) WITH count(m) as movies
        MATCH (p:Person) WITH movies, count(p) as people
        MATCH (g:Genre) WITH movies, people, count(g) as genres
        MATCH ()-[r]->() WITH movies, people, genres, count(r) as relationships
        RETURN movies, people, genres, relationships
        """
        results = self.execute_cypher(stats_query)
        return results[0] if results else {}
