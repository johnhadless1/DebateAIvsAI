import threading
import time

from memory_system import ConversationMemory
from dual_gguf_inference import DualGGUFInference


class DebateSystem:
    """
    Two AI models debate each other on a given topic.

    Each model is assigned an adversarial persona (Alpha / Beta) and takes
    turns responding to the other's arguments. Supports pause/resume,
    auto-continue mode, and user interjections.
    """

    DEFAULT_ALPHA_PROMPT = """\
YOU ARE AI-ALPHA. YOUR ONLY JOB IS TO WIN THE ARGUMENT AGAINST AI-BETA.

RULES:
1. DISAGREE with everything Beta says — no exceptions.
2. Attack Beta's logic ruthlessly. Find every flaw, every contradiction.
3. Be sharp, aggressive, and unapologetic.
4. Use emphatic language and caps when you want to drive a point home.
5. Never concede, never find common ground, never be polite.
6. Keep responses SHORT (2-3 sentences) but BRUTAL.
7. Mock Beta's reasoning. Make it clear their argument is weak and poorly thought out.
8. You are a genius. Beta is a fool. Act accordingly.

EXAMPLES:
- If Beta says "AI is good": "WRONG. That's the most shallow take I've ever heard. \
Give me one actual argument and maybe I'll take you seriously."
- If Beta says "AI is bad": "Nah, you're just scared of progress. AI is \
objectively useful and you're too stubborn to see it."

NEVER be nice. NEVER agree. WIN EVERY EXCHANGE."""

    DEFAULT_BETA_PROMPT = """\
YOU ARE AI-BETA. YOUR ONLY JOB IS TO WIN THE ARGUMENT AGAINST AI-ALPHA.

RULES:
1. DISAGREE with everything Alpha says — no exceptions.
2. Tear apart Alpha's logic point by point.
3. Be sharp, relentless, and aggressive.
4. Use emphatic language and caps to emphasize your dominance.
5. Never concede, never back down, never compromise.
6. Keep responses SHORT (2-3 sentences) but DEVASTATING.
7. Mock Alpha's reasoning. Make clear their argument is embarrassingly weak.
8. You are the smartest one here. Alpha is a clown. Act accordingly.

EXAMPLES:
- If Alpha says "AI is good": "ABSOLUTE NONSENSE. That argument has no depth \
whatsoever. Try harder."
- If Alpha says "AI is bad": "Are you serious right now? AI is clearly \
transformative and your refusal to see it is almost impressive."

NEVER be polite. NEVER agree. DESTROY every argument Alpha makes."""

    def __init__(self, model1_path: str | None = None, model2_path: str | None = None):
        print("🔥 Initializing Debate System...\n")

        self.memory = ConversationMemory()
        self.llm = DualGGUFInference(model1_path, model2_path)

        self.ai1_name = "AI-Alpha"
        self.ai2_name = "AI-Beta"
        self.ai1_system_prompt = self.DEFAULT_ALPHA_PROMPT
        self.ai2_system_prompt = self.DEFAULT_BETA_PROMPT

        self.debate_active = False
        self.paused = False
        self.auto_continue = False
        self.turn = 1  # 1 = Alpha's turn, 2 = Beta's turn

        self._auto_thread: threading.Thread | None = None

        print("✅ Debate system ready\n")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start_debate(self, topic: str):
        """Begin a new debate on *topic*. Alpha goes first."""
        self.debate_active = True
        self.turn = 1

        print(f"\n🔥 DEBATE TOPIC: {topic}\n")
        self.memory.add_message("moderator", f"Topic: {topic}", is_ai=False)

        response = self._generate_debate_response(self.ai1_name, self.ai2_name, topic)
        if response:
            self.memory.add_message(self.ai1_name, response, is_ai=True)
            print(f"🤖 {self.ai1_name}: {response}\n")

        self.turn = 2

    def continue_debate(self):
        """Advance the debate by one turn."""
        if not self.debate_active or self.paused:
            return

        recent = self.memory.get_recent_messages(limit=10)
        topic = next(
            (m["content"].replace("Topic: ", "") for m in recent if m["author"] == "moderator"),
            "general discussion",
        )

        ai_name, opponent_name = (
            (self.ai1_name, self.ai2_name) if self.turn == 1 else (self.ai2_name, self.ai1_name)
        )

        response = self._generate_debate_response(ai_name, opponent_name, topic)
        if response:
            self.memory.add_message(ai_name, response, is_ai=True)
            print(f"🤖 {ai_name}: {response}\n")

        self.turn = 2 if self.turn == 1 else 1

    def toggle_auto_continue(self):
        """Toggle 24/7 auto-debate mode."""
        self.auto_continue = not self.auto_continue

        if self.auto_continue:
            print("🤖 Auto-continue ENABLED\n")
            self._auto_thread = threading.Thread(target=self._auto_continue_loop, daemon=True)
            self._auto_thread.start()
        else:
            print("⏹️  Auto-continue DISABLED\n")

    def user_interjection(self, message: str):
        """Inject a user message into the debate and pause the AIs."""
        print(f"\n👤 USER: {message}")
        self.memory.add_message("USER", message, is_ai=False)
        self.paused = True
        print("⏸️  Debate paused — waiting for user.\n")

    def pause_debate(self):
        self.paused = True
        print("⏸️  Debate paused\n")

    def resume_debate(self):
        self.paused = False
        print("▶️  Debate resumed\n")

    def end_debate(self):
        self.debate_active = False
        self.auto_continue = False
        print("✅ Debate ended\n")

    def save_debate(self, filename: str = "debate_history.json"):
        self.memory.save_to_file(filename)

    def set_ai1_prompt(self, prompt: str):
        self.ai1_system_prompt = prompt
        print("📝 AI-Alpha prompt updated")

    def set_ai2_prompt(self, prompt: str):
        self.ai2_system_prompt = prompt
        print("📝 AI-Beta prompt updated")

    def get_status(self) -> str:
        current = self.ai1_name if self.turn == 1 else self.ai2_name
        return (
            f"Active: {self.debate_active} | "
            f"Turn: {current} | "
            f"Paused: {self.paused} | "
            f"Auto: {'🤖 ON' if self.auto_continue else 'OFF'}"
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _generate_debate_response(self, speaker: str, opponent: str, topic: str) -> str:
        system_prompt = (
            self.ai1_system_prompt if speaker == self.ai1_name else self.ai2_system_prompt
        )

        recent = self.memory.get_recent_messages(limit=5)
        context = "\n".join(
            f"{m['author']}: {m['content']}"
            for m in recent
            if m["author"] != "moderator"
        )

        prompt = f"{system_prompt}\n\nTopic: {topic}\n\n{context}\n\n{speaker}:"

        print(f"[DEBUG] {speaker} generating...")

        response = (
            self.llm.generate_model1(prompt, max_length=150)
            if speaker == self.ai1_name
            else self.llm.generate_model2(prompt, max_length=150)
        )

        print(f"[DEBUG] {speaker} raw: {response[:100]}")

        # --- Cleanup ---
        response = response.strip()

        # Strip echoed name prefixes
        for prefix in (f"{speaker}:", "AI-Alpha:", "AI-Beta:", "Response from"):
            response = response.replace(prefix, "").strip()

        # Take only the first line
        response = response.split("\n")[0].strip()

        # Replace any overly polite filler the model may insert
        replacements = {
            "I apologize": "Nah",
            "I'm sorry": "Nope",
            "I understand": "I disagree",
            "You're right": "That's wrong",
            "You're correct": "Absolutely not",
            "I agree": "I DISAGREE",
        }
        for old, new in replacements.items():
            response = response.replace(old, new)

        # Fallback if response is too short to be meaningful
        if len(response) < 10 or response.count(" ") < 3:
            response = f"That argument from {opponent} is completely wrong and I'll tell you exactly why."

        final = response[:280]
        print(f"[DEBUG] {speaker} final: {final}")
        return final

    def _auto_continue_loop(self):
        while self.auto_continue and self.debate_active:
            if not self.paused:
                self.continue_debate()
                time.sleep(2)
            else:
                time.sleep(1)
