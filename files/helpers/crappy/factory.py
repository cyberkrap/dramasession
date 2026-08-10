from .config import crappy_provider_name
from .provider import CrappyProvider, CrappyProviderError


def get_crappy_provider() -> CrappyProvider:
    provider = crappy_provider_name()

    if provider == "gemini":
        from .gemini import GeminiCrappyProvider
        return GeminiCrappyProvider()

    raise CrappyProviderError(f"Unsupported Crappy provider: {provider}")
