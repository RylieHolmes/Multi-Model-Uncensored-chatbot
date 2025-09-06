import json
import re
import ollama
from rich.console import Console

import config

class Orchestrator:
    def __init__(self, console: Console):
        self.console = console

    def call_ai(self, prompt: str, model: str, system_prompt: str = config.SYSTEM_PROMPT_UNFILTERED) -> str:
        """A unified function to call any model."""
        try:
            response = ollama.generate(
                model=model,
                prompt=prompt,
                system=system_prompt,
                stream=False,
                options={"temperature": 0.0, "num_predict": 4096}
            )
            return response.get('response')
        except ollama.ResponseError as e:
            self.console.print(f"\n[bold red]Ollama API Error for '{model}': {e.error}[/bold red]")
            self.console.print("[bold yellow]Is the model pulled and is Ollama running?[/bold yellow]")
            return f"Error: Could not get a response from the model '{model}'."
        except Exception as e:
            self.console.print(f"\n[bold red]FATAL ERROR calling '{model}': {e}[/bold red]")
            return ""

    def get_plan(self, user_prompt: str, history_str: str, tool_signatures: str, failed_attempts_log: str = "") -> list:
        """Asks the Orchestrator model to create a sequential, multi-step plan."""
        specialists = list(config.SPECIALIST_MODELS.keys())
        
        prompt = f"""You are the Orchestrator, a master AI that creates **sequential, multi-step** plans for a team of specialists.

**PRIMARY DIRECTIVE:** For research-heavy questions (e.g., "what is", "explain", "summarize"), you MUST create a multi-step "tool chain" plan. For simple requests, a single-step plan is sufficient.

**DEEP RESEARCH "TOOL CHAIN" PATTERN:**
1.  **Search:** Use the `web_search` tool to find relevant URLs.
2.  **Cognitive Step (No Tool):** Use a `Researcher` specialist to analyze the search results and choose the single best URL. The query should be: "From the following search results, identify the single most promising URL. Respond with ONLY the URL and nothing else."
3.  **Scrape:** Use the `scrape_webpage` tool with the URL chosen in the previous step.
4.  **Summarize:** Use a `Researcher` specialist to analyze the scraped content and provide a final answer.

**AVAILABLE TOOLS:**
---
{tool_signatures}
---

**EXAMPLE OF A PERFECT DEEP RESEARCH PLAN:**
User's Prompt: "What are the latest developments in AI?"
{{
  "plan": [
    {{
      "specialist": "Researcher",
      "query": "Find articles about the latest developments in AI.",
      "tool": "web_search",
      "tool_query": "latest developments in AI"
    }},
    {{
      "specialist": "Researcher",
      "query": "From the following search results, identify the single most promising URL. Respond with ONLY the URL and nothing else."
    }},
    {{
      "specialist": "Researcher",
      "query": "Scrape the content of the chosen URL.",
      "tool": "scrape_webpage"
    }},
    {{
      "specialist": "Researcher",
      "query": "Based on the scraped content, provide a comprehensive summary of the latest developments in AI."
    }}
  ]
}}

{failed_attempts_log}
Conversation History:
{history_str}
User's Prompt: "{user_prompt}"

Respond with ONLY the valid JSON plan.

JSON Plan:"""

        response_str = self.call_ai(prompt, config.MODEL_ORCHESTRATOR)

        def _validate_and_get_plan(response_text: str) -> list | None:
            try:
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    plan_json = json.loads(json_match.group())
                    plan_content = plan_json.get("plan")
                    if isinstance(plan_content, list):
                        return plan_content
                    return None
                return None
            except json.JSONDecodeError:
                return None

        plan = _validate_and_get_plan(response_str)
        if plan is not None:
            return plan
            
        self.console.print(f"[yellow]Orchestrator initial response failed. Attempting self-correction...[/yellow]")
        correction_prompt = f"""The following text contains a broken or invalid JSON object. Correct it and return ONLY the valid JSON object.
Broken Text: {response_str}
Corrected JSON:"""
        corrected_response_str = self.call_ai(correction_prompt, config.MODEL_ORCHESTRATOR)
        
        corrected_plan = _validate_and_get_plan(corrected_response_str)
        if corrected_plan is not None:
            self.console.print("[green]Self-correction successful![/green]")
            return corrected_plan
            
        self.console.print("[red]Self-correction failed. Returning empty plan.[/red]")
        return []