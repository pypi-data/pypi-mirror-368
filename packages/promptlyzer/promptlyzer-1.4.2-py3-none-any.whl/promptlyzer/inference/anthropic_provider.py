"""Anthropic inference provider implementation."""

import time
from typing import List, Optional, Dict, Any, Union, AsyncGenerator
import anthropic
from anthropic import AsyncAnthropic, Anthropic

from .base import InferenceProvider, InferenceResponse, InferenceMetrics, StreamChunk


class AnthropicProvider(InferenceProvider):
    """Anthropic (Claude) inference provider."""
    
    # Model pricing per 1K tokens (as of 2025)
    PRICING = {
        "claude-3-5-sonnet-20241022": {"prompt": 0.00300, "completion": 0.01500},
        "claude-3-haiku-20240307": {"prompt": 0.00025, "completion": 0.00125},
        "claude-3-opus-20240229": {"prompt": 0.01500, "completion": 0.07500},
        "claude-3-sonnet-20240229": {"prompt": 0.00300, "completion": 0.01500},
    }
    
    SUPPORTED_MODELS = list(PRICING.keys())
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """Initialize Anthropic provider."""
        super().__init__(api_key, base_url)
        self.client = Anthropic(api_key=api_key, base_url=base_url)
        self.async_client = AsyncAnthropic(api_key=api_key, base_url=base_url)
    
    def get_supported_models(self) -> List[str]:
        """Get list of supported Anthropic models."""
        return self.SUPPORTED_MODELS
    
    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost based on Anthropic pricing."""
        if model not in self.PRICING:
            # Default pricing for unknown models
            pricing = {"prompt": 0.00300, "completion": 0.01500}
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
        """Perform async inference using Anthropic."""
        start_time = time.time()
        
        try:
            # Prepare messages
            messages = [{"role": "user", "content": prompt}]
            
            # Set default max_tokens if not provided
            if max_tokens is None:
                max_tokens = 4096
            
            # Build parameters
            params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs
            }
            
            # Only add system if it exists
            if system_prompt:
                params["system"] = system_prompt
            
            if stream:
                # Streaming response
                async def stream_generator():
                    collected_content = []
                    prompt_tokens = 0
                    completion_tokens = 0
                    
                    stream = await self.async_client.messages.create(**params, stream=True)
                    async for chunk in stream:
                            if chunk.type == "content_block_delta":
                                content = chunk.delta.text
                                collected_content.append(content)
                                
                                # Estimate tokens (rough approximation)
                                completion_tokens += len(content.split()) // 4
                                
                                yield StreamChunk(content=content, is_final=False)
                            
                            elif chunk.type == "message_start":
                                # Get usage info from message_start event
                                if hasattr(chunk, "message") and hasattr(chunk.message, "usage"):
                                    prompt_tokens = chunk.message.usage.input_tokens
                            
                            elif chunk.type == "message_delta":
                                # Get final usage info
                                if hasattr(chunk, "usage"):
                                    completion_tokens = chunk.usage.output_tokens
                    
                    # Final chunk with metrics
                    latency_ms = self.measure_latency(start_time)
                    full_content = "".join(collected_content)
                    
                    # If we didn't get token counts from the stream, estimate
                    if prompt_tokens == 0:
                        prompt_tokens = len(prompt.split()) // 4 + (len(system_prompt.split()) // 4 if system_prompt else 0)
                    if completion_tokens == 0:
                        completion_tokens = len(full_content.split()) // 4
                    
                    total_tokens = prompt_tokens + completion_tokens
                    cost = self.calculate_cost(model, prompt_tokens, completion_tokens)
                    
                    metrics = InferenceMetrics(
                        provider="anthropic",
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
                response = await self.async_client.messages.create(**params)
                
                latency_ms = self.measure_latency(start_time)
                
                # Extract token usage
                prompt_tokens = response.usage.input_tokens
                completion_tokens = response.usage.output_tokens
                total_tokens = prompt_tokens + completion_tokens
                
                # Calculate cost
                cost = self.calculate_cost(model, prompt_tokens, completion_tokens)
                
                # Create metrics
                metrics = InferenceMetrics(
                    provider="anthropic",
                    model=model,
                    latency_ms=latency_ms,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    cost=cost,
                    success=True
                )
                
                # Extract content
                content = response.content[0].text
                
                return InferenceResponse(
                    content=content,
                    model=model,
                    provider="anthropic",
                    metrics=metrics,
                    raw_response=response.model_dump()
                )
            
        except Exception as e:
            latency_ms = self.measure_latency(start_time)
            
            # Create error metrics
            metrics = InferenceMetrics(
                provider="anthropic",
                model=model,
                latency_ms=latency_ms,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                cost=0.0,
                success=False,
                error=str(e)
            )
            
            raise Exception(f"Anthropic inference failed: {str(e)}")