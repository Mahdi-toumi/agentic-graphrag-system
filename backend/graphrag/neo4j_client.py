import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='backend/.env')

class Neo4jClient:
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "MahdiToumi")
        
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def execute_cypher(self, query, parameters=None):
        """Execute a Cypher query and return results as a list of dictionaries"""
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

    def verify_connection(self):
        """Verify the connection to Neo4j"""
        try:
            self.driver.verify_connectivity()
            return True
        except Exception as e:
            print(f"Neo4j connection error: {e}")
            return False
