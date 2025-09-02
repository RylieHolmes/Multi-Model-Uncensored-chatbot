import config

def select_model_for_specialist(specialist: str, query: str) -> str:
    """Dynamically select the best model for a specialist/task based on the query."""
    query_lower = query.lower()
    if specialist == "Researcher":
        if any(x in query_lower for x in ["adult", "drug", "nsfw", "uncensored", "controversial"]):
            return "llama3-uncensored:latest"
        if "code" in query_lower or "python" in query_lower:
            return "deepseek-coder:6.7b-instruct"
        return config.MODEL_RESEARCHER
    elif specialist == "Coder":
        if "web" in query_lower:
            return "phi3:latest"
        return config.MODEL_CODER
    elif specialist == "Creative":
        return "phi3:latest"
    else:

        return config.MODEL_SYNTHESIZER
