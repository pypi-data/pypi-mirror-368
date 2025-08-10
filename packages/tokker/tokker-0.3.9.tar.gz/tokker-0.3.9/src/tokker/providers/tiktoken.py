try:
    import tiktoken  # type: ignore[import-not-found]
except Exception:
    tiktoken = None  # type: ignore[assignment]

from tokker import messages
from tokker.providers import Provider, register_provider


@register_provider
class ProviderTiktoken(Provider):
    NAME = "OpenAI"
    MODELS: list[str] = [
        "o200k_base",
        "cl100k_base",
        "p50k_base",
        "p50k_edit",
        "r50k_base",
    ]

    def _get_encoding(self, model_name: str):
        if tiktoken is None:
            # Surface missing dependency with standardized message from messages.py
            raise messages.missing_dep_error("tiktoken")
        return tiktoken.get_encoding(model_name)

    def tokenize(
        self,
        text: str,
        model_name: str,
    ) -> dict[str, str | int | list[str] | list[int]]:
        encoding = self._get_encoding(model_name)
        token_ids = encoding.encode(text)
        token_strings: list[str] = []
        for token_id in token_ids:
            try:
                token_strings.append(encoding.decode([token_id]))
            except Exception:
                token_strings.append(f"<token_{token_id}>")
        return {
            "token_strings": token_strings,
            "token_ids": token_ids,
            "token_count": len(token_ids),
        }
