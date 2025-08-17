import customtkinter as ctk
import threading
import json
import re
from queue import Queue
from tkinter import Menu
from spellchecker import SpellChecker
from rich.console import Console

class Theme:
    BACKGROUND = "#171717"
    INPUT_BOX = "#232323"
    TEXT = "#d4d4d4"
    SENDER_TEXT = "#ffffff"
    MUTED_TEXT = "#6a6a6a"
    ACCENT = "#525252"
    CODE_BG = "#2d2d2d"

class MultiAIGUI(ctk.CTk):
    def __init__(self, agent):
        super().__init__()
        self.agent = agent
        self.title("MultiAI")
        self.geometry("1280x800")
        self.configure(fg_color=Theme.BACKGROUND)
        
        self.message_widgets = []
        self.spell = SpellChecker()

        # --- Font Definitions ---
        self.font_main = ctk.CTkFont(family="Segoe UI Variable", size=15)
        self.font_bold = ctk.CTkFont(family="Segoe UI Variable", size=15, weight="bold")
        self.font_status = ctk.CTkFont(family="Segoe UI Variable", size=12, slant="italic")
        self.font_title = ctk.CTkFont(family="Segoe UI Variable", size=24, weight="bold")
        self.font_code = ctk.CTkFont(family="Consolas", size=14)

        # --- Main Layout ---
        self.grid_columnconfigure((0, 2), weight=1)
        self.grid_columnconfigure(1, minsize=1200)
        self.grid_rowconfigure(0, weight=1)

        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.title_label = ctk.CTkLabel(self.main_container, text="MultiAI", font=self.font_title, text_color=Theme.SENDER_TEXT)
        self.title_label.grid(row=0, column=0, pady=(40, 20))
        self.chat_frame = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent", scrollbar_button_color=Theme.BACKGROUND, scrollbar_button_hover_color=Theme.ACCENT)
        self.chat_frame.grid(row=1, column=0, sticky="nsew")
        self.chat_frame.grid_columnconfigure(0, weight=1)
        self.bottom_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.bottom_frame.grid(row=2, column=0, pady=(10, 20), sticky="sew")
        self.bottom_frame.grid_columnconfigure(0, weight=1)
        self.status_label = ctk.CTkLabel(self.bottom_frame, text="", font=self.font_status, text_color=Theme.MUTED_TEXT)
        self.input_frame = ctk.CTkFrame(self.bottom_frame, fg_color=Theme.INPUT_BOX, corner_radius=20)
        self.input_frame.grid(row=1, column=0, sticky="ew")
        
        self.input_box = ctk.CTkTextbox(self.input_frame, font=self.font_main, fg_color="transparent", border_width=0, height=30, activate_scrollbars=False)
        self.input_box.pack(side="left", fill="x", expand=True, padx=20, pady=10)
        self.input_box.bind("<Return>", self.send_message)
        self.input_box.bind("<KeyRelease>", self._check_spelling)
        self.input_box.bind("<Button-3>", self._show_suggestions_menu)

        self.send_btn = ctk.CTkButton(self.input_frame, text="↑", width=30, height=30, font=ctk.CTkFont(size=20), fg_color="#3c3c3c", text_color=Theme.TEXT, hover_color="#4a4a4a", corner_radius=15, command=self.send_message)
        self.send_btn.pack(side="right", padx=(0, 10), pady=10)
        
        # --- THE DEFINITIVE FIX: Use foreground color for misspelled words ---
        self.input_box.tag_config("misspelled", foreground="red")
        
        self.after(100, self.finalize_setup)

    def finalize_setup(self):
        self.add_message("AI", "Welcome to MultiAI. How can I assist you today?")
        self.chat_frame.bind("<Configure>", self.update_wraplength)

    def _check_spelling(self, event=None):
        self.input_box.tag_remove("misspelled", "1.0", "end")
        text = self.input_box.get("1.0", "end-1c")
        for match in re.finditer(r'\w+', text):
            word = match.group()
            if self.spell.unknown([word]):
                start_index = f"1.{match.start()}"
                end_index = f"1.{match.end()}"
                self.input_box.tag_add("misspelled", start_index, end_index)

    def _show_suggestions_menu(self, event):
        index = self.input_box.index(f"@{event.x},{event.y}")
        tags = self.input_box.tag_names(index)
        if "misspelled" in tags:
            word_start, word_end = self.input_box.index(f"{index} wordstart"), self.input_box.index(f"{index} wordend")
            word, suggestions = self.input_box.get(word_start, word_end), self.spell.candidates(word)
            if suggestions:
                menu = Menu(self, tearoff=0, background=Theme.INPUT_BOX, foreground=Theme.TEXT, activebackground=Theme.ACCENT)
                for s in suggestions:
                    menu.add_command(label=s, command=lambda s=s: self._replace_word(word_start, word_end, s))
                menu.tk_popup(event.x_root, event.y_root)

    def _replace_word(self, start, end, new_word):
        self.input_box.delete(start, end)
        self.input_box.insert(start, new_word)
        self._check_spelling()

    def _render_message_content(self, parent_bubble, message):
        parts = re.split(r"(```(?:\w*\n)?[\s\S]*?```)", message)
        for part in parts:
            if part.strip():
                if part.startswith("```") and part.endswith("```"):
                    code_content = part.strip()[3:-3].strip()
                    if '\n' in code_content:
                        first_line, rest_of_code = code_content.split('\n', 1)
                        if first_line.strip().isalnum(): code_content = rest_of_code
                    code_box = ctk.CTkTextbox(parent_bubble, font=self.font_code, fg_color=Theme.CODE_BG, corner_radius=8)
                    code_box.insert("1.0", code_content)
                    code_box.configure(state="disabled")
                    code_box.pack(side="top", fill="x", expand=False, padx=40, pady=5)
                    self.message_widgets.append(code_box)
                else:
                    text_label = ctk.CTkLabel(parent_bubble, text=part.strip(), font=self.font_main, text_color=Theme.TEXT, justify="left", anchor="w")
                    text_label.pack(side="top", fill="x", expand=True, padx=(40, 0), pady=2)
                    self.message_widgets.append(text_label)

    def add_message(self, sender, message):
        bubble = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        bubble.grid(sticky="ew", pady=(0, 15), padx=5)
        top_bar = ctk.CTkFrame(bubble, fg_color="transparent")
        top_bar.pack(fill="x", expand=True)
        sender_label = ctk.CTkLabel(top_bar, text=sender, font=self.font_bold, text_color=Theme.SENDER_TEXT)
        sender_label.pack(side="left")
        if sender == "AI":
            copy_button = ctk.CTkButton(top_bar, text="Copy", width=40, height=20, font=ctk.CTkFont(size=12), fg_color=Theme.INPUT_BOX, text_color=Theme.MUTED_TEXT, hover_color=Theme.ACCENT, command=lambda m=message: self.copy_to_clipboard(m))
            copy_button.pack(side="right")
        self._render_message_content(bubble, message)
        self._scroll_to_bottom()

    def add_streaming_message(self, sender):
        bubble = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        bubble.grid(sticky="ew", pady=(0, 15), padx=5)
        sender_label = ctk.CTkLabel(bubble, text=sender, font=self.font_bold, text_color=Theme.SENDER_TEXT, width=40, anchor="nw")
        sender_label.pack(side="left", anchor="n", padx=(0, 10))
        message_label = ctk.CTkLabel(bubble, text="", font=self.font_main, text_color=Theme.TEXT, justify="left", anchor="w")
        message_label.pack(side="left", fill="x", expand=True)
        self._scroll_to_bottom()
        return bubble, message_label
    
    def add_correction_note(self, bubble, correction_text):
        correction_label = ctk.CTkLabel(bubble, text=f"Corrected to: \"{correction_text}\"", font=self.font_status, text_color=Theme.MUTED_TEXT, justify="left", anchor="w")
        correction_label.pack(side="top", fill="x", expand=True, padx=(0, 0), pady=(2,0))
        self._scroll_to_bottom()

    def copy_to_clipboard(self, message_text):
        self.clipboard_clear()
        self.clipboard_append(message_text)

    def update_wraplength(self, event=None):
        new_wraplength = self.main_container.winfo_width() - 120
        for widget in self.message_widgets:
            if widget.winfo_exists() and isinstance(widget, ctk.CTkLabel):
                widget.configure(wraplength=new_wraplength)

    def _create_streaming_bubble(self, queue):
        streaming_bubble, streaming_label = self.add_streaming_message("AI")
        queue.put((streaming_bubble, streaming_label))

    def _scroll_to_bottom(self):
        self.update_idletasks()
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def _update_ui_safely(self, func, *args, **kwargs):
        self.after(0, lambda: func(*args, **kwargs))

    def send_message(self, event=None):
        user_msg = self.input_box.get("1.0", "end-1c").strip()
        if not user_msg: return "break"
        if event and event.keysym == "Return":
            user_bubble = self.add_message("You", user_msg)
            self._clear_input_box()
            self.send_btn.configure(state="disabled", fg_color="#2a2a2a")
            threading.Thread(target=self.get_ai_response, args=(user_msg, user_bubble), daemon=True).start()
            return "break"
        
        user_bubble = self.add_message("You", user_msg)
        self._clear_input_box()
        self.send_btn.configure(state="disabled", fg_color="#2a2a2a")
        threading.Thread(target=self.get_ai_response, args=(user_msg, user_bubble), daemon=True).start()

    def _clear_input_box(self):
        self.input_box.delete("1.0", "end")

    def get_ai_response(self, user_msg, user_bubble):
        streaming_bubble, streaming_label, full_response_text = None, None, ""
        try:
            self._update_ui_safely(self.status_label.grid, row=0, column=0, pady=(0, 10), sticky="ew")
            widget_queue = Queue()
            self._update_ui_safely(self._create_streaming_bubble, widget_queue)
            streaming_bubble, streaming_label = widget_queue.get()
            
            response_generator = self.agent.run(user_msg)
            
            for chunk in response_generator:
                if isinstance(chunk, dict):
                    if 'status' in chunk and chunk['status'] != "Done":
                        self._update_ui_safely(self.status_label.configure, text=chunk['status'])
                    elif 'correction' in chunk:
                        self._update_ui_safely(self.add_correction_note, user_bubble, chunk['correction'])
                elif isinstance(chunk, str):
                    full_response_text += chunk
                    self._update_ui_safely(streaming_label.configure, text=full_response_text)
                    self._update_ui_safely(self._scroll_to_bottom)
                    
        except Exception as e:
            if streaming_bubble: self._update_ui_safely(streaming_bubble.destroy)
            self.add_message("System", f"[Error] {str(e)}")
        finally:
            if streaming_bubble: self._update_ui_safely(streaming_bubble.destroy)
            if full_response_text: self._update_ui_safely(self.add_message, "AI", full_response_text)
            self._update_ui_safely(self.send_btn.configure, state="normal", fg_color="#3c3c3c")
            self._update_ui_safely(self.status_label.grid_remove)

if __name__ == "__main__":
    console = Console()
    console.print("[bold red]This file should not be run directly. Run main.py with the --gui flag.[/bold red]")