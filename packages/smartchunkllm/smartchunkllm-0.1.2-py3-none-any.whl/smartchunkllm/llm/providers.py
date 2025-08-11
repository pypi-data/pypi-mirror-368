"""LLM providers for semantic chunking."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, AsyncIterator
import logging
import asyncio
import json
from dataclasses import dataclass
from enum import Enum
import time
import warnings
warnings.filterwarnings('ignore')

# OpenAI
try:
    import openai
    from openai import OpenAI, AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI not available")

# Anthropic
try:
    import anthropic
    from anthropic import Anthropic, AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logging.warning("Anthropic not available")

# Ollama
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logging.warning("Ollama not available")

# HTTP requests for Ollama API
try:
    import requests
    import aiohttp
    HTTP_AVAILABLE = True
except ImportError:
    HTTP_AVAILABLE = False
    logging.warning("HTTP libraries not available")

from ..core.config import Config, OllamaConfig, OpenAIConfig, AnthropicConfig


class LLMProviderType(Enum):
    """LLM provider types."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


@dataclass
class LLMResponse:
    """LLM response container."""
    content: str
    provider: str
    model: str
    usage: Dict[str, Any]
    metadata: Dict[str, Any]
    processing_time: float
    success: bool
    error: Optional[str] = None


@dataclass
class LLMRequest:
    """LLM request container."""
    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = 0.1
    max_tokens: Optional[int] = None
    stop_sequences: Optional[List[str]] = None
    metadata: Dict[str, Any] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self._client = None
        self._async_client = None
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available."""
        pass
    
    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response synchronously."""
        pass
    
    @abstractmethod
    async def generate_async(self, request: LLMRequest) -> LLMResponse:
        """Generate response asynchronously."""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        pass
    
    def validate_request(self, request: LLMRequest) -> bool:
        """Validate request parameters."""
        if not request.prompt:
            return False
        
        if request.temperature < 0 or request.temperature > 2:
            return False
        
        if request.max_tokens and request.max_tokens <= 0:
            return False
        
        return True


class OpenAIProvider(LLMProvider):
    """OpenAI provider implementation."""
    
    def __init__(self, config: OpenAIConfig):
        super().__init__(config.__dict__)
        self.config = config
        
        if OPENAI_AVAILABLE and config.api_key:
            try:
                self._client = OpenAI(
                    api_key=config.api_key,
                    base_url=config.base_url,
                    timeout=config.timeout
                )
                self._async_client = AsyncOpenAI(
                    api_key=config.api_key,
                    base_url=config.base_url,
                    timeout=config.timeout
                )
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI client: {e}")
    
    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return OPENAI_AVAILABLE and self._client is not None
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using OpenAI."""
        start_time = time.time()
        
        if not self.validate_request(request):
            return LLMResponse(
                content="",
                provider="openai",
                model=self.config.model,
                usage={},
                metadata={},
                processing_time=0,
                success=False,
                error="Invalid request parameters"
            )
        
        try:
            messages = []
            
            if request.system_prompt:
                messages.append({
                    "role": "system",
                    "content": request.system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": request.prompt
            })
            
            response = self._client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens or self.config.max_tokens,
                stop=request.stop_sequences,
                timeout=self.config.timeout
            )
            
            content = response.choices[0].message.content or ""
            
            return LLMResponse(
                content=content,
                provider="openai",
                model=self.config.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "model": response.model
                },
                processing_time=time.time() - start_time,
                success=True
            )
        
        except Exception as e:
            self.logger.error(f"OpenAI generation failed: {e}")
            return LLMResponse(
                content="",
                provider="openai",
                model=self.config.model,
                usage={},
                metadata={},
                processing_time=time.time() - start_time,
                success=False,
                error=str(e)
            )
    
    async def generate_async(self, request: LLMRequest) -> LLMResponse:
        """Generate response asynchronously."""
        start_time = time.time()
        
        if not self.validate_request(request):
            return LLMResponse(
                content="",
                provider="openai",
                model=self.config.model,
                usage={},
                metadata={},
                processing_time=0,
                success=False,
                error="Invalid request parameters"
            )
        
        try:
            messages = []
            
            if request.system_prompt:
                messages.append({
                    "role": "system",
                    "content": request.system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": request.prompt
            })
            
            response = await self._async_client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens or self.config.max_tokens,
                stop=request.stop_sequences,
                timeout=self.config.timeout
            )
            
            content = response.choices[0].message.content or ""
            
            return LLMResponse(
                content=content,
                provider="openai",
                model=self.config.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "model": response.model
                },
                processing_time=time.time() - start_time,
                success=True
            )
        
        except Exception as e:
            self.logger.error(f"OpenAI async generation failed: {e}")
            return LLMResponse(
                content="",
                provider="openai",
                model=self.config.model,
                usage={},
                metadata={},
                processing_time=time.time() - start_time,
                success=False,
                error=str(e)
            )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get OpenAI model information."""
        return {
            "provider": "openai",
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "available": self.is_available()
        }


class AnthropicProvider(LLMProvider):
    """Anthropic provider implementation."""
    
    def __init__(self, config: AnthropicConfig):
        super().__init__(config.__dict__)
        self.config = config
        
        if ANTHROPIC_AVAILABLE and config.api_key:
            try:
                self._client = Anthropic(
                    api_key=config.api_key,
                    timeout=config.timeout
                )
                self._async_client = AsyncAnthropic(
                    api_key=config.api_key,
                    timeout=config.timeout
                )
            except Exception as e:
                self.logger.error(f"Failed to initialize Anthropic client: {e}")
    
    def is_available(self) -> bool:
        """Check if Anthropic is available."""
        return ANTHROPIC_AVAILABLE and self._client is not None
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Anthropic."""
        start_time = time.time()
        
        if not self.validate_request(request):
            return LLMResponse(
                content="",
                provider="anthropic",
                model=self.config.model,
                usage={},
                metadata={},
                processing_time=0,
                success=False,
                error="Invalid request parameters"
            )
        
        try:
            # Combine system prompt and user prompt for Anthropic
            full_prompt = ""
            if request.system_prompt:
                full_prompt = f"System: {request.system_prompt}\n\nHuman: {request.prompt}\n\nAssistant:"
            else:
                full_prompt = f"Human: {request.prompt}\n\nAssistant:"
            
            response = self._client.messages.create(
                model=self.config.model,
                max_tokens=request.max_tokens or self.config.max_tokens,
                temperature=request.temperature,
                system=request.system_prompt or "",
                messages=[
                    {
                        "role": "user",
                        "content": request.prompt
                    }
                ],
                stop_sequences=request.stop_sequences
            )
            
            content = ""
            if response.content:
                content = response.content[0].text if response.content[0].type == "text" else ""
            
            return LLMResponse(
                content=content,
                provider="anthropic",
                model=self.config.model,
                usage={
                    "input_tokens": response.usage.input_tokens if response.usage else 0,
                    "output_tokens": response.usage.output_tokens if response.usage else 0,
                    "total_tokens": (response.usage.input_tokens + response.usage.output_tokens) if response.usage else 0
                },
                metadata={
                    "stop_reason": response.stop_reason,
                    "model": response.model
                },
                processing_time=time.time() - start_time,
                success=True
            )
        
        except Exception as e:
            self.logger.error(f"Anthropic generation failed: {e}")
            return LLMResponse(
                content="",
                provider="anthropic",
                model=self.config.model,
                usage={},
                metadata={},
                processing_time=time.time() - start_time,
                success=False,
                error=str(e)
            )
    
    async def generate_async(self, request: LLMRequest) -> LLMResponse:
        """Generate response asynchronously."""
        start_time = time.time()
        
        if not self.validate_request(request):
            return LLMResponse(
                content="",
                provider="anthropic",
                model=self.config.model,
                usage={},
                metadata={},
                processing_time=0,
                success=False,
                error="Invalid request parameters"
            )
        
        try:
            response = await self._async_client.messages.create(
                model=self.config.model,
                max_tokens=request.max_tokens or self.config.max_tokens,
                temperature=request.temperature,
                system=request.system_prompt or "",
                messages=[
                    {
                        "role": "user",
                        "content": request.prompt
                    }
                ],
                stop_sequences=request.stop_sequences
            )
            
            content = ""
            if response.content:
                content = response.content[0].text if response.content[0].type == "text" else ""
            
            return LLMResponse(
                content=content,
                provider="anthropic",
                model=self.config.model,
                usage={
                    "input_tokens": response.usage.input_tokens if response.usage else 0,
                    "output_tokens": response.usage.output_tokens if response.usage else 0,
                    "total_tokens": (response.usage.input_tokens + response.usage.output_tokens) if response.usage else 0
                },
                metadata={
                    "stop_reason": response.stop_reason,
                    "model": response.model
                },
                processing_time=time.time() - start_time,
                success=True
            )
        
        except Exception as e:
            self.logger.error(f"Anthropic async generation failed: {e}")
            return LLMResponse(
                content="",
                provider="anthropic",
                model=self.config.model,
                usage={},
                metadata={},
                processing_time=time.time() - start_time,
                success=False,
                error=str(e)
            )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Anthropic model information."""
        return {
            "provider": "anthropic",
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "available": self.is_available()
        }


class OllamaProvider(LLMProvider):
    """Ollama provider implementation."""
    
    def __init__(self, config: OllamaConfig):
        super().__init__(config.__dict__)
        self.config = config
        self.base_url = f"{config.host}:{config.port}"
        
        # Initialize Ollama client if available
        if OLLAMA_AVAILABLE:
            try:
                self._client = ollama.Client(host=self.base_url)
            except Exception as e:
                self.logger.error(f"Failed to initialize Ollama client: {e}")
    
    def is_available(self) -> bool:
        """Check if Ollama is available."""
        if not OLLAMA_AVAILABLE and not HTTP_AVAILABLE:
            return False
        
        try:
            # Test connection
            if OLLAMA_AVAILABLE and self._client:
                models = self._client.list()
                return True
            elif HTTP_AVAILABLE:
                response = requests.get(f"http://{self.base_url}/api/tags", timeout=5)
                return response.status_code == 200
        except Exception as e:
            self.logger.debug(f"Ollama not available: {e}")
        
        return False
    
    def ensure_model(self) -> bool:
        """Ensure model is available, pull if necessary."""
        try:
            if OLLAMA_AVAILABLE and self._client:
                # Check if model exists
                models = self._client.list()
                model_names = [model['name'] for model in models.get('models', [])]
                
                if self.config.model not in model_names:
                    self.logger.info(f"Pulling model {self.config.model}...")
                    self._client.pull(self.config.model)
                    return True
                
                return True
            
            elif HTTP_AVAILABLE:
                # Use HTTP API to check and pull model
                response = requests.get(f"http://{self.base_url}/api/tags")
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    model_names = [model['name'] for model in models]
                    
                    if self.config.model not in model_names:
                        self.logger.info(f"Pulling model {self.config.model}...")
                        pull_response = requests.post(
                            f"http://{self.base_url}/api/pull",
                            json={"name": self.config.model}
                        )
                        return pull_response.status_code == 200
                    
                    return True
        
        except Exception as e:
            self.logger.error(f"Failed to ensure model: {e}")
        
        return False
    
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Ollama."""
        start_time = time.time()
        
        if not self.validate_request(request):
            return LLMResponse(
                content="",
                provider="ollama",
                model=self.config.model,
                usage={},
                metadata={},
                processing_time=0,
                success=False,
                error="Invalid request parameters"
            )
        
        # Ensure model is available
        if not self.ensure_model():
            return LLMResponse(
                content="",
                provider="ollama",
                model=self.config.model,
                usage={},
                metadata={},
                processing_time=time.time() - start_time,
                success=False,
                error="Model not available"
            )
        
        try:
            # Prepare prompt
            full_prompt = request.prompt
            if request.system_prompt:
                full_prompt = f"System: {request.system_prompt}\n\nUser: {request.prompt}"
            
            if OLLAMA_AVAILABLE and self._client:
                response = self._client.generate(
                    model=self.config.model,
                    prompt=full_prompt,
                    options={
                        "temperature": request.temperature,
                        "num_predict": request.max_tokens or self.config.max_tokens,
                        "stop": request.stop_sequences or []
                    }
                )
                
                content = response.get('response', '')
                
                return LLMResponse(
                    content=content,
                    provider="ollama",
                    model=self.config.model,
                    usage={
                        "prompt_tokens": response.get('prompt_eval_count', 0),
                        "completion_tokens": response.get('eval_count', 0),
                        "total_tokens": response.get('prompt_eval_count', 0) + response.get('eval_count', 0)
                    },
                    metadata={
                        "eval_duration": response.get('eval_duration', 0),
                        "load_duration": response.get('load_duration', 0)
                    },
                    processing_time=time.time() - start_time,
                    success=True
                )
            
            elif HTTP_AVAILABLE:
                # Use HTTP API
                payload = {
                    "model": self.config.model,
                    "prompt": full_prompt,
                    "options": {
                        "temperature": request.temperature,
                        "num_predict": request.max_tokens or self.config.max_tokens
                    },
                    "stream": False
                }
                
                response = requests.post(
                    f"http://{self.base_url}/api/generate",
                    json=payload,
                    timeout=self.config.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get('response', '')
                    
                    return LLMResponse(
                        content=content,
                        provider="ollama",
                        model=self.config.model,
                        usage={
                            "prompt_tokens": result.get('prompt_eval_count', 0),
                            "completion_tokens": result.get('eval_count', 0),
                            "total_tokens": result.get('prompt_eval_count', 0) + result.get('eval_count', 0)
                        },
                        metadata={
                            "eval_duration": result.get('eval_duration', 0),
                            "load_duration": result.get('load_duration', 0)
                        },
                        processing_time=time.time() - start_time,
                        success=True
                    )
                else:
                    raise Exception(f"HTTP {response.status_code}: {response.text}")
        
        except Exception as e:
            self.logger.error(f"Ollama generation failed: {e}")
            return LLMResponse(
                content="",
                provider="ollama",
                model=self.config.model,
                usage={},
                metadata={},
                processing_time=time.time() - start_time,
                success=False,
                error=str(e)
            )
    
    async def generate_async(self, request: LLMRequest) -> LLMResponse:
        """Generate response asynchronously."""
        start_time = time.time()
        
        if not self.validate_request(request):
            return LLMResponse(
                content="",
                provider="ollama",
                model=self.config.model,
                usage={},
                metadata={},
                processing_time=0,
                success=False,
                error="Invalid request parameters"
            )
        
        try:
            # For now, use sync version in thread pool
            # TODO: Implement proper async Ollama client
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.generate, request)
            return response
        
        except Exception as e:
            self.logger.error(f"Ollama async generation failed: {e}")
            return LLMResponse(
                content="",
                provider="ollama",
                model=self.config.model,
                usage={},
                metadata={},
                processing_time=time.time() - start_time,
                success=False,
                error=str(e)
            )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Ollama model information."""
        info = {
            "provider": "ollama",
            "model": self.config.model,
            "host": self.config.host,
            "port": self.config.port,
            "available": self.is_available()
        }
        
        try:
            if OLLAMA_AVAILABLE and self._client:
                models = self._client.list()
                model_list = models.get('models', [])
                current_model = next((m for m in model_list if m['name'] == self.config.model), None)
                if current_model:
                    info.update({
                        "size": current_model.get('size', 0),
                        "modified_at": current_model.get('modified_at', '')
                    })
        except Exception as e:
            self.logger.debug(f"Could not get model info: {e}")
        
        return info


class LLMManager:
    """Manager for multiple LLM providers with fallback support."""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.providers: Dict[str, LLMProvider] = {}
        
        # Initialize providers
        self._initialize_providers()
        
        # Set primary provider
        self.primary_provider = config.llm.primary_provider
        self.fallback_providers = config.llm.fallback_providers or []
    
    def _initialize_providers(self):
        """Initialize all configured providers."""
        config = self.config
        
        # OpenAI
        if config.openai.api_key:
            try:
                self.providers['openai'] = OpenAIProvider(config.openai)
                self.logger.info("OpenAI provider initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI: {e}")
        
        # Anthropic
        if config.anthropic.api_key:
            try:
                self.providers['anthropic'] = AnthropicProvider(config.anthropic)
                self.logger.info("Anthropic provider initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Anthropic: {e}")
        
        # Ollama
        try:
            self.providers['ollama'] = OllamaProvider(config.ollama)
            if self.providers['ollama'].is_available():
                self.logger.info("Ollama provider initialized")
            else:
                self.logger.warning("Ollama provider initialized but not available")
        except Exception as e:
            self.logger.error(f"Failed to initialize Ollama: {e}")
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return [name for name, provider in self.providers.items() if provider.is_available()]
    
    def get_provider(self, provider_name: str) -> Optional[LLMProvider]:
        """Get specific provider."""
        return self.providers.get(provider_name)
    
    def generate(self, request: LLMRequest, provider_name: Optional[str] = None) -> LLMResponse:
        """Generate response with fallback support."""
        # Determine provider order
        providers_to_try = []
        
        if provider_name:
            providers_to_try.append(provider_name)
        else:
            providers_to_try.append(self.primary_provider)
            providers_to_try.extend(self.fallback_providers)
        
        # Remove duplicates while preserving order
        seen = set()
        providers_to_try = [p for p in providers_to_try if not (p in seen or seen.add(p))]
        
        last_error = None
        
        for provider_name in providers_to_try:
            provider = self.providers.get(provider_name)
            
            if not provider or not provider.is_available():
                self.logger.warning(f"Provider {provider_name} not available")
                continue
            
            try:
                self.logger.debug(f"Trying provider: {provider_name}")
                response = provider.generate(request)
                
                if response.success:
                    self.logger.debug(f"Success with provider: {provider_name}")
                    return response
                else:
                    last_error = response.error
                    self.logger.warning(f"Provider {provider_name} failed: {response.error}")
            
            except Exception as e:
                last_error = str(e)
                self.logger.error(f"Provider {provider_name} error: {e}")
        
        # All providers failed
        return LLMResponse(
            content="",
            provider="none",
            model="none",
            usage={},
            metadata={},
            processing_time=0,
            success=False,
            error=f"All providers failed. Last error: {last_error}"
        )
    
    async def generate_async(self, request: LLMRequest, provider_name: Optional[str] = None) -> LLMResponse:
        """Generate response asynchronously with fallback support."""
        # Determine provider order
        providers_to_try = []
        
        if provider_name:
            providers_to_try.append(provider_name)
        else:
            providers_to_try.append(self.primary_provider)
            providers_to_try.extend(self.fallback_providers)
        
        # Remove duplicates while preserving order
        seen = set()
        providers_to_try = [p for p in providers_to_try if not (p in seen or seen.add(p))]
        
        last_error = None
        
        for provider_name in providers_to_try:
            provider = self.providers.get(provider_name)
            
            if not provider or not provider.is_available():
                self.logger.warning(f"Provider {provider_name} not available")
                continue
            
            try:
                self.logger.debug(f"Trying provider: {provider_name}")
                response = await provider.generate_async(request)
                
                if response.success:
                    self.logger.debug(f"Success with provider: {provider_name}")
                    return response
                else:
                    last_error = response.error
                    self.logger.warning(f"Provider {provider_name} failed: {response.error}")
            
            except Exception as e:
                last_error = str(e)
                self.logger.error(f"Provider {provider_name} error: {e}")
        
        # All providers failed
        return LLMResponse(
            content="",
            provider="none",
            model="none",
            usage={},
            metadata={},
            processing_time=0,
            success=False,
            error=f"All providers failed. Last error: {last_error}"
        )
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers."""
        status = {}
        
        for name, provider in self.providers.items():
            try:
                status[name] = {
                    "available": provider.is_available(),
                    "model_info": provider.get_model_info()
                }
            except Exception as e:
                status[name] = {
                    "available": False,
                    "error": str(e)
                }
        
        return status