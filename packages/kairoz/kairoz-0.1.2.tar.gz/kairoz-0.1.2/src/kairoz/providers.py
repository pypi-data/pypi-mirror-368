from typing import Optional

from .openai import ProviderConfig

"""
Predefined provider configurations for popular OpenAI-compatible services.
Based on the AI SDK documentation: https://ai-sdk.dev/providers/ai-sdk-providers
"""


class Providers:
    """Predefined provider configurations."""

    @staticmethod
    def openai(api_key: str, organization: Optional[str] = None) -> ProviderConfig:
        """OpenAI (original) configuration."""
        return ProviderConfig(
            api_key=api_key,
            base_url="https://api.openai.com/v1",
            organization=organization,
        )

    @staticmethod
    def azure_openai(api_key: str, endpoint: str) -> ProviderConfig:
        """Azure OpenAI configuration."""
        return ProviderConfig(
            api_key=api_key,
            base_url=f"{endpoint}/openai/deployments",
        )

    @staticmethod
    def anthropic(api_key: str) -> ProviderConfig:
        """Anthropic (Claude) configuration."""
        return ProviderConfig(
            api_key=api_key,
            base_url="https://api.anthropic.com/v1",
        )

    @staticmethod
    def groq(api_key: str) -> ProviderConfig:
        """Groq configuration."""
        return ProviderConfig(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )

    @staticmethod
    def deepinfra(api_key: str) -> ProviderConfig:
        """DeepInfra configuration."""
        return ProviderConfig(
            api_key=api_key,
            base_url="https://api.deepinfra.com/v1/openai",
        )

    @staticmethod
    def mistral(api_key: str) -> ProviderConfig:
        """Mistral AI configuration."""
        return ProviderConfig(
            api_key=api_key,
            base_url="https://api.mistral.ai/v1",
        )

    @staticmethod
    def together(api_key: str) -> ProviderConfig:
        """Together.ai configuration."""
        return ProviderConfig(
            api_key=api_key,
            base_url="https://api.together.xyz/v1",
        )

    @staticmethod
    def cohere(api_key: str) -> ProviderConfig:
        """Cohere configuration."""
        return ProviderConfig(
            api_key=api_key,
            base_url="https://api.cohere.ai/v1",
        )

    @staticmethod
    def fireworks(api_key: str) -> ProviderConfig:
        """Fireworks configuration."""
        return ProviderConfig(
            api_key=api_key,
            base_url="https://api.fireworks.ai/inference/v1",
        )

    @staticmethod
    def deepseek(api_key: str) -> ProviderConfig:
        """DeepSeek configuration."""
        return ProviderConfig(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1",
        )

    @staticmethod
    def cerebras(api_key: str) -> ProviderConfig:
        """Cerebras configuration."""
        return ProviderConfig(
            api_key=api_key,
            base_url="https://api.cerebras.ai/v1",
        )

    @staticmethod
    def google_generative_ai(api_key: str) -> ProviderConfig:
        """Google Generative AI configuration."""
        return ProviderConfig(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta",
        )

    @staticmethod
    def google_vertex_ai(
        api_key: str, project_id: str, location: str = "us-central1"
    ) -> ProviderConfig:
        """Google Vertex AI configuration."""
        return ProviderConfig(
            api_key=api_key,
            base_url=f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}",
        )

    @staticmethod
    def lm_studio(
        api_key: str, base_url: str = "http://localhost:1234/v1"
    ) -> ProviderConfig:
        """LM Studio configuration."""
        return ProviderConfig(
            api_key=api_key,
            base_url=base_url,
        )

    @staticmethod
    def nvidia_nim(api_key: str, base_url: str) -> ProviderConfig:
        """NVIDIA NIM configuration."""
        return ProviderConfig(
            api_key=api_key,
            base_url=base_url,
        )

    @staticmethod
    def baseten(api_key: str) -> ProviderConfig:
        """Baseten configuration."""
        return ProviderConfig(
            api_key=api_key,
            base_url="https://api.baseten.co/v1",
        )

    @staticmethod
    def openrouter(api_key: str) -> ProviderConfig:
        """OpenRouter configuration."""
        return ProviderConfig(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    @staticmethod
    def cloudflare_workers_ai(api_key: str) -> ProviderConfig:
        """Cloudflare Workers AI configuration."""
        return ProviderConfig(
            api_key=api_key,
            base_url="https://api.cloudflare.com/client/v4/ai",
        )

    @staticmethod
    def perplexity(api_key: str) -> ProviderConfig:
        """Perplexity configuration."""
        return ProviderConfig(
            api_key=api_key,
            base_url="https://api.perplexity.ai",
        )

    @staticmethod
    def luma_ai(api_key: str) -> ProviderConfig:
        """Luma AI configuration."""
        return ProviderConfig(
            api_key=api_key,
            base_url="https://api.lumalabs.ai/v1",
        )
