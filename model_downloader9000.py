from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from pathlib import Path

# WARNING!! SCROLL DOWN HERE!!!! THIS ISNT CONFIG THERE, CONFIG IS FAR DOWN THAT YOU CAN EDIT.

def download_model(model_name: str, save_dir: str) -> None:
    """
    Downloads a model and tokenizer, then saves them locally.

    Args:
        model_name (str): Hugging Face model ID
        save_dir (str): Directory where the model will be saved
    """

    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    print(f"🔄 Downloading model: {model_name}...")

    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float32,
        device_map="auto",
        trust_remote_code=True
    )

    tokenizer.save_pretrained(save_path)
    model.save_pretrained(save_path)

    print(f"✅ Model saved to: {save_path}")

## CONFIG HERE!!!!!!!!!!!

if __name__ == "__main__":
    MODEL_NAME = "dphn/Dolphin3.0-Llama3.2-1B"
    SAVE_DIR = "./models/llama3-1b"

    download_model(MODEL_NAME, SAVE_DIR)
