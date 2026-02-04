"""
AXIOM Brain using Ollama (simpler and better than llama-cpp-python)
"""
import os
import ollama
from typing import Optional


class AxiomBrain:
    """
    AXIOM brain using Ollama - simpler than llama-cpp-python
    
    Benefits:
    - Automatic GPU handling
    - Easier to update (just edit Modelfile)
    - Better performance
    - Cleaner code
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize with Ollama model.
        Prefers the fine-tuned LoRA merge "drobotics_test" unless overridden.
        """
        preferred = model_name or os.getenv("AXIOM_MODEL") or "drobotics_test"
        self.model_name = preferred
        print(f"✅ Using Ollama model: {self.model_name}")
    
    def generate_response(
        self,
        user_input: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 180,
        temperature: float = 0.4,
        **kwargs
    ) -> str:
        """
        Generate response using Ollama
        
        Args:
            user_input: User's question
            system_prompt: Optional system prompt override (usually not needed)
            max_tokens: Maximum response length
            temperature: Creativity (0.4 = focused)
        
        Returns:
            Model's response
        """
        try:
            # Build messages
            messages = []
            
            # Add system prompt if provided (override model's default)
            if system_prompt:
                messages.append({
                    'role': 'system',
                    'content': system_prompt
                })
            
            # Add user message
            messages.append({
                'role': 'user',
                'content': user_input
            })
            
            # Generate response
            try:
                response = ollama.chat(
                    model=self.model_name,
                    messages=messages,
                    options={
                        'temperature': temperature,
                        'num_predict': max_tokens,
                    }
                )
            except Exception as primary_error:
                # Graceful fallback if the preferred model is missing; keeps service alive.
                if "not found" in str(primary_error).lower() and self.model_name != "drobo_lab_v2":
                    fallback = "drobo_lab_v2"
                    print(f"⚠️  Model '{self.model_name}' missing. Falling back to '{fallback}'")
                    self.model_name = fallback
                    response = ollama.chat(
                        model=self.model_name,
                        messages=messages,
                        options={
                            'temperature': temperature,
                            'num_predict': max_tokens,
                        }
                    )
                else:
                    raise
            
            return response['message']['content'].strip()
            
        except Exception as e:
            print(f"❌ Ollama error: {e}")
            return "I am having trouble right now. Can you try again?"


# Singleton
_brain = None

def get_axiom_brain(model_name: Optional[str] = None) -> AxiomBrain:
    """Get or create Ollama brain instance."""
    global _brain
    if _brain is None:
        _brain = AxiomBrain(model_name)
    return _brain


if __name__ == "__main__":
    # Test the brain
    brain = AxiomBrain()
    
    test_queries = [
        "Hi, how are you?",
        "What is the Drobotics Lab?",
        "Tell me about the Jetson Orin",
    ]
    
    print("Testing Ollama Brain:\n")
    print("="*60)
    for query in test_queries:
        print(f"\nQ: {query}")
        response = brain.generate_response(query)
        print(f"A: {response}")
    print("\n" + "="*60)
