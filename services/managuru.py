import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os

class ManaGuruService:
    def __init__(self):
        self.model_name = "Suru/Bhagvad-Gita-LLM"
        self.model = None
        self.tokenizer = None
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        print(f"Initializing Mana Guru Service on {self.device}...")

    def load_model(self):
        """Loads the model and tokenizer lazily."""
        if self.model is None:
            print(f"Loading model {self.model_name}...")
            
            # Load in 4-bit only if CUDA is available, otherwise normal load
            kwargs = {
                "device_map": "auto",
            }
            if torch.cuda.is_available():
                kwargs["load_in_4bit"] = True
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name, 
                **kwargs
            )
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name, 
                use_fast=True
            )
            print("Model loaded successfully.")

    def generate_guidance(self, prompt: str):
        """Generates guidance based on the Gita LLM."""
        if self.model is None:
            self.load_model()

        prompt_format = f"<s>[INST] {prompt} [/INST]"
        
        # Prepare inputs
        model_inputs = self.tokenizer(prompt_format, return_tensors="pt").to(self.device)
        
        # Generate output
        with torch.no_grad():
            output = self.model.generate(
                **model_inputs, 
                max_new_tokens=1000,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(output[0], skip_special_tokens=True)
        
        # Clean up the response (remove the prompt if it's echoed)
        if "[/INST]" in response:
            response = response.split("[/INST]")[-1].strip()
            
        return response

# Single instance for the application
managuru_service = ManaGuruService()
