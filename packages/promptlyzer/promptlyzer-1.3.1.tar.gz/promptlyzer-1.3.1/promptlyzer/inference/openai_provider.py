"""OpenAI inference provider implementation."""

import time
from typing import List, Optional, Dict, Any, Union, AsyncGenerator
import openai
from openai import AsyncOpenAI, OpenAI

from .base import InferenceProvider, InferenceResponse, InferenceMetrics, StreamChunk


class OpenAIProvider(InferenceProvider):
    """OpenAI inference provider."""
    
    # Model pricing per 1K tokens (as of 2025)
    PRICING = {
        "gpt-4o": {"prompt": 0.00250, "completion": 0.01000},
        "gpt-4-vision-preview": {"prompt": 0.01000, "completion": 0.03000},
        "gpt-3.5-turbo": {"prompt": 0.00050, "completion": 0.00150},
        "gpt-4-turbo": {"prompt": 0.01000, "completion": 0.03000},
        "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.00060},
    }
    
    SUPPORTED_MODELS = list(PRICING.keys())
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """Initialize OpenAI provider."""
        super().__init__(api_key, base_url)
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    
    def get_supported_models(self) -> List[str]:
        """Get list of supported OpenAI models."""
        return self.SUPPORTED_MODELS
    
    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost based on OpenAI pricing."""
        if model not in self.PRICING:
            # Default pricing for unknown models
            pricing = {"prompt": 0.01000, "completion": 0.03000}
        else:
            pricing = self.PRICING[model]
        
        prompt_cost = (prompt_tokens / 1000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1000) * pricing["completion"]
        
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
        """Perform async inference using OpenAI."""
        start_time = time.time()
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            if stream:
                # Streaming response
                async def stream_generator():
                    stream_response = self.async_client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=True,
                        **kwargs
                    )
                    
                    collected_content = []
                    prompt_tokens = 0
                    completion_tokens = 0
                    
                    async for chunk in stream_response:
                        if chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            collected_content.append(content)
                            
                            # Estimate tokens (rough approximation)
                            completion_tokens += len(content.split()) // 4
                            
                            yield StreamChunk(content=content, is_final=False)
                    
                    # Final chunk with metrics
                    latency_ms = self.measure_latency(start_time)
                    full_content = "".join(collected_content)
                    
                    # Better token estimation for final metrics
                    prompt_tokens = len(prompt.split()) // 4 + (len(system_prompt.split()) // 4 if system_prompt else 0)
                    completion_tokens = len(full_content.split()) // 4
                    total_tokens = prompt_tokens + completion_tokens
                    
                    cost = self.calculate_cost(model, prompt_tokens, completion_tokens)
                    
                    metrics = InferenceMetrics(
                        provider="openai",
                        model=model,
                        latency_ms=latency_ms,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=total_tokens,
                        cost=cost,
                        success=True
                    )
                    
                    yield StreamChunk(content="", is_final=True, metrics=metrics)
                
                return stream_generator()
            else:
                # Non-streaming response
                response = await self.async_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                
                latency_ms = self.measure_latency(start_time)
                
                # Extract token usage
                usage = response.usage
                prompt_tokens = usage.prompt_tokens
                completion_tokens = usage.completion_tokens
                total_tokens = usage.total_tokens
                
                # Calculate cost
                cost = self.calculate_cost(model, prompt_tokens, completion_tokens)
                
                # Create metrics
                metrics = InferenceMetrics(
                    provider="openai",
                    model=model,
                    latency_ms=latency_ms,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    cost=cost,
                    success=True
                )
                
                # Create response
                content = response.choices[0].message.content
                
                return InferenceResponse(
                    content=content,
                    model=model,
                    provider="openai",
                    metrics=metrics,
                    raw_response=response.model_dump()
                )
            
        except Exception as e:
            latency_ms = self.measure_latency(start_time)
            
            # Create error metrics
            metrics = InferenceMetrics(
                provider="openai",
                model=model,
                latency_ms=latency_ms,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                cost=0.0,
                success=False,
                error=str(e)
            )
            
            raise Exception(f"OpenAI inference failed: {str(e)}")