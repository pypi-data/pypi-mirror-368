"""Together AI inference provider implementation."""

import time
from typing import List, Optional, Dict, Any, Union, AsyncGenerator
import aiohttp
import requests
import json

from .base import InferenceProvider, InferenceResponse, InferenceMetrics, StreamChunk


class TogetherProvider(InferenceProvider):
    """Together AI inference provider."""
    
    # Model pricing per 1M tokens (Together uses per-million pricing)
    PRICING = {
        "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo": {"prompt": 0.88, "completion": 0.88},
        "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo": {"prompt": 0.18, "completion": 0.18},
        "meta-llama/Llama-3.2-3B-Instruct-Turbo": {"prompt": 0.06, "completion": 0.06},
        "mistralai/Mixtral-8x7B-Instruct-v0.1": {"prompt": 0.60, "completion": 0.60},
        "qwen/Qwen2.5-72B-Instruct-Turbo": {"prompt": 0.90, "completion": 0.90},
        "qwen/Qwen2.5-7B-Instruct-Turbo": {"prompt": 0.30, "completion": 0.30},
        "deepseek-ai/deepseek-v3": {"prompt": 0.14, "completion": 0.14},
        "deepseek-ai/deepseek-r1-distill-qwen-1.5b": {"prompt": 0.06, "completion": 0.06},
    }
    
    SUPPORTED_MODELS = list(PRICING.keys())
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """Initialize Together provider."""
        super().__init__(api_key, base_url or "https://api.together.xyz/v1")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_supported_models(self) -> List[str]:
        """Get list of supported Together AI models."""
        return self.SUPPORTED_MODELS
    
    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost based on Together AI pricing."""
        if model not in self.PRICING:
            # Default pricing for unknown models
            pricing = {"prompt": 0.60, "completion": 0.60}
        else:
            pricing = self.PRICING[model]
        
        # Convert from per-million to per-token pricing
        prompt_cost = (prompt_tokens / 1_000_000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1_000_000) * pricing["completion"]
        
        return round(prompt_cost + completion_cost, 6)
    
    async def infer_async(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Union[InferenceResponse, AsyncGenerator[StreamChunk, None]]:
        """Perform async inference using Together AI."""
        start_time = time.time()
        
        try:
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Prepare request data
            data = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens or 2048,
                **kwargs
            }
            
            if stream:
                # Streaming response
                data["stream"] = True
                
                async def stream_generator():
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            f"{self.base_url}/chat/completions",
                            headers=self.headers,
                            json=data
                        ) as response:
                            collected_content = []
                            
                            async for line in response.content:
                                line = line.decode('utf-8').strip()
                                if line.startswith('data: '):
                                    json_str = line[6:]  # Remove 'data: ' prefix
                                    
                                    if json_str == '[DONE]':
                                        # Final chunk with metrics
                                        latency_ms = self.measure_latency(start_time)
                                        full_content = "".join(collected_content)
                                        
                                        # Estimate tokens
                                        prompt_tokens = len(prompt.split()) // 4 + (len(system_prompt.split()) // 4 if system_prompt else 0)
                                        completion_tokens = len(full_content.split()) // 4
                                        total_tokens = prompt_tokens + completion_tokens
                                        
                                        cost = self.calculate_cost(model, prompt_tokens, completion_tokens)
                                        
                                        metrics = InferenceMetrics(
                                            provider="together",
                                            model=model,
                                            latency_ms=latency_ms,
                                            prompt_tokens=prompt_tokens,
                                            completion_tokens=completion_tokens,
                                            total_tokens=total_tokens,
                                            cost=cost,
                                            success=True
                                        )
                                        
                                        yield StreamChunk(content="", is_final=True, metrics=metrics)
                                        break
                                    
                                    try:
                                        chunk_data = json.loads(json_str)
                                        if 'choices' in chunk_data and chunk_data['choices']:
                                            delta = chunk_data['choices'][0].get('delta', {})
                                            if 'content' in delta:
                                                content = delta['content']
                                                collected_content.append(content)
                                                yield StreamChunk(content=content, is_final=False)
                                    except json.JSONDecodeError:
                                        continue
                
                return stream_generator()
            else:
                # Non-streaming response
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/chat/completions",
                        headers=self.headers,
                        json=data
                    ) as response:
                        result = await response.json()
                    
                    if response.status != 200:
                        raise Exception(f"API error: {result}")
            
            latency_ms = self.measure_latency(start_time)
            
            # Extract token usage
            usage = result.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)
            
            # Calculate cost
            cost = self.calculate_cost(model, prompt_tokens, completion_tokens)
            
            # Create metrics
            metrics = InferenceMetrics(
                provider="together",
                model=model,
                latency_ms=latency_ms,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost=cost,
                success=True
            )
            
            # Extract content
            content = result["choices"][0]["message"]["content"]
            
            return InferenceResponse(
                content=content,
                model=model,
                provider="together",
                metrics=metrics,
                raw_response=result
            )
            
        except Exception as e:
            latency_ms = self.measure_latency(start_time)
            
            # Create error metrics
            metrics = InferenceMetrics(
                provider="together",
                model=model,
                latency_ms=latency_ms,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                cost=0.0,
                success=False,
                error=str(e)
            )
            
            raise Exception(f"Together AI inference failed: {str(e)}")