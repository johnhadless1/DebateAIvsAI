# DebateAIvsAI
Watch AI vs AI debate over useless topic or interesting topic.

> [!NOTE]
> OK, this is gonna be bit confusing to set up. Be prepared for your eyes with bad writing!!!! wink wink
>
> Made by Preplexity AI.
>
> Mostly AI/LLM models are pretty too kind and nice, if you want mean and rude results -> uncersoned AI/LLM models are better.
>
> Dolphin AI/LLM models are recommended.

> [!WARNING]
> This was only tested on Linux and mid-horsepower GPU (GTX 1660 SUPER). Everything else is unknown, expect errors and stuff. Tinker with it.
>
> Local AI/LLM models only.

### Inspired by DougDoug's [video](https://youtu.be/rPh-wiS8sjI?si=GGPKllLSePoCx6hS) about locking AIs in endless debate.

This version is more trash but more local-ized and more uncensored (we love this!!!!!!)

### Click below there to expand it.

<details>

<summary>Human-made poem (bad writing, but explains small details)</summary>

# Folder where? DEEZ NUTS!
GOTTEM!
<sub> _i will not make this joke ever again._ </sub>

Anyways, you may need to make folders in the folder:

- scripts (where the python files and stuff will live)
- models (where the AI/LLM models will live)
- database (where the AI's memory will live (plus they have dementia for extra coolness after 5 messages they gone))


## Notes

Though, I used interpreter (.venv or something like that) for this.

Watch out for missing imports and stuff like that, cuz i forgot all of it.

GGUF may be heavy, used LLM instead myself.

You may need to download LLM/AI model of your choice from `model_downloader9000.py`

<sub> YOU HAVE TO PUT THE DOWNLOADED MODEL FILE INTO `models/` NEXT TO `scripts/` FOLDER IF IT WAS MISPLACED/DOESNT WORK!!!!!!!!!!!!!!!!!! </sub>


</details>


<details>

<summary>AI-made poem (good writing, explains big details)</summary>

# 🔥 AI vs AI Debate System

An experiment in adversarial AI interaction — two local language models debate each other on any topic you give them, with a live GUI to watch, intervene, and control the action.

---

## 🗂️ Project Structure

```
├── debate_gui.py          # Entry point — the debate GUI
├── debate_system.py       # Core debate logic (turns, prompts, auto mode)
├── dual_gguf_inference.py # Loads and manages two GGUF models via llama.cpp
├── gguf_inference.py      # Single GGUF model wrapper
├── memory_system.py       # SQLite-backed conversation history
└── database/
    └── conversation.db    # Auto-created on first run
```

### How the pieces connect

```
debate_gui.py
  └─ debate_system.py
       ├─ dual_gguf_inference.py → gguf_inference.py (llama.cpp)
       └─ memory_system.py
```

---

## 🚀 Setup

### 1. Install dependencies

```bash
pip install llama-cpp-python
```

For GPU support:
```bash
CMAKE_ARGS="-DLLAMA_CUDA=on" pip install llama-cpp-python --force-reinstall
```

### 2. Download a GGUF model

Download a `.gguf` file — e.g. [Dolphin 3.0 Llama 3.2 3B](https://huggingface.co/cognitivecomputations/Dolphin3.0-Llama3.2-3B-GGUF) — and place it in a `models/` folder next to the scripts.

### 3. Set your model path

In `dual_gguf_inference.py`, update the default model name to match your file:
```python
DEFAULT_MODEL_NAME = "Dolphin3.0-Llama3.2-3B-IQ4_NL.gguf"
```

Or pass paths directly when instantiating `DualGGUFInference`.

---

## ▶️ Running

```bash
python debate_gui.py
```

---

## 🎮 Controls

| Control | Description |
|---|---|
| **Topic** field + **Start** | Begin a new debate on any topic |
| **Continue** | Advance one turn manually |
| **Pause / Resume** | Freeze and unfreeze the debate |
| **Auto: ON/OFF** | Let the debate run continuously without clicking |
| **Force Alpha / Beta** | Force a specific AI to speak next |
| **Your Input** | Interject as a third voice — pauses the AIs |
| **Alpha / Beta Prompt** | Edit each AI's system prompt live mid-debate |
| **Save** | Export the full debate to JSON |
| **Clear** | Wipe conversation history |

---

## 🤖 How It Works

1. You provide a topic.
2. **AI-Alpha** opens with an argument.
3. **AI-Beta** responds, disagreeing entirely.
4. They alternate turns indefinitely.
5. Each AI only sees the last 5 messages as context — no memory beyond that window.
6. You can jump in at any time, adjust their system prompts mid-debate, or force a turn.

The default prompts make each AI maximally adversarial — they'll disagree with everything the other says. You can tune this down or change it entirely via the prompt editors in the GUI.

---

## 📝 Notes

- Conversation history is stored in `database/conversation.db` (SQLite). Delete this file to start fresh between debates.
- GPU layers (`n_gpu_layers`) in `dual_gguf_inference.py` default to 35 — reduce this if you run out of VRAM with two models loaded simultaneously.
- Both models can be the same file (the default) or two different GGUF models for more varied outputs.

</details>
