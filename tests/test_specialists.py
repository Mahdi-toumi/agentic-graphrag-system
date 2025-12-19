from backend.agents.specialist_agents import RecommendationAgent, AnalysisAgent, OrchestratorAgent

def test_specialists():
    print("🧪 Testing Specialist Agents...\n")
    
    # Test RecommendationAgent
    rec_agent = RecommendationAgent()
    prefs = {"genre": "Sci-Fi", "vibe": "mind-bending"}
    recommendations = rec_agent.recommend(prefs)
    print(f"✅ RecommendationAgent: {recommendations}")
    
    # Test AnalysisAgent
    analysis_agent = AnalysisAgent()
    query = "Why is Inception so popular?"
    analysis = analysis_agent.analyze(query)
    print(f"✅ AnalysisAgent: {analysis}")
    
    # Test OrchestratorAgent
    orch_agent = OrchestratorAgent()
    result = orch_agent.coordinate("Find me a complex sci-fi movie")
    print(f"✅ OrchestratorAgent: {result}")

if __name__ == "__main__":
    test_specialists()
