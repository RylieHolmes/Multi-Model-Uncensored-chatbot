from datetime import datetime
import config

class CoreMemory:
    """Handles reading and appending to the core memory/journal file."""

    def __init__(self, filepath=config.CORE_MEMORY_FILE):
        self.filepath = filepath

    def read_core_memory(self):
        """Reads the entire content of the core memory file."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return "Core memory file not found. A new one will be created."
        except Exception as e:
            return f"Error reading core memory: {e}"

    def append_to_journal(self, text):
        """Appends a new entry to the journal with a timestamp."""
        try:
            with open(self.filepath, 'a', encoding='utf-8') as f:
                f.write(f"\nJOURNAL ({datetime.now().isoformat()}): {text}")
            return "Successfully appended to journal."
        except Exception as e:
            return f"Error appending to journal: {e}"

    def initialize_if_needed(self):
        """Creates the core memory file if it doesn't exist."""
        try:
            with open(self.filepath, 'x', encoding='utf-8') as f:
                f.write("--- Journal of Gemini Local ---")
        except FileExistsError:
            pass # File already exists, no action needed.
        except Exception as e:
            print(f"Error initializing core memory: {e}")

    def save_conversation(self, history, filename=config.CONV_HISTORY_FILE):
        """Saves the conversation history to a separate file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for turn in history:
                    f.write(f"{turn['role']}: {turn['content']}\n")
            return "Conversation history saved."
        except Exception as e:
            return f"Error saving conversation: {e}"