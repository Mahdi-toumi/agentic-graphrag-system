# 🎬 Agentic GraphRAG Movie Intelligence

An advanced, multi-agent movie assistant powered by **GraphRAG**, **Neo4j**, and **LangGraph**. This system combines the power of structured knowledge graphs with the reasoning capabilities of Large Language Models to provide cinematic-grade movie insights and recommendations.

![Premium UI Showcase](https://raw.githubusercontent.com/Mahdi-toumi/agentic-graphrag-system/main/docs/screenshots/hero_showcase.png)

## 🌌 Overview
This system is designed to provide a premium, cinematic experience for movie enthusiasts and data lovers alike. By leveraging a high-performance knowledge graph, we can perform complex traversals and vector-based semantic searches to answer queries that traditional search engines struggle with.

## 🏗️ Architecture
The system is built on a modular, agentic architecture:

- **Frontend**: A high-contrast, React-based "Deep Space" interface with glassmorphism and real-time graph visualization.
- **Backend API**: A high-performance FastAPI server managing the orchestration between the UI and the agent system.
- **Agent System**: A multi-agent workflow built with LangGraph, utilizing specialized agents for retrieval, analysis, and recommendations.
- **Data Layer**: Neo4j Knowledge Graph storing movies, actors, directors, genres, and studios with vector-embedded relationships.

For a deep dive, see [ARCHITECTURE.md](docs/ARCHITECTURE.md).

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.12+
- Node.js 18+
- Neo4j Instance (Local or AuraDB)
- Groq API Key (for LLM reasoning)

### 2. Environment Setup
Clone the repository and set up your environment variables:

```bash
cp .env.example .env
# Edit .env with your Neo4j and Groq credentials
```

### 3. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn api.main:app --reload
```

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🛠️ Usage
- **Chat**: Ask about plots, ratings, or complex connections (e.g., "What sci-fi movies directed by Nolan have a rating > 8.5?").
- **Dashboard**: Visualize graph statistics and high-level insights in the Data Hub.
- **CLI**: Use the powerful command-line interface for batch queries.
  ```bash
  python -m backend.cli --query "Tell me about The Matrix"
  ```

## 🧪 Testing
Run the comprehensive suite of test scenarios:
```bash
python -m pytest tests/test_scenarios.py
```

## 🤝 Contributing
Contributions are welcome! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
