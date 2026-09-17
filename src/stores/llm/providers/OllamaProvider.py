from ..LLMInterface import LLMInterface
from openai import OpenAI

class OllamaProvider(LLMInterface):
    def __init__(self, api_key: str, base_url: str, max_output_tokens: int = 1000, temperature: float = 0.1):
        self.api_key = api_key
        self.base_url = base_url
        self.generation_model_name = None
        self.embedding_model_name = None
        self.embedding_size = None
        self.max_output_tokens = max_output_tokens
        self.temperature = temperature
        self.client = OpenAI(api_key = self.api_key, base_url = self.base_url)
    
    def set_embedding_model(self, model_name: str, embedding_size: int = 1024):
        self.embedding_model_name = model_name
        self.embedding_size = embedding_size
        
    def set_generation_model(self, model_name: str):
        self.generation_model_name = model_name
        
    def embedding(self, text: str):
        if self.embedding_model_name is None:
            raise ValueError("Set Embedding Model")
        
        response = self.client.embeddings.create(model = self.embedding_model_name,
                                                dimensions = self.embedding_size,
                                                input = text)
    
        return response.data[0].embedding
    
    def generate(self, prompt, max_output_tokens: int = None, temperature: float = None):        
        if not self.generation_model_name:
            raise ValueError("Set Generation Model")
        
        max_output_tokens = max_output_tokens if max_output_tokens is not None else self.max_output_tokens

        temperature = temperature if temperature is not None else self.temperature
        
        response = self.client.chat.completions.create(model = self.generation_model_name,
                messages = [{"role": "user", "content": prompt}],
                max_tokens = max_output_tokens,
                temperature = temperature,
                extra_body={"think": False},
                    )
        print(response)
        return response.choices[0].message.content