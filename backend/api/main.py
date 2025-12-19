from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.models.schemas import (
    QueryRequest, QueryResponse, GraphStatsResponse, HealthResponse
)
from backend.agents.graph_agent import MovieAgentSystem
from backend.graphrag.neo4j_client import Neo4jClient
import time
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path='backend/.env')

# Initialize FastAPI
app = FastAPI(
    title="Agentic GraphRAG System",
    description="Multi-agent system with GraphRAG for movie recommendations",
    version="1.0.0"
)

# CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]
env_origins = os.getenv("CORS_ORIGINS")
if env_origins:
    origins.extend(env_origins.split(","))

print(f"📡 Allowing origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
agent_system = None
neo4j_client = None

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global agent_system, neo4j_client
    
    try:
        agent_system = MovieAgentSystem()
        neo4j_client = Neo4jClient()
        print("✅ Agent system initialized")
    except Exception as e:
        print(f"❌ Initialization error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if neo4j_client:
        neo4j_client.close()

@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    neo4j_ok = False
    llm_ok = False
    
    try:
        if neo4j_client:
            neo4j_client.execute_cypher("RETURN 1")
            neo4j_ok = True
    except:
        pass
    
    try:
        if agent_system:
            llm_ok = True
    except:
        pass
    
    return HealthResponse(
        status="healthy" if (neo4j_ok and llm_ok) else "degraded",
        neo4j_connected=neo4j_ok,
        llm_available=llm_ok
    )

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """Main query endpoint"""
    if not agent_system:
        raise HTTPException(status_code=503, detail="Agent system not initialized")
    
    try:
        start_time = time.time()
        
        # Run agent
        result = agent_system.run(request.query)
        
        execution_time = time.time() - start_time
        
        return QueryResponse(
            answer=result["answer"],
            tool_calls=result["tool_calls"],
            reasoning=result["reasoning"],
            context_used=result["context_used"],
            execution_time=round(execution_time, 2)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph-info", response_model=GraphStatsResponse)
async def get_graph_info():
    """Get knowledge graph statistics"""
    if not neo4j_client:
        raise HTTPException(status_code=503, detail="Neo4j not connected")
    
    try:
        stats = neo4j_client.get_graph_stats()
        
        return GraphStatsResponse(
            total_movies=stats['movies'],
            total_people=stats['people'],
            total_genres=stats['genres'],
            total_relationships=stats['relationships']
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/movies/{title}")
async def get_movie(title: str):
    """Get detailed movie information"""
    if not neo4j_client:
        raise HTTPException(status_code=503, detail="Neo4j not connected")
    
    try:
        context = neo4j_client.get_movie_context(title)
        
        if not context:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        return context
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
