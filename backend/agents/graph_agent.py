from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from backend.agents.state import AgentState
from backend.tools.graph_query_tool import GraphQueryTool
from backend.tools.search_tool import WebSearchTool
from backend.tools.calculator_tool import CalculatorTool
from backend.graphrag.hybrid_search import HybridRetriever
from backend.graphrag.neo4j_client import Neo4jClient
from typing import Dict
import os

class MovieAgentSystem:
    def __init__(self):
        # Initialize LLM
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
            temperature=0.7
        )
        
        # Initialize components
        self.neo4j = Neo4jClient()
        self.retriever = HybridRetriever()
        
        # Initialize tools
        self.tools = [
            GraphQueryTool(neo4j_client=self.neo4j),
            WebSearchTool(),
            CalculatorTool()
        ]
        
        # Build workflow
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_query", self.analyze_query)
        workflow.add_node("retrieve_context", self.retrieve_context)
        workflow.add_node("reason_with_tools", self.reason_with_tools)
        workflow.add_node("generate_answer", self.generate_answer)
        
        # Define edges
        workflow.set_entry_point("analyze_query")
        workflow.add_edge("analyze_query", "retrieve_context")
        workflow.add_conditional_edges(
            "retrieve_context",
            self.should_use_tools,
            {
                "use_tools": "reason_with_tools",
                "skip_tools": "generate_answer"
            }
        )
        workflow.add_edge("reason_with_tools", "generate_answer")
        workflow.add_edge("generate_answer", END)
        
        return workflow
    
    def analyze_query(self, state: AgentState) -> AgentState:
        """Analyze user query and plan approach"""
        prompt = ChatPromptTemplate.from_template("""
        Analyze this query and determine:
        1. Is it asking about movies in our database?
        2. Does it require graph traversal?
        3. Does it need external information?
        4. Does it require calculations?
        
        Query: {query}
        
        Provide a brief analysis and reasoning.
        """)
        
        response = self.llm.invoke(prompt.format(query=state["query"]))
        
        state["reasoning"].append(f"Analysis: {response.content}")
        state["iteration"] = 0
        
        return state
    
    def retrieve_context(self, state: AgentState) -> AgentState:
        """Retrieve relevant context from knowledge graph"""
        results = self.retriever.retrieve(state["query"], top_k=5)
        
        # Format context
        context_parts = []
        for item in results['enriched_context']:
            context_parts.append(f"""
            Movie: {item.get('title')}
            Overview: {item.get('overview')}
            Rating: {item.get('rating')}
            Genres: {', '.join(item.get('genres', []))}
            Director: {', '.join(item.get('directors', []))}
            Actors: {', '.join(item.get('actors', []))}
            Similar: {', '.join(item.get('similar_movies', []))}
            """)
        
        state["graph_context"] = "\n---\n".join(context_parts)
        state["vector_results"] = results['vector_results']
        
        return state
    
    def should_use_tools(self, state: AgentState) -> str:
        """Decide if tools are needed"""
        # Simple heuristic: check if query contains keywords
        query_lower = state["query"].lower()
        
        tool_keywords = [
            'calculate', 'compute', 'search web', 'current', 'latest',
            'how many', 'count', 'find all', 'list'
        ]
        
        needs_tools = any(keyword in query_lower for keyword in tool_keywords)
        
        return "use_tools" if needs_tools else "skip_tools"
    
    def reason_with_tools(self, state: AgentState) -> AgentState:
        """Use tools to gather additional information"""
        
        # Create tool-using prompt
        prompt = ChatPromptTemplate.from_template("""
        You are an AI assistant with access to these tools:
        {tools}
        
        Query: {query}
        Context from knowledge graph: {context}
        
        Decide which tool to use and provide the input.
        If no tool is needed, say "NO_TOOL_NEEDED".
        
        Format: TOOL_NAME: input
        """)
        
        tool_descriptions = "\n".join([
            f"- {tool.name}: {tool.description}" for tool in self.tools
        ])
        
        response = self.llm.invoke(prompt.format(
            tools=tool_descriptions,
            query=state["query"],
            context=state.get("graph_context", "")
        ))
        
        # Parse and execute tool
        tool_output = response.content.strip()
        
        if "NO_TOOL_NEEDED" not in tool_output:
            # Simple parsing (in production, use structured output)
            for tool in self.tools:
                if tool.name in tool_output.lower():
                    tool_input = tool_output.split(":", 1)[1].strip()
                    result = tool._run(tool_input)
                    state["tool_calls"].append({
                        'tool': tool.name,
                        'input': tool_input,
                        'output': result
                    })
        
        return state

    def generate_answer(self, state: AgentState) -> AgentState:
        """Generate final answer using all gathered context"""
        
        prompt = ChatPromptTemplate.from_template("""
        You are a helpful movie recommendation assistant.
        
        User Query: {query}
        
        Knowledge Graph Context:
        {graph_context}
        
        Tool Results:
        {tool_results}
        
        Reformulate the gathered information into a natural, high-quality answer.
        - Use **bold** for movie titles or ratings.
        - Provide a concise summary (under 2-3 sentences).
        - **ONLY** include a specific list (Director, Cast, etc.) if the user explicitly asked for those details or if the query is a formal request for movie specifications.
        - If creating a list, use bullet points (*) on NEW LINES.
        
        Example (General Query):
        The movie **Interstellar** is a sci-fi epic rated **8.6**, following a team of explorers through a wormhole to save humanity.
        
        Example (Specific Request):
        **Interstellar** details:
        * **Director**: Christopher Nolan
        * **Cast**: Matthew McConaughey, Anne Hathaway
        """)
        
        tool_results = "\n".join([
            f"{call['tool']}: {call['output']}" 
            for call in state.get("tool_calls", [])
        ]) or "No tools were used."
        
        response = self.llm.invoke(prompt.format(
            query=state["query"],
            graph_context=state.get("graph_context", "No context available"),
            tool_results=tool_results
        ))
        
        state["final_answer"] = response.content
        
        return state

    def run(self, query: str) -> Dict:
        """Run the agent workflow"""
        initial_state = {
            "query": query,
            "messages": [],
            "tool_calls": [],
            "graph_context": None,
            "vector_results": None,
            "cypher_results": None,
            "search_results": None,
            "calculation_results": None,
            "final_answer": None,
            "iteration": 0,
            "reasoning": []
        }
        
        result = self.app.invoke(initial_state)
        
        return {
            "answer": result["final_answer"],
            "tool_calls": result["tool_calls"],
            "reasoning": result["reasoning"],
            "context_used": len(result.get("vector_results", []))
        }
