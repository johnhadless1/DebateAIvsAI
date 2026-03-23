from llama_cpp import Llama


class GGUFInference:
    """Loads and runs a GGUF model via llama.cpp with optional GPU offloading."""

    def __init__(self, model_path: str, n_gpu_layers: int = 35, n_ctx: int = 2048):
        print(f"📥 Loading GGUF model: {model_path}")

        try:
            self.llm = Llama(
                model_path=model_path,
                n_gpu_layers=n_gpu_layers,
                n_ctx=n_ctx,
                verbose=False,
                cuda=True,
            )
            print("✅ GGUF model loaded (GPU enabled)")
        except Exception as e:
            print(f"⚠️  GPU load failed ({e}), falling back to CPU.")
            self.llm = Llama(
                model_path=model_path,
                n_gpu_layers=0,
                n_ctx=n_ctx,
                verbose=False,
            )

    def generate(self, prompt: str, max_length: int = 500) -> str:
        """Generate a response using the ChatML prompt format (Dolphin / Llama 3.2)."""

        formatted_prompt = (
            "<|im_start|>system\n"
            "You are a helpful AI assistant. Be direct and concise.\n"
            "<|im_end|>\n"
            "<|im_start|>user\n"
            f"{prompt}\n"
            "<|im_end|>\n"
            "<|im_start|>assistant\n"
        )

        try:
            output = self.llm(
                formatted_prompt,
                max_tokens=max_length,
                temperature=1.3,
                top_p=0.95,
                top_k=40,
                repeat_penalty=1.05,
                stop=["<|im_end|>", "user:", "system:"],
            )
            response = output["choices"][0]["text"].strip()
            return response if response else "..."
        except Exception as e:
            print(f"❌ Generation error: {e}")
            return "..."
