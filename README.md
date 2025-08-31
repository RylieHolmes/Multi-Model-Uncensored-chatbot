# Multi-Model AI Chatbot

This is an experimental chatbot I built to play with local Large Language Models (LLMs) and agentic frameworks.

Instead of relying on a single AI model, this project uses a "team" of specialized models that work together. An "Orchestrator" model creates a plan, different "Specialist" models (like a Coder or a Researcher) execute the steps, and a "Synthesizer" model delivers the final, conversational answer.

### Core Features:

*   **Mixture-of-Experts Design:** Uses a team of different local LLMs, each with a specific role.
*   **Runs 100% Locally:** The entire system runs on your machine using **Ollama**. No API keys needed.
*   **Tool-Enabled:** The AI can use tools like `web_search`, `scrape_webpage`, and `execute_python_script`.
*   **Uncensored:** The system prompts are designed to be unfiltered and direct, providing answers without moralizing or refusing requests.
*   **GUI and CLI:** You can run the chatbot with a graphical user interface or in your command line.
*   **Long-term Memory:** It has a simple journaling feature to remember key facts between conversations.

### Setup & How to Run:

This project requires a bit of setup because it runs everything locally.

**1. Install Ollama:**
You must have Ollama installed and running on your system.

**2. Download the Required AI Models:**
Open your terminal and pull the models defined in the `config.py` file. The default models are:
```bash
ollama pull dolphin-llama3:8b
ollama pull dolphin-mixtral
ollama pull codstral
ollama pull phi3:medium-128k
```


### Minimum System Requirements

**NVIDIA GeForce RTX 3070**
**32GB RAM**
