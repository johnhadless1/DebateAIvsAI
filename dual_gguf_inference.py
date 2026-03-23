from pathlib import Path
from gguf_inference import GGUFInference

DEFAULT_MODEL_NAME = "Dolphin3.0-Llama3.2-3B-IQ4_NL.gguf"


class DualGGUFInference:
    """Loads and manages two independent GGUF models for simultaneous inference."""

    def __init__(
        self,
        model1_path: str | None = None,
        model2_path: str | None = None,
        n_gpu_layers: int = 35,
    ):
        models_dir = Path(__file__).parent.parent / "models"

        if model1_path is None:
            model1_path = str(models_dir / DEFAULT_MODEL_NAME)
        if model2_path is None:
            model2_path = str(models_dir / DEFAULT_MODEL_NAME)

        print("🔥 Initializing dual GGUF inference...\n")

        print("🤖 Loading Model 1...")
        self.llm1 = GGUFInference(model1_path, n_gpu_layers=n_gpu_layers)

        print("🤖 Loading Model 2...")
        self.llm2 = GGUFInference(model2_path, n_gpu_layers=n_gpu_layers)

        print()

    def generate_model1(self, prompt: str, max_length: int = 1000) -> str:
        return self.llm1.generate(prompt, max_length)

    def generate_model2(self, prompt: str, max_length: int = 1000) -> str:
        return self.llm2.generate(prompt, max_length)
