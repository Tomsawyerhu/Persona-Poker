import os
import time
import yaml
import random
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, Union, List
from openai import APIError, APIConnectionError, APITimeoutError, RateLimitError, OpenAI

from pydantic import BaseModel, Field, model_validator, ConfigDict

DEFAULT_LLM_PROFILE_PATH = Path("configs/profiles.yaml")


class LLMConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_default=True)

    api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key (defaults to OPENAI_API_KEY environment variable)"
    )
    base_url: Optional[str] = Field(
        default=None,
        description="Custom API base URL for OpenAI-compatible endpoints"
    )
    model: str = Field(default="gpt-4o-mini", description="Model name to use")
    temperature: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="Sampling temperature (omit by default; excluded for o-series)"
    )
    max_tokens: Optional[int] = Field(
        default=None,
        gt=0,
        description="Maximum number of tokens to generate (omit by default)"
    )
    timeout: int = Field(default=60, gt=0, description="API request timeout in seconds")
    max_retries: int = Field(default=30, ge=0, description="Maximum retry attempts")
    retry_base_delay: float = Field(default=1.0, description="Base retry delay in seconds")
    retry_jitter: float = Field(default=0.1, description="Retry delay jitter factor")
    track_costs: bool = Field(default=True, description="Enable cost tracking")

    @classmethod
    def from_profile(cls, profile: str = "default", config_path: Path = DEFAULT_LLM_PROFILE_PATH) -> "LLMConfig":
        try:
            with config_path.open("r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            profile_config = config.get("models", {}).get(profile, {})

            return cls(**{
                k: v for k, v in profile_config.items()
                if v is not None and k in cls.model_fields
            })

        except Exception as e:
            return cls()

    @model_validator(mode="after")
    def resolve_api_key(self) -> "LLMConfig":
        if not self.api_key:
            self.api_key = os.environ.get("OPENAI_API_KEY")
        return self


class LLMClient(BaseModel):
    config: LLMConfig = Field(default_factory=LLMConfig)
    client: Optional[OpenAI] = Field(default=None, exclude=True)
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, profile_or_config: Union[str, Dict[str, Any]] = "default", profile_path: Optional[str] = None,
                 **kwargs):
        if isinstance(profile_or_config, str):
            config = self._load_profile_config(profile_or_config, profile_path)
            config.update({k: v for k, v in kwargs.items() if k in LLMConfig.model_fields})
            super().__init__(config=LLMConfig(**config))
        else:
            config_kwargs = profile_or_config if isinstance(profile_or_config, dict) else {}
            config_kwargs.update({k: v for k, v in kwargs.items() if k in LLMConfig.model_fields})
            super().__init__(config=LLMConfig(**config_kwargs))

        self._initialize_client()

    def _load_profile_config(self, profile: str, profile_path: Optional[str]) -> Dict[str, Any]:
        try:
            config_path = DEFAULT_LLM_PROFILE_PATH
            if profile_path is not None:
                config_path = profile_path
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            if profile in config.get("models", {}):
                return config["models"][profile]
            elif profile in config.get("llm_pool", {}):
                pool_config = config["llm_pool"][profile]
                return {k: v for k, v in pool_config.items() if k in LLMConfig.model_fields}
            else:
                return {}

        except Exception as e:
            return {}

    def _initialize_client(self) -> None:
        if not self.config.api_key:
            self.config.api_key = os.environ.get("OPENAI_API_KEY")
            if not self.config.api_key:
                raise ValueError("Missing required API key. Set OPENAI_API_KEY environment variable.")

        client_args = {
            "api_key": self.config.api_key,
            "timeout": self.config.timeout
        }

        if self.config.base_url:
            client_args["base_url"] = self.config.base_url

        self.client = OpenAI(**client_args)

    def __call__(
            self,
            prompt: str,
            system_prompt: Optional[str] = None,
            tools: Optional[list] = None,
            **generation_args
    ):
        messages = self._build_messages(prompt, system_prompt)
        params = self._prepare_params(messages, generation_args, tools)

        response = self._retry_api_call(params)
        return response

    def _build_messages(self, prompt: str, system_prompt: Optional[str]) -> List[Dict[str, str]]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages

    def _prepare_params(
            self,
            messages: list[Dict[str, str]],
            generation_args: Dict[str, Any],
            tools: Optional[list]
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
        }
        if tools is not None:
            params['tools'] = tools

        model_name = (self.config.model or "").lower()
        is_o_series = model_name.startswith("o")

        if (self.config.temperature is not None) and (not is_o_series):
            params["temperature"] = self.config.temperature

        if self.config.max_tokens is not None:
            params["max_tokens"] = self.config.max_tokens

        safe_generation_args = dict(generation_args) if generation_args else {}
        if is_o_series:
            safe_generation_args.pop("temperature", None)

        params.update(safe_generation_args)
        return params

    def _retry_api_call(self, params: Dict[str, Any]) -> Any:
        for attempt in range(self.config.max_retries + 1):
            try:
                return self.client.chat.completions.create(**params)
            except (APIError, APIConnectionError, APITimeoutError, RateLimitError) as e:
                if attempt == self.config.max_retries:
                    raise
                backoff_time = self._calculate_backoff(
                    attempt,
                    self.config.retry_base_delay,
                    self.config.timeout
                )
                time.sleep(backoff_time)

    def _calculate_backoff(self, attempt: int, base: float, max_wait: float) -> float:
        delay = base * (2 ** attempt)
        jitter = delay * self.config.retry_jitter * random.uniform(-1, 1)
        return min(delay + jitter, max_wait)


def create_llm_instance(model_name: str, model_config: str) -> LLMClient:
    return LLMClient(profile_or_config=model_name,profile_path=model_config)
