"""Base classes for inference providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, AsyncGenerator, Generator
from enum import Enum
import time


class ModelProvider(str, Enum):
    """Supported model providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    TOGETHER = "together"


@dataclass
class InferenceMetrics:
    """Metrics collected during inference."""
    provider: str
    model: str
    latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    success: bool = True
    error: Optional[str] = None
    prompt_metadata: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    team_id: Optional[str] = None
    session_id: Optional[str] = None
    optimization_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for API submission."""
        data = {
            "provider": self.provider,
            "model": self.model,
            "latency_ms": self.latency_ms,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "cost": self.cost,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "error": self.error
        }
        
        if self.prompt_metadata:
            data["prompt_metadata"] = self.prompt_metadata
        if self.user_id:
            data["user_id"] = self.user_id
        if self.team_id:
            data["team_id"] = self.team_id
        if self.session_id:
            data["session_id"] = self.session_id
        if self.optimization_data:
            data["optimization_data"] = self.optimization_data
            
        return data


@dataclass
class InferenceResponse:
    """Response from inference call."""
    content: str
    model: str
    provider: str
    metrics: InferenceMetrics
    raw_response: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider,
            "metrics": self.metrics.to_dict(),
            "raw_response": self.raw_response
        }


@dataclass
class StreamChunk:
    """A chunk of streaming response."""
    content: str
    is_final: bool = False
    metrics: Optional[InferenceMetrics] = None


class InferenceProvider(ABC):
    """Abstract base class for inference providers."""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """Initialize provider with API key."""
        self.api_key = api_key
        self.base_url = base_url
        self.provider_name = self.__class__.__name__.replace("Provider", "").lower()
        
    @abstractmethod
    def get_supported_models(self) -> List[str]:
        """Get list of supported models for this provider."""
        pass
    
    @abstractmethod
    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost for the inference based on token usage."""
        pass
    
    @abstractmethod
    async def infer_async(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[InferenceResponse, AsyncGenerator[StreamChunk, None]]:
        """Perform async inference with the given prompt.
        
        Args:
            prompt: The prompt to send
            model: The model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional provider-specific parameters
            
        Returns:
            InferenceResponse if stream=False, AsyncGenerator[StreamChunk] if stream=True
        """
        pass
    
    def infer(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[InferenceResponse, Generator[StreamChunk, None, None]]:
        """Perform synchronous inference with the given prompt."""
        import asyncio
        
        if stream:
            # For streaming, we need to handle it differently
            async def stream_wrapper():
                result = await self.infer_async(prompt, model, temperature, max_tokens, stream=True, **kwargs)
                async for chunk in result:
                    yield chunk
            
            # Convert async generator to sync generator
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                async_gen = stream_wrapper()
                while True:
                    try:
                        chunk = loop.run_until_complete(async_gen.__anext__())
                        yield chunk
                    except StopAsyncIteration:
                        break
            finally:
                loop.close()
        else:
            # Non-streaming case
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    self.infer_async(prompt, model, temperature, max_tokens, stream=False, **kwargs)
                )
            finally:
                loop.close()
    
    def measure_latency(self, start_time: float) -> float:
        """Calculate latency in milliseconds."""
        return (time.time() - start_time) * 1000