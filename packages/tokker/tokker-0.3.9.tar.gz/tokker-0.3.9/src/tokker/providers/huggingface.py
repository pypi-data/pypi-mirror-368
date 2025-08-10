from typing import Any
from tokker import messages
from tokker.providers import Provider, register_provider


def _import_auto_tokenizer():  # Local helper
    # Lazy import to avoid triggering Transformers' import-time framework warnings
    try:
        from transformers import AutoTokenizer  # type: ignore

        # Suppress Transformers advisory/logging noise as soon as it's imported.
        # Do this in a guarded manner so missing submodules or API changes don't crash.
        try:
            from transformers.utils import logging as hf_logging  # type: ignore

            try:
                hf_logging.set_verbosity_error()
            except Exception:
                # If setting verbosity fails for any reason, ignore and continue.
                pass
        except Exception:
            # If the logging module isn't available, ignore and continue.
            pass

        return AutoTokenizer
    except Exception:
        raise messages.missing_dep_error("transformers")


@register_provider
class ProviderHuggingFace(Provider):
    NAME = "HuggingFace"
    MODELS: list[str] = []

    def __init__(self):  # Local helper
        self._model_cache: dict[str, Any] = {}

    def _get_model(self, model_name: str) -> Any:  # Local helper
        if model_name in self._model_cache:
            return self._model_cache[model_name]
        AutoTokenizer = _import_auto_tokenizer()
        model: Any = AutoTokenizer.from_pretrained(
            model_name,
            use_fast=True,
            trust_remote_code=False,
        )
        if not getattr(model, "is_fast", False):
            model = AutoTokenizer.from_pretrained(
                model_name,
                use_fast=False,
                trust_remote_code=False,
            )
        self._model_cache[model_name] = model
        return model

    def tokenize(
        self,
        text: str,
        model_name: str,
    ) -> dict[str, Any]:
        tok = self._get_model(model_name)
        token_ids = tok.encode(text)
        token_strings: list[str] = []
        for token_id in token_ids:
            try:
                token_strings.append(tok.decode([token_id]))
            except Exception:
                token_strings.append(f"<token_{token_id}>")
        return {
            "token_strings": token_strings,
            "token_ids": token_ids,
            "token_count": len(token_ids),
        }

    def is_on_huggingface(self, model_name: str) -> bool:
        if model_name in {
            "o200k_base",
            "cl100k_base",
            "p50k_base",
            "p50k_edit",
            "r50k_base",
        }:
            return False
        if model_name in self._model_cache:
            return True
        try:
            AutoTokenizer = _import_auto_tokenizer()
        except Exception:
            # transformers not installed -> cannot validate dynamically; treat as unsupported
            return False
        try:
            AutoTokenizer.from_pretrained(
                model_name,
                use_fast=True,
                trust_remote_code=False,
            )
            return True
        except Exception:
            return False
