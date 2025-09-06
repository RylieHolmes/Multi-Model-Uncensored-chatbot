# Multi-Model AI Chatbot: An Advanced, Locally-Run Agentic Framework

This project is an experimental, locally-run chatbot built on an advanced "mixture-of-experts" architecture. Instead of relying on a single, monolithic AI, it employs a team of specialized Large Language Models (LLMs) that collaborate to fulfill user requests.

An **Orchestrator** AI designs a plan, **Specialist** agents (like a Coder or a Researcher) execute the steps using a suite of tools, and a final **Synthesizer** AI crafts the definitive, conversational response.

The entire system runs 100% locally on your machine using **Ollama**, ensuring complete privacy and offline capability. It also includes robust resource management scripts to prevent system instability, making it a safe and powerful tool for development and experimentation.

### Core Features

*   **Multi-Agent Architecture** Utilizes a sophisticated team of AI agents (Orchestrator, Critic, Specialists, Synthesizer) for more robust and accurate problem-solving.
*   **Tool-Enabled Agents:** The AI can use tools like `web_search`, `scrape_webpage`, and `execute_python_script` to interact with external information and perform complex tasks.
*   **100% Local and Private:** All models and processing run on your own hardware via Ollama. No data ever leaves your machine. No API keys are needed.
*   **Resource Safety Management:** Includes scripts to limit Ollama's CPU and VRAM usage, ensuring your computer remains stable and responsive even under heavy load.
*   **Configurable Safety:** Features a `SAFE_MODE` toggle in the configuration, allowing you to switch between a standard helpful prompt and a more direct, unfiltered system prompt.
*   **Dual Interface:** Run the chatbot with a polished graphical user interface (GUI) or directly in your command-line interface (CLI).
*   **Long-Term Memory:** A simple journaling feature allows the AI to remember key facts and user preferences between conversations.

### System Architecture

The project follows a logical flow to process user requests, inspired by modern agentic design patterns.

```
User Prompt
      |
      v
[Orchestrator] -> Creates a step-by-step plan.
      |
      v
[Critic] -> Reviews the plan. If flawed, requests a new one.
      |
      v
[Specialist Agents (Coder, Researcher)] -> Execute each step of the plan.
      |         |
      |         v
      |      [Tools: web_search, execute_python_script, etc.] -> Gathers information or performs actions.
      |
      v
[Synthesizer] -> Synthesizes all reports and data into a final, conversational response.
      |
      v
Final Response
```

### Setup and Installation

Follow these steps to get the project running on your local machine.

#### 1. Prerequisites
*   **Ollama:** You must have the [Ollama](https://ollama.com/) application installed and running.
*   **Python:** Python 3.8 or newer is recommended.

#### 2. Get the Code
Clone this repository to your local machine:
```bash
git clone <your-repository-url>
cd Multi-Model-Uncensored-chatbot-main
```

#### 3. Install Dependencies
Install all the required Python packages using the `requirements.txt` file.
```bash
pip install -r requirements.txt
```

#### 4. Download the AI Models
Open your terminal and pull the default models required by the configuration.
```bash
ollama pull dolphin-llama3:8b
ollama pull dolphin-mixtral
ollama pull codestral
ollama pull phi3:medium-128k
```

### Important: Resource Management (Recommended)

To ensure the application does not consume all of your system resources, it is highly recommended to run the provided resource management script.

#### For Windows Users
This script will apply CPU affinity and priority limits to the running `ollama.exe` process and set a VRAM limit.

1.  **Ensure Ollama is running.**
2.  Run the script from your terminal (it will automatically request Administrator privileges):
    ```cmd
    python manage_ollama_limits_windows.py
    ```
3.  **Restart the Ollama application** for the VRAM limit to take effect.

#### For Linux Users
This script creates a `systemd` override file to apply resource limits to the Ollama service.

1.  Run the script with `sudo`:
    ```bash
    sudo python manage_ollama_limits.py
    ```
2.  Apply the new configuration by running the commands shown by the script:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl restart ollama
    ```

### How to Run the Chatbot

You can launch the chatbot in either GUI or command-line mode.

*   **To run the GUI version:**
    ```bash
    python MultiAI/main.py --gui
    ```

*   **To run the CLI version (Coming Soon):**
    ```bash
    python MultiAI/main.py
    ```

### Configuration

Key settings can be adjusted in the `MultiAI/config.py` file:
*   `SAFE_MODE`: Toggle between `True` for a standard, helpful AI persona or `False` for the unfiltered, direct persona.
*   `MODEL_...`: Change the default models used for each specialist agent.

### Technology Stack

*   **Core:** Python
*   **LLM Service:** Ollama
*   **GUI:** CustomTkinter
*   **CLI Display:** Rich
*   **Web Scraping:** BeautifulSoup4, Requests
*   **Web Search:** DuckDuckGo Search
*   **Resource Management:** psutil, WMI (via PowerShell)

### License

This project is licensed under the MIT License.
