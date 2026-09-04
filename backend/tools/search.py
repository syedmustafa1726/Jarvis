from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_web(query: str) -> str:
    """Search the web and return results"""
    try:
        print(f"🌐 Searching: {query}")
        response = client.search(
            query=query,
            max_results=3,
            search_depth="basic"
        )
        
        results = []
        for r in response["results"]:
            results.append(f"- {r['title']}: {r['content'][:200]}")
        
        return "\n".join(results)
    
    except Exception as e:
        return f"Search failed: {str(e)}"