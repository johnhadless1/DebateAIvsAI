import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

from debate_system import DebateSystem


class DebateGUI:
    """Tkinter GUI for the AI vs AI debate system."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🔥 AI vs AI Debate")
        self.root.geometry("1400x900")

        self.system = DebateSystem()
        self._build_widgets()
        self._poll_display()

    # ------------------------------------------------------------------
    # Widget construction
    # ------------------------------------------------------------------

    def _build_widgets(self):
        # Title
        tk.Label(self.root, text="🔥 AI vs AI Debate System", font=("Arial", 18, "bold")).pack(
            anchor=tk.W, padx=10, pady=10
        )

        # Topic input row
        input_row = tk.Frame(self.root)
        input_row.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(input_row, text="Topic:", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=5)

        self.topic_input = tk.Entry(input_row, font=("Arial", 11))
        self.topic_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.topic_input.insert(0, "AI is good for humanity")

        tk.Button(
            input_row, text="🔥 START DEBATE", command=self.start_debate,
            font=("Arial", 12, "bold"), bg="green", fg="white", padx=20, pady=10,
        ).pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(self.root, text="", font=("Arial", 10), fg="gray")
        self.status_label.pack(padx=10)

        # Main area
        main = tk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left: debate display
        left = tk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.display = scrolledtext.ScrolledText(
            left, height=30, width=70, wrap=tk.WORD, state=tk.DISABLED,
            bg="#2b2b2b", fg="#e8e8e8", font=("Arial", 12),
            spacing1=10, spacing2=5, spacing3=10,
        )
        self.display.pack(fill=tk.BOTH, expand=True)

        # Right: controls
        right = tk.LabelFrame(main, text="⚙️ Controls", font=("Arial", 11, "bold"))
        right.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, ipadx=5, ipady=5, anchor=tk.NE)

        tk.Label(right, text="Debate:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=5, pady=(5, 0))

        for label, cmd, bg in (
            ("▶️  Continue",      self.continue_debate,  "#4CAF50"),
            ("⏸️  Pause",         self.pause_debate,     "#FF9800"),
            ("▶️  Resume",        self.resume_debate,    "#2196F3"),
            ("🔓 Force Unpause",  self.force_unpause,    "#9C27B0"),
            ("⚡ Force Continue", self.force_continue,   "#FF5722"),
        ):
            tk.Button(right, text=label, command=cmd, font=("Arial", 10), width=20, bg=bg, fg="white").pack(
                padx=5, pady=2, fill=tk.X
            )

        self.auto_btn = tk.Button(
            right, text="🤖 Auto: OFF", command=self.toggle_auto_continue,
            font=("Arial", 10), width=20, bg="gray",
        )
        self.auto_btn.pack(padx=5, pady=2, fill=tk.X)

        # Force turn buttons
        tk.Label(right, text="Force Turn:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=5, pady=(10, 0))
        turn_frame = tk.Frame(right)
        turn_frame.pack(padx=5, pady=5, fill=tk.X)
        tk.Button(turn_frame, text="Alpha", command=self.force_alpha_turn, font=("Arial", 9), bg="#E91E63", fg="white").pack(side=tk.LEFT, fill=tk.X, padx=2)
        tk.Button(turn_frame, text="Beta",  command=self.force_beta_turn,  font=("Arial", 9), bg="#00BCD4", fg="white").pack(side=tk.LEFT, fill=tk.X, padx=2)

        # User interjection
        tk.Label(right, text="Your Input:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=5, pady=(10, 0))
        user_row = tk.Frame(right)
        user_row.pack(padx=5, pady=5, fill=tk.X)
        self.user_input = tk.Entry(user_row, font=("Arial", 10))
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        self.user_input.bind("<Return>", lambda _: self.user_interjection())
        tk.Button(user_row, text="Say It!", command=self.user_interjection, font=("Arial", 10), bg="#4CAF50", fg="white").pack(side=tk.LEFT)

        # System prompt editors
        for label, attr, update_cmd in (
            ("AI-Alpha Prompt:", "alpha_prompt", self.update_alpha_prompt),
            ("AI-Beta Prompt:",  "beta_prompt",  self.update_beta_prompt),
        ):
            tk.Label(right, text=label, font=("Arial", 9, "bold")).pack(anchor=tk.W, padx=5, pady=(10, 0))
            widget = tk.Text(right, height=3, width=25, font=("Arial", 8))
            widget.pack(padx=5, pady=2, fill=tk.X)
            setattr(self, attr, widget)
            tk.Button(right, text=f"Update {label.split('-')[1].split(' ')[0]}", command=update_cmd, font=("Arial", 9), width=20).pack(padx=5, pady=2, fill=tk.X)

        self.alpha_prompt.insert(1.0, self.system.ai1_system_prompt)
        self.beta_prompt.insert(1.0, self.system.ai2_system_prompt)

        # Chat management
        tk.Label(right, text="Chat:", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=5, pady=(10, 0))
        for label, cmd, bg, fg in (
            ("💾 Save",       self.save_debate,  "#2196F3", "white"),
            ("🗑️  Clear Chat", self.clear_chat,   "#FF9800", "white"),
            ("❌ End",        self.end_debate,   "red",     "white"),
        ):
            tk.Button(right, text=label, command=cmd, font=("Arial", 10), width=20, bg=bg, fg=fg).pack(padx=5, pady=2, fill=tk.X)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def start_debate(self):
        topic = self.topic_input.get().strip()
        if not topic:
            messagebox.showwarning("Error", "Enter a topic!")
            return
        threading.Thread(target=self.system.start_debate, args=(topic,), daemon=True).start()

    def continue_debate(self):
        threading.Thread(target=self.system.continue_debate, daemon=True).start()

    def pause_debate(self):
        self.system.pause_debate()

    def resume_debate(self):
        self.system.resume_debate()

    def force_unpause(self):
        self.system.paused = False
        print("🔓 Forced unpause\n")

    def force_continue(self):
        self.system.paused = False
        threading.Thread(target=self.system.continue_debate, daemon=True).start()

    def force_alpha_turn(self):
        self.system.turn = 1
        threading.Thread(target=self.system.continue_debate, daemon=True).start()

    def force_beta_turn(self):
        self.system.turn = 2
        threading.Thread(target=self.system.continue_debate, daemon=True).start()

    def toggle_auto_continue(self):
        self.system.toggle_auto_continue()
        on = self.system.auto_continue
        self.auto_btn.config(bg="green" if on else "gray", text=f"🤖 Auto: {'ON' if on else 'OFF'}")

    def user_interjection(self):
        message = self.user_input.get().strip()
        if not message:
            return
        self.user_input.delete(0, tk.END)
        self.system.user_interjection(message)

    def update_alpha_prompt(self):
        self.system.set_ai1_prompt(self.alpha_prompt.get(1.0, tk.END).strip())
        messagebox.showinfo("Updated", "AI-Alpha prompt updated!")

    def update_beta_prompt(self):
        self.system.set_ai2_prompt(self.beta_prompt.get(1.0, tk.END).strip())
        messagebox.showinfo("Updated", "AI-Beta prompt updated!")

    def clear_chat(self):
        if messagebox.askyesno("Confirm", "Delete ALL messages?"):
            self.system.memory.clear()

    def end_debate(self):
        self.system.end_debate()

    def save_debate(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if filename:
            self.system.save_debate(filename)
            messagebox.showinfo("Saved", "Debate saved!")

    # ------------------------------------------------------------------
    # Display polling
    # ------------------------------------------------------------------

    def _poll_display(self):
        recent = self.system.memory.get_recent_messages(limit=50)

        self.display.tag_config("alpha_name", foreground="#FF4444", font=("Arial", 12, "bold"))
        self.display.tag_config("beta_name",  foreground="#307fBB", font=("Arial", 12, "bold"))
        self.display.tag_config("user_name",  foreground="#88DD88", font=("Arial", 12, "bold"))
        self.display.tag_config("alpha_text", foreground="#FFAAAA")
        self.display.tag_config("beta_text",  foreground="#AABBDD")
        self.display.tag_config("user_text",  foreground="#AADDAA")

        self.display.config(state=tk.NORMAL)
        self.display.delete(1.0, tk.END)

        for msg in recent:
            author, content = msg["author"], msg["content"]
            if "Alpha" in author:
                self.display.insert(tk.END, f"🤖 {author}:\n", "alpha_name")
                self.display.insert(tk.END, f"{content}\n\n", "alpha_text")
            elif "Beta" in author:
                self.display.insert(tk.END, f"🤖 {author}:\n", "beta_name")
                self.display.insert(tk.END, f"{content}\n\n", "beta_text")
            else:
                self.display.insert(tk.END, f"👤 {author}:\n", "user_name")
                self.display.insert(tk.END, f"{content}\n\n", "user_text")

        self.display.config(state=tk.DISABLED)
        self.display.see(tk.END)
        self.status_label.config(text=self.system.get_status())

        self.root.after(500, self._poll_display)


if __name__ == "__main__":
    root = tk.Tk()
    DebateGUI(root)
    root.mainloop()
