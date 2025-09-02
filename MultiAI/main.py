import sys
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from concurrent.futures import ThreadPoolExecutor
from spellchecker import SpellChecker
import re

import config
from memory.core_memory import CoreMemory
from tool_loader import load_tools_from_directory
from model_selector import select_model_for_specialist
from orchestrator import Orchestrator
from synthesizer import Synthesizer

class ConversationalAgent:
    """A conversational agent that uses multiple LLMs to generate a synthesized response."""

    def __init__(self, console: Console, memory: CoreMemory, tools: dict, orchestrator: Orchestrator, synthesizer: Synthesizer, is_gui_mode: bool = False):
        self.console = console
        self.memory = memory
        self.tools = tools
        self.orchestrator = orchestrator
        self.synthesizer = synthesizer
        self.is_gui_mode = is_gui_mode
        self.spell = SpellChecker()
        self.conversation_history = []
        self.full_response = ""

    def _execute_task(self, specialist: str, query: str, tool: str = None, tool_query: any = None, context: str = "") -> str:
        model = select_model_for_specialist(specialist, query)
        if not model: return f"Error: Unknown specialist '{specialist}'."
        if context: query = f"{query}\n\n**Previous Step's Results (for context):**\n{context}"
        self.console.print(f"> Consulting [bold magenta]{specialist}[/bold magenta] for: '[italic]{query.splitlines()[0]}[/italic]'")
        
        if tool:
            if tool in self.tools:
                self.console.print(f"> Using tool [bold yellow]{tool}[/bold yellow] with query: '[italic]{tool_query or context}[/italic]'")
                try:
                    tool_info, tool_function = self.tools[tool], self.tools[tool]['func']
                    if tool == 'execute_python_script' and self.is_gui_mode:
                        if isinstance(tool_query, dict): tool_query['confirm_execution'] = False
                        else: tool_query = {'filename': tool_query, 'confirm_execution': False}
                    if isinstance(tool_query, dict): return tool_function(**tool_query)
                    elif tool_query is None and context: return tool_function(context)
                    else: return tool_function(tool_query)
                except Exception as e: return f"Error executing tool {tool}: {e}"
            else: return f"Error: Unknown tool '{tool}' specified."
        
        prompt = f"You are the {specialist}. Your task is to address the following query: '{query}'."
        if specialist == "Coder":
            prompt = f"""You are an expert programmer. Your ONLY job is to write a complete, runnable Python script. Respond with ONLY the Python code in a markdown block. User's Request: '{query}'"""

        response = self.orchestrator.call_ai(prompt, model)
        return response.strip().strip('`').strip()

    def run(self, user_prompt: str):
        self.full_response = ""
        words = user_prompt.split()
        misspelled = self.spell.unknown(words)
        corrected_prompt = " ".join(self.spell.correction(word) if word in misspelled and self.spell.correction(word) is not None else word for word in words)
        
        if corrected_prompt.lower() != user_prompt.lower():
            yield {"correction": corrected_prompt}
            prompt_for_ai = corrected_prompt
        else:
            prompt_for_ai = user_prompt

        history_str = "\n".join(f"{item['role']}: {item['content']}" for item in self.conversation_history[-config.MAX_TURNS:])
        tool_signatures = "\n".join(f"- {name}{info['signature']}: {info['docstring']}" for name, info in self.tools.items())
        failed_attempts_log, specialist_reports = "", ""
        
        for loop_count in range(config.MAX_CRITIC_LOOPS):
            plan = []
            if loop_count > 0:
                yield {"status": f"Attempt {loop_count} failed. Falling back to a smarter plan..."}
                plan = [
                    {"specialist": "Researcher", "query": f"Find information on: {prompt_for_ai}", "tool": "web_search", "tool_query": prompt_for_ai},
                    {"specialist": "Researcher", "query": "Based on the search results, provide a comprehensive answer to the user's original query."}
                ]
            else:
                yield {"status": "Thinking..."}
                plan = self.orchestrator.get_plan(prompt_for_ai, history_str, tool_signatures, failed_attempts_log)

            if not isinstance(plan, list): plan = []
            yield {"plan": plan}
            
            is_greeting = any(word in prompt_for_ai.lower() for word in ["hello", "hi", "hey"])
            if not plan and not is_greeting and loop_count == 0:
                plan = [{"specialist": "Researcher", "query": f"Find information on: {prompt_for_ai}", "tool": "web_search", "tool_query": prompt_for_ai}]

            step_context, all_reports = "", []
            if plan:
                for i, task in enumerate(plan):
                    if isinstance(task, dict) and task.get("specialist") and task.get("query"):
                        specialist = task.get("specialist")
                        yield {"status": f"Step {i+1}/{len(plan)}: Consulting {specialist}..."}
                        step_result = self._execute_task(context=step_context, **task)
                        step_context = step_result
                        all_reports.append(f"--- Report from Step {i+1} ({specialist}) ---\n{step_result}")
                    else: self.console.print(f"[bold yellow]Warning: Skipping invalid task in plan: {task}[/bold yellow]")
            
            specialist_reports = "\n\n".join(all_reports)

            yield {"status": "Critiquing response..."}
            critic_prompt = f"""You are the Critic. Your job is to determine if the final report successfully and completely fulfilled the user's original request. The report MUST be helpful and directly address the query. A list of search results is NOT a complete answer.
**User's Original Request:** "{prompt_for_ai}"
**Final Report:** {specialist_reports if specialist_reports else "No reports were generated."}
Does the final report adequately fulfill the user's request? Your answer MUST be a single word: "Yes" or "No".
"""
            critic_response = self.orchestrator.call_ai(critic_prompt, config.MODEL_RESEARCHER)

            if "yes" in critic_response.lower():
                self.console.print("[green]Critic approved. Proceeding to synthesis.[/green]")
                break
            else:
                self.console.print(f"[yellow]Critic rejected. Attempt {loop_count + 1}/{config.MAX_CRITIC_LOOPS}. Re-planning...[/yellow]")
                failed_attempts_log += f"--- ATTEMPT {loop_count + 1} FAILED ---\nPLAN: {plan}\nREPORTS: {specialist_reports}\n\n"
                yield {"status": f"Attempt {loop_count + 1} failed. Re-planning..."}
                if loop_count == config.MAX_CRITIC_LOOPS - 1:
                    specialist_reports = "\n\n--- AGENT FAILED ---\nAfter multiple attempts, I could not generate a satisfactory response."

        yield {"status": "Generating response..."}
        journal_content = self.memory.read_core_memory()
        response_generator = self.synthesizer.synthesize_response(prompt_for_ai, history_str, specialist_reports, journal_content)
        
        for chunk in response_generator:
            self.full_response += chunk
            yield chunk

        self.conversation_history.append({"role": "user", "content": user_prompt})
        self.conversation_history.append({"role": "assistant", "content": self.full_response})
        self.memory.save_conversation(self.conversation_history)
        yield {"status": "Done"}


def main(run_gui: bool):
    console = Console()
    console.print(Panel("[bold green]Conversational Gemini Local v10.1[/bold green]", border_style="green"))
    core_memory = CoreMemory()
    core_memory.initialize_if_needed()
    tools = load_tools_from_directory()
    orchestrator = Orchestrator(console)
    synthesizer = Synthesizer(console)
    agent = ConversationalAgent(console, core_memory, tools, orchestrator, synthesizer, is_gui_mode=run_gui)
    if run_gui:
        try:
            from gui_main import MultiAIGUI
            import customtkinter as ctk
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")
            app = MultiAIGUI(agent)
            app.mainloop()
        except ImportError:
            console.print("[bold red]GUI dependencies not installed. Please run 'pip install customtkinter'[/bold red]")
            sys.exit(1)
    else:
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the MultiAI Chatbot.")
    parser.add_argument("--gui", action="store_true", help="Run the GUI version of the chatbot.")
    args = parser.parse_args()

    main(args.gui)
