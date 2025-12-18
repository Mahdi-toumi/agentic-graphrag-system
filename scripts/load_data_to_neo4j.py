from neo4j import GraphDatabase
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='backend/.env')

class Neo4jLoader:
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "MahdiToumi")
        
        print(f"Connecting to Neo4j at {uri}...")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def create_constraints(self):
        """Create unique constraints and indexes"""
        with self.driver.session() as session:
            print("Creating constraints...")
            # Unique Constraints
            session.run("CREATE CONSTRAINT movie_id IF NOT EXISTS FOR (m:Movie) REQUIRE m.id IS UNIQUE")
            session.run("CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE")
            session.run("CREATE CONSTRAINT genre_id IF NOT EXISTS FOR (g:Genre) REQUIRE g.id IS UNIQUE")
            session.run("CREATE CONSTRAINT studio_id IF NOT EXISTS FOR (s:Studio) REQUIRE s.id IS UNIQUE")
            session.run("CREATE CONSTRAINT keyword_id IF NOT EXISTS FOR (k:Keyword) REQUIRE k.id IS UNIQUE")
            
            # Vector index (for 384 dimensions)
            print("Creating vector index...")
            session.run("""
                CREATE VECTOR INDEX movie_embeddings IF NOT EXISTS
                FOR (m:Movie) ON (m.embedding)
                OPTIONS {indexConfig: {
                    `vector.dimensions`: 384,
                    `vector.similarity_function`: 'cosine'
                }}
            """)
            
            # Full-text index
            print("Creating full-text index...")
            session.run("""
                CREATE FULLTEXT INDEX movie_text IF NOT EXISTS
                FOR (m:Movie) ON EACH [m.title, m.overview]
            """)
    
    def load_movies(self, data_path):
        """Load enriched movie data"""
        if not os.path.exists(data_path):
            print(f"Error: {data_path} not found.")
            return

        with open(data_path, 'r') as f:
            movies = json.load(f)
        
        print(f"Loading {len(movies)} movies into Neo4j...")
        with self.driver.session() as session:
            for movie in movies:
                # 1. Create/Update Movie node
                session.run("""
                    MERGE (m:Movie {id: $id})
                    SET m.title = $title,
                        m.year = $year,
                        m.rating = $rating,
                        m.budget = $budget,
                        m.revenue = $revenue,
                        m.overview = $overview,
                        m.embedding = $embedding
                """, movie)
                
                # 2. Genres
                for genre_name in movie.get('genres', []):
                    session.run("""
                        MERGE (g:Genre {name: $name})
                        ON CREATE SET g.id = apoc.create.uuid()
                        WITH g
                        MATCH (m:Movie {id: $movie_id})
                        MERGE (m)-[:HAS_GENRE {relevance: 1.0}]->(g)
                    """, name=genre_name, movie_id=movie['id'])
                
                # 3. Keywords (Enhanced to use Keyword nodes)
                for keyword in movie.get('keywords', []):
                    session.run("""
                        MERGE (k:Keyword {term: $term})
                        ON CREATE SET k.id = apoc.create.uuid()
                        WITH k
                        MATCH (m:Movie {id: $movie_id})
                        MERGE (m)-[:HAS_KEYWORD]->(k)
                    """, term=keyword, movie_id=movie['id'])

                # 4. Director (Enhanced to handle object)
                director = movie.get('director')
                if director:
                    session.run("""
                        MERGE (p:Person {id: $id})
                        SET p.name = $name, p.birth_year = $birth_year
                        WITH p
                        MATCH (m:Movie {id: $movie_id})
                        MERGE (p)-[:DIRECTED {year: $movie_year}]->(m)
                    """, id=director['id'], name=director['name'], 
                         birth_year=director.get('birth_year'), 
                         movie_id=movie['id'], movie_year=movie['year'])
                
                # 5. Actors (Enhanced to handle objects/roles)
                for actor in movie.get('actors', []):
                    session.run("""
                        MERGE (p:Person {id: $id})
                        SET p.name = $name
                        WITH p
                        MATCH (m:Movie {id: $movie_id})
                        MERGE (p)-[:ACTED_IN {role: $role, order: $order}]->(m)
                    """, id=actor['id'], name=actor['name'], 
                         role=actor.get('role'), order=actor.get('order'),
                         movie_id=movie['id'])

                # 6. Studio (Enhanced)
                studio = movie.get('studio')
                if studio:
                    session.run("""
                        MERGE (s:Studio {id: $id})
                        SET s.name = $name, s.country = $country, s.founded_year = $founded_year
                        WITH s
                        MATCH (m:Movie {id: $movie_id})
                        MERGE (m)-[:PRODUCED_BY {year: $movie_year}]->(s)
                    """, id=studio['id'], name=studio['name'], 
                         country=studio.get('country'), 
                         founded_year=studio.get('founded_year'),
                         movie_id=movie['id'], movie_year=movie['year'])
        
        print(f"Successfully loaded {len(movies)} movies.")
    
    def create_similarity_edges(self, threshold=0.8):
        """Create SIMILAR_TO relationships based on embeddings"""
        print(f"Creating similarity edges (threshold > {threshold})...")
        with self.driver.session() as session:
            # We use vector search to find neighbors for each movie
            session.run("""
                MATCH (m1:Movie)
                WHERE m1.embedding IS NOT NULL
                WITH m1
                CALL db.index.vector.queryNodes('movie_embeddings', 10, m1.embedding)
                YIELD node as m2, score
                WHERE m1 <> m2 AND score > $threshold
                MERGE (m1)-[r:SIMILAR_TO]->(m2)
                SET r.similarity_score = score, r.method = 'embedding'
            """, threshold=threshold)
        print("Similarity edges created.")

if __name__ == "__main__":
    loader = Neo4jLoader()
    try:
        loader.create_constraints()
        loader.load_movies('data/processed/movies_with_embeddings.json')
        loader.create_similarity_edges()
        print("Data loading completed successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        loader.close()
