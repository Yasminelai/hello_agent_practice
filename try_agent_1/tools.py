"""External tools available to tool-using agents."""

import os

from dotenv import load_dotenv
from serpapi import SerpApiClient


load_dotenv()


def search(query: str) -> str:
    """Search the web with SerpApi and return a concise observation."""
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return "Error: SERPAPI_API_KEY is not configured in .env."

    try:
        client = SerpApiClient(
            {
                "engine": "google",
                "q": query,
                "api_key": api_key,
                "gl": "cn",
                "hl": "en",
            }
        )
        results = client.get_dict()

        if "answer_box_list" in results:
            return "\n".join(str(item) for item in results["answer_box_list"])

        answer_box = results.get("answer_box", {})
        if answer_box.get("answer"):
            return answer_box["answer"]
        if answer_box.get("snippet"):
            return answer_box["snippet"]

        knowledge_graph = results.get("knowledge_graph", {})
        if knowledge_graph.get("description"):
            return knowledge_graph["description"]

        organic_results = results.get("organic_results", [])
        if organic_results:
            snippets = []
            for index, item in enumerate(organic_results[:3], start=1):
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                snippets.append(f"[{index}] {title}\n{snippet}".strip())
            return "\n\n".join(snippets)

        return f"No information was found for '{query}'."
    except Exception as exc:
        return f"Error while searching: {exc}"
