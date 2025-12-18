from sentence_transformers import SentenceTransformer
from typing import List, Dict
from backend.graphrag.neo4j_client import Neo4jClient

class HybridRetriever:
    def __init__(self):
        self.neo4j = Neo4jClient()
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    def retrieve(self, query: str, top_k: int = 5) -> Dict:
        """Hybrid retrieval: vector + full-text + graph traversal"""
        
        # 1. Vector search
        query_embedding = self.embedder.encode(query).tolist()
        vector_results = self.neo4j.vector_search(query_embedding, top_k)
        
        # 2. Full-text search
        fulltext_results = self.neo4j.fulltext_search(query, top_k)
        
        # 3. Merge and deduplicate
        combined_results = self._merge_results(vector_results, fulltext_results)
        
        # 4. Expand context with graph traversal
        enriched_results = []
        for result in combined_results[:3]:  # Top 3
            context = self.neo4j.get_movie_context(result['title'])
            enriched_results.append(context)
        
        return {
            'vector_results': vector_results,
            'fulltext_results': fulltext_results,
            'enriched_context': enriched_results
        }
    
    def _merge_results(self, vector_results: List, text_results: List) -> List:
        """Merge and rank results from different sources"""
        seen = set()
        merged = []
        
        # Interleave results, prioritizing vector search
        for v, t in zip(vector_results, text_results):
            if v['title'] not in seen:
                merged.append(v)
                seen.add(v['title'])
            if t['title'] not in seen:
                merged.append(t)
                seen.add(t['title'])
        
        # Add remaining items if lists were different lengths
        if len(vector_results) > len(text_results):
            for v in vector_results[len(text_results):]:
                if v['title'] not in seen:
                    merged.append(v)
                    seen.add(v['title'])
        elif len(text_results) > len(vector_results):
            for t in text_results[len(vector_results):]:
                if t['title'] not in seen:
                    merged.append(t)
                    seen.add(t['title'])
        
        return merged
