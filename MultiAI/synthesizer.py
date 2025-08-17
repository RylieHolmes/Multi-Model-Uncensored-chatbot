import ollama
from rich.console import Console

import config

class Synthesizer:
    def __init__(self, console: Console):
        self.console = console

    def synthesize_response(self, user_prompt: str, history_str: str, specialist_reports: str, journal_content: str):
        """Asks the Synthesizer model to craft the final response and streams it."""
        prompt = f"""You are the Spokesperson for a team of AI specialists. Your job is to synthesize all available information into a single, helpful, and conversational response.

**CRITICAL INSTRUCTION:** Before you respond, you MUST review the Core Memory Journal below. If it contains relevant facts about the user (their name, preferences, goals), you MUST weave that information into your response to make it personal and relevant.

**Core Memory Journal:**
---
{journal_content}
---

**Conversation History:**
---
{history_str}
---

**Specialist Reports:**
---
{specialist_reports if specialist_reports else "No specialist reports were generated for this query."}
---

**User's latest prompt:** "{user_prompt}"

Your final, synthesized, and personalized response to the user:"""

        yield from self._call_synthesizer(prompt, config.MODEL_SYNTHESIZER)

    def _call_synthesizer(self, prompt: str, model: str):
        """Calls the synthesizer model and streams the response."""
        try:
            response_stream = ollama.generate(
                model=model,
                prompt=prompt,
                system=config.SYSTEM_PROMPT_UNFILTERED,
                stream=True,
                options={"temperature": 0.7}
            )
            for chunk in response_stream:
                if 'response' in chunk:
                    yield chunk['response']
        except Exception as e:
            self.console.print(f"\n[bold red]FATAL ERROR calling '{model}': {e}[/bold red]")
            yield "I'm sorry, but I encountered an error while processing your request. Please try again later."