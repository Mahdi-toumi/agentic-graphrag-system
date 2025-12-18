import os
import sys
from dotenv import load_dotenv

# Add the project root to sys.path to allow imports from 'backend'
sys.path.append(os.getcwd())

# Load environment variables
load_dotenv(dotenv_path='backend/.env')

from backend.agents.graph_agent import MovieAgentSystem

def test_agent():
    print("Initializing Movie Agent System...")
    agent_system = MovieAgentSystem()
    
    test_queries = [
        "What are some sci-fi movies similar to The Matrix?",
        "Who directed Inception and what is its rating?",
        "Can you recommend a movie with intense action set in a dream world?",
        "Compare the ratings of Matrix and Inception."
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"USER QUERY: {query}")
        print(f"{'='*50}")
        
        try:
            result = agent_system.run(query)
            
            print(f"\nAGENT ANSWER:\n{result['answer']}")
            
            if result['tool_calls']:
                print("\nTOOLS USED:")
                for call in result['tool_calls']:
                    print(f"- {call['tool']}: Input='{call['input']}'")
            else:
                print("\nNO EXTERNAL TOOLS USED.")
                
            print(f"\nREASONING STEPS:")
            for step in result['reasoning']:
                print(f"- {step[:100]}...")
                
        except Exception as e:
            print(f"Error testing query '{query}': {e}")

if __name__ == "__main__":
    test_agent()
