"""Provider module for interacting with different LLM APIs."""

import os
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class Provider(ABC):
    """Base class for LLM providers."""
    
    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> str:
        """Get completion from the model."""
        pass


class OpenRouterProvider(Provider):
    """OpenRouter API provider for accessing multiple models."""
    
    def __init__(self, model: str, api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        
    def complete(self, prompt: str, **kwargs) -> str:
        import requests
        import time
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/llmux",  # Optional
            "X-Title": "LLMux Evaluation"  # Optional
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,  # Make responses deterministic
            **kwargs
        }
        
        # Retry with exponential backoff for rate limits
        for attempt in range(3):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 429:  # Rate limited
                    if attempt < 2:  # Don't sleep on last attempt
                        sleep_time = (2 ** attempt) + 1  # 2, 5 seconds
                        time.sleep(sleep_time)
                        continue
                
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
                
            except requests.exceptions.Timeout:
                if attempt < 2:
                    time.sleep(1)
                    continue
                raise ValueError("Request timed out after 3 attempts")
            except requests.exceptions.RequestException as e:
                if attempt < 2 and "429" in str(e):
                    time.sleep((2 ** attempt) + 1)
                    continue
                raise e
        
        # If we get here, all retries failed
        raise ValueError(f"Failed to complete request for model {self.model} after 3 attempts")


class OpenAIProvider(Provider):
    """OpenAI API provider."""
    
    def __init__(self, model: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
    def complete(self, prompt: str, **kwargs) -> str:
        import openai
        client = openai.OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,  # Make responses deterministic
            **kwargs
        )
        return response.choices[0].message.content


class AnthropicProvider(Provider):
    """Anthropic API provider."""
    
    def __init__(self, model: str = "claude-3-haiku-20240307", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
    def complete(self, prompt: str, **kwargs) -> str:
        import anthropic
        client = anthropic.Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,  # Make responses deterministic
            **kwargs
        )
        return response.content[0].text


def get_provider(name: str, **kwargs) -> Provider:
    """Factory function to get provider by name."""
    providers = {
        "openrouter": OpenRouterProvider,
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
    }
    if name not in providers:
        raise ValueError(f"Unknown provider: {name}")
    return providers[name](**kwargs)