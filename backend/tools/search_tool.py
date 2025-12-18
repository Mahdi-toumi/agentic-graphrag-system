from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import httpx

class SearchInput(BaseModel):
    """Input for web search tool"""
    query: str = Field(description="Search query")

class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = """
    Search the web for current information not in the knowledge graph.
    Use this for real-time data, external facts, or information beyond the movie database.
    """
    args_schema: Type[BaseModel] = SearchInput
    
    def _run(self, query: str) -> str:
        """Perform web search"""
        # Using DuckDuckGo as a free option
        try:
            url = f"https://api.duckduckgo.com/?q={query}&format=json"
            response = httpx.get(url, timeout=10)
            data = response.json()
            
            abstract = data.get('AbstractText', 'No results found')
            return f"Search results: {abstract}"
        except Exception as e:
            return f"Search error: {str(e)}"
