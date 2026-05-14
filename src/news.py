import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def get_match_context(home: str, away: str) -> str:
    """
    Busca noticias recientes sobre el partido:
    lesionados, suspendidos, estado de forma, declaraciones.
    """
    query = f"{home} vs {away} injuries suspensions team news 2025"
    response = client.search(
        query=query,
        search_depth="basic",
        max_results=3
    )
    results = response["results"]
    lines = []
    for r in results:
        lines.append(f"[{r['title']}]\n{r['content']}\n")
    return "\n---\n".join(lines)

if __name__ == "__main__":
    context = get_match_context("Arsenal FC", "Manchester City FC")
    print(context)