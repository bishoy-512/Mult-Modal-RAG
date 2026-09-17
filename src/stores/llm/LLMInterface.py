from abc import ABC,abstractmethod

class LLMInterface(ABC):
    @abstractmethod
    def generate(self, prompt: str, max_output_tokens: int = 512, temperature: float = 0.1):
        pass
    
    @abstractmethod
    def embedding(self, text: str):
        pass
    
    @abstractmethod
    def set_generation_model(self, model_name: str):
        pass

    @abstractmethod
    def set_embedding_model(self, model_name: str, embedding_size: int):
        pass