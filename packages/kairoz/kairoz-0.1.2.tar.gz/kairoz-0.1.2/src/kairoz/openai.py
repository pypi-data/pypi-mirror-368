import logging
from typing import Any, Dict, Optional

from openai import OpenAI
from openai.types.chat import ChatCompletion
from openai.types.completion import Completion
from openai.types.embedding import Embedding


class ProviderConfig:
    """Configuration for an OpenAI-compatible provider."""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        organization: Optional[str] = None,
        project: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.organization = organization
        self.project = project
        self.headers = headers or {}


class KairozOpenAI:
    """
    Kairoz OpenAI wrapper with automatic fallback to secondary provider.

    Automatically switches to fallback provider when primary provider
    returns server errors (>500 status codes).
    """

    def __init__(
        self,
        primary: ProviderConfig,
        fallback: Optional[ProviderConfig] = None,
        max_retries: int = 3,
        retry_delay: int = 1000,
        enable_logging: bool = False,
    ):
        self.primary = primary
        self.fallback = fallback
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.enable_logging = enable_logging

        # Initialize primary client
        self.primary_client = OpenAI(
            api_key=primary.api_key,
            base_url=primary.base_url,
            organization=primary.organization,
            project=primary.project,
            default_headers=primary.headers,
        )

        # Initialize fallback client if provided
        self.fallback_client = None
        if fallback:
            self.fallback_client = OpenAI(
                api_key=fallback.api_key,
                base_url=fallback.base_url,
                organization=fallback.organization,
                project=fallback.project,
                default_headers=fallback.headers,
            )

        # Setup logging
        if enable_logging:
            logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _log(self, message: str) -> None:
        """Log message if logging is enabled."""
        if self.enable_logging:
            self.logger.info(f"[KairozOpenAI] {message}")

    def _should_use_fallback(self, error: Exception) -> bool:
        """Check if we should use fallback for this error."""
        # Don't use fallback for client errors (4xx) except rate limits and auth issues
        if hasattr(error, "status_code") and 400 <= error.status_code < 500:
            # Use fallback for rate limits and auth issues
            if error.status_code in [429, 401, 403]:
                return True
            # Don't use fallback for other 4xx errors (400, 404, 422, etc.)
            return False

        # Use fallback for all server errors (5xx)
        if hasattr(error, "status_code") and error.status_code >= 500:
            return True

        # Check for OpenAI API error types that should trigger fallback
        if hasattr(error, "error") and hasattr(error.error, "type"):
            fallback_error_types = [
                "server_error",
                "internal_error",
                "rate_limit_error",
                "service_unavailable",
                "invalid_api_key",
                "quota_exceeded",
                "billing_not_active",
                "insufficient_quota",
                "model_not_found",  # Some providers might not have the same models
                "context_length_exceeded",  # Model-specific limits
            ]
            return error.error.type in fallback_error_types

        # Check for specific error messages that indicate provider issues
        if hasattr(error, "message"):
            fallback_error_messages = [
                "rate limit",
                "quota exceeded",
                "billing",
                "api key",
                "authentication",
                "server error",
                "internal error",
                "service unavailable",
                "timeout",
                "connection",
            ]

            error_message = error.message.lower()
            return any(msg in error_message for msg in fallback_error_messages)

        return False

    def _execute_with_fallback(
        self, operation: callable, operation_name: str, **kwargs
    ) -> Any:
        """Execute operation with automatic fallback to secondary provider."""
        last_error = None

        # Try primary client first
        try:
            self._log(f"Attempting {operation_name} with primary provider")
            # Remove model_fallback from kwargs before calling the client
            client_kwargs = {k: v for k, v in kwargs.items() if k != "model_fallback"}
            return operation(self.primary_client, **client_kwargs)
        except Exception as error:
            last_error = error
            self._log(f"Primary provider failed: {error}")

            # Check if we should use fallback and we have a fallback
            if self.fallback_client and self._should_use_fallback(error):
                self._log(f"Switching to fallback provider for {operation_name}")

                # If we have a model_fallback specified, use it for the fallback provider
                fallback_kwargs = kwargs.copy()
                if "model_fallback" in kwargs and "model" in kwargs:
                    fallback_kwargs["model"] = kwargs["model_fallback"]
                    self._log(
                        f"Using fallback model: {kwargs['model_fallback']} instead of {kwargs['model']}"
                    )

                # Remove model_fallback from fallback kwargs before calling the client
                fallback_client_kwargs = {
                    k: v for k, v in fallback_kwargs.items() if k != "model_fallback"
                }

                try:
                    return operation(self.fallback_client, **fallback_client_kwargs)
                except Exception as fallback_error:
                    self._log(f"Fallback provider also failed: {fallback_error}")
                    raise fallback_error

            raise last_error

    @property
    def chat(self):
        """Chat completions interface."""
        return ChatCompletions(self)

    @property
    def completions(self):
        """Legacy completions interface."""
        return Completions(self)

    @property
    def embeddings(self):
        """Embeddings interface."""
        return Embeddings(self)


class ChatCompletions:
    """Chat completions wrapper."""

    def __init__(self, client: KairozOpenAI):
        self.client = client

    @property
    def completions(self):
        """Return self to support the chat.completions.create pattern."""
        return self

    def create(self, **kwargs) -> ChatCompletion:
        """Create a chat completion."""

        def operation(client, **params):
            return client.chat.completions.create(**params)

        return self.client._execute_with_fallback(
            operation, "chat.completions.create", **kwargs
        )


class Completions:
    """Legacy completions wrapper."""

    def __init__(self, client: KairozOpenAI):
        self.client = client

    def create(self, **kwargs) -> Completion:
        """Create a completion."""

        def operation(client, **params):
            return client.completions.create(**params)

        return self.client._execute_with_fallback(
            operation, "completions.create", **kwargs
        )


class Embeddings:
    """Embeddings wrapper."""

    def __init__(self, client: KairozOpenAI):
        self.client = client

    def create(self, **kwargs) -> Embedding:
        """Create embeddings."""

        def operation(client, **params):
            return client.embeddings.create(**params)

        return self.client._execute_with_fallback(
            operation, "embeddings.create", **kwargs
        )


# TODO: Implement remaining OpenAI SDK methods
# - models.list()
# - models.retrieve()
# - files.* (all file operations)
# - fine_tuning.* (all fine-tuning operations)
# - images.* (all image generation operations)
# - audio.* (all audio operations)
# - moderations.create()
# - beta.assistants.* (all assistant operations)
# - beta.threads.* (all thread operations)
# - beta.vector_stores.* (all vector store operations)
# - beta.tools.* (all tool operations)
