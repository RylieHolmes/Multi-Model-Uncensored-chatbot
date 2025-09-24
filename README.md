<div align="center">

# 🧠 Multi-Model AI Chatbot 🤖

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Ollama-232323?style=for-the-badge&logo=ollama&logoColor=white" alt="Ollama">
  <img src="https://img.shields.io/badge/CustomTkinter-3A7ABF?style=for-the-badge" alt="CustomTkinter">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License: MIT">
</p>

An advanced, locally-run agentic framework that uses a team of specialized AI models to deliver robust, tool-enabled responses, all with a focus on privacy and system safety.

</div>

<details>
  <summary><strong>Table of Contents</strong></summary>
  <ol>
    <li><a href="#-about-the-project">About The Project</a></li>
    <li><a href="#-key-features">Key Features</a></li>
    <li><a href="#-system-architecture">System Architecture</a></li>
    <li><a href="#-tech-stack">Tech Stack</a></li>
    <li><a href="#-getting-started">Getting Started</a></li>
    <li><a href="#-resource-management-recommended">Resource Management (Recommended)</a></li>
    <li><a href="#-how-to-run">How to Run</a></li>
    <li><a href="#-configuration">Configuration</a></li>
    <li><a href="#-license">License</a></li>
  </ol>
</details>

---

## 📖 About The Project

This project is an experimental, locally-run chatbot built on an advanced "mixture-of-experts" architecture. Instead of relying on a single AI, it employs a team of specialized Large Language Models (LLMs) that collaborate to fulfill user requests. An **Orchestrator** AI designs a plan, **Specialist** agents execute the steps using a suite of tools, and a final **Synthesizer** AI crafts the definitive response.

The entire system runs 100% locally on your machine using **Ollama**, ensuring complete privacy and offline capability. It also includes robust resource management scripts to prevent system instability, making it a safe and powerful tool for development.

---

## ✨ Key Features

*   **Multi-Agent Architecture**: Utilizes a sophisticated team of AI agents (Orchestrator, Critic, Specialists, Synthesizer) for more robust and accurate problem-solving.
*   **Tool-Enabled Agents**: The AI can use tools like `web_search`, `scrape_webpage`, and `execute_python_script` to perform complex tasks.
*   **100% Local and Private**: All models and processing run on your own hardware via Ollama. No data ever leaves your machine.
*   **Resource Safety Management**: Includes scripts to limit Ollama's CPU and VRAM usage, ensuring your computer remains stable.
*   **Configurable Safety**: A `SAFE_MODE` toggle allows switching between a standard helpful prompt and a more direct, unfiltered system prompt.
*   **Dual Interface**: Run the chatbot with a polished graphical user interface (GUI) or directly in your command-line interface (CLI).
*   **Long-Term Memory**: A simple journaling feature allows the AI to remember key facts and user preferences between conversations.

---

## 🏗️ System Architecture

The project follows a logical agentic flow to process user requests:

User Prompt
      |
      ▼
[Orchestrator] -> Creates a step-by-step plan.
      |
      ▼
[Critic] -> Reviews the plan. If flawed, requests a new one.
      |
      ▼
[Specialist Agents (Coder, Researcher)] -> Execute each step of the plan.
      |         |
      |         ▼
      |      [Tools: web_search, execute_python_script, etc.] -> Gathers info or performs actions.
      |
      ▼
[Synthesizer] -> Synthesizes all reports into a final, conversational response.
      |
      ▼
Final Response

---

## 🛠️ Tech Stack

*   **Core**: Python
*   **LLM Service**: Ollama
*   **GUI**: CustomTkinter
*   **CLI Display**: Rich
*   **Web Scraping**: BeautifulSoup4, Requests
*   **Web Search**: DuckDuckGo Search
*   **Resource Management**: psutil, WMI (via PowerShell)

---

## 🚀 Getting Started

Follow these steps to get the project running on your local machine.

#### 1. Prerequisites
*   **Ollama:** You must have the [Ollama](https://ollama.com/) application installed and running.
*   **Python:** Python 3.8 or newer is recommended.

#### 2. Get the Code
Clone this repository to your local machine:
```bash
git clone https://github.com/RylieHolmes/Multi-Model-AI-Chatbot.git
cd Multi-Model-AI-Chatbot
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

---

## 🚨 Resource Management (Recommended)

To prevent the application from consuming all your system resources, running the provided management script is highly recommended.

#### For Windows Users
This script applies CPU affinity/priority limits and sets a VRAM limit for the `ollama.exe` process.

1.  **Ensure Ollama is running.**
2.  Run the script from your terminal (it will automatically request Admin privileges):
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

---

## 🧭 How to Run

You can launch the chatbot in either GUI or command-line mode.

*   **To run the GUI version:**
    ```bash
    python MultiAI/main.py --gui
    ```

*   **To run the CLI version (Coming Soon):**
    ```bash
    python MultiAI/main.py
    ```

---

## ⚙️ Configuration

Key settings can be adjusted in the `MultiAI/config.py` file:
*   `SAFE_MODE`: Toggle between `True` for a standard, helpful AI persona or `False` for an unfiltered, direct persona.
*   `MODEL_...`: Change the default models used for each specialist agent.

---

## 📄 License

This project is licensed under the MIT License.
