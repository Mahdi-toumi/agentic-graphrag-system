# System Architecture

## Overview
The Agentic GraphRAG System is a high-performance movie intelligence platform that bridges the gap between unstructured LLM reasoning and structured Knowledge Graph retrieval. It uses an asynchronous, multi-agent approach to decompose complex cinematic queries and answer them with high precision using both semantic (vector) and structural (Cypher) context.

## Components

### 1. Agent System (LangGraph)
- **State management**: Uses `AgentState` to track messages, gathered context, tool results, and the reasoning loop.
- **Workflow orchestration**: A directed acyclic graph (DAG) implemented in LangGraph that routes queries through analysis, retrieval, and synthesis phases.
- **Tool integration**: Agents have access to a suite of tools including `GraphQueryTool`, `VectorSearchTool`, and `MovieDetailsTool`.

### 2. Knowledge Graph (Neo4j)
- **Schema design**: A rich domain model featuring `Movie`, `Person`, `Genre`, and `Studio` nodes.
- **Vector indexes**: Integrated Neo4j vector search for finding movies based on plot semantic similarity.
- **Relationship modeling**: Explicit relationships like `DIRECTED`, `ACTED_IN`, and `SIMILAR_TO` with properties like `roles` and `relevance`.

### 3. GraphRAG Pipeline
- **Hybrid retrieval**: Combines vector-based plot similarity with graph-based neighbor traversals.
- **Context construction**: Aggregates disparate data points (ratings, cast lists, plot fragments) into a unified prompt context.
- **Query expansion**: The analysis agent expands simple user queries into precise search parameters.

### 4. API Layer (FastAPI)
- **Endpoints**: Multi-functional REST API providing endpoints for chat (`/ask`), statistics (`/graph-info`), and raw metadata (`/movies/{title}`).
- **Request/response models**: Strict Pydantic schemas ensure data integrity between the agent and the frontend.
- **Error handling**: Centralized exception management for LLM timeouts or database connectivity issues.

### 5. Frontend (React)
- **Chat interface**: A premium "Deep Space" UI featuring glassmorphism, framer-motion animations, and `react-markdown` support.
- **Visualization**: Interactive stat dashboard with glowing high-contrast indicators.
- **State management**: Clean React state hooks for managing message history and loading transitions.

## Data Flow
1. **User Query**: Received via the React Frontend.
2. **FastAPI Route**: Forwards the query to the `MovieAgentSystem`.
3. **Agent Workflow**:
    - **Analysis**: LLM chooses search strategy.
    - **Retrieval**: Neo4j executes Cypher or Vector searches.
    - **Synthesis**: LLM reformulates data into a concise Markdown response.
4. **Response**: Returned via API and rendered with rich formatting in the Chat UI.

## Design Decisions
- **Groq/Llama-3.3**: Chosen for extremely fast inference speeds without sacrificing reasoning quality.
- **PostCSS/Tailwind v4**: Implementation of a modern CSS-in-JS style pipeline for performance.
- **Virtual Environment (venv)**: Strict dependency isolation to prevent Pydantic v1/v2 compatibility issues.
