import os
import shutil
import subprocess
from typing import Any

try:
    from google import genai  # type: ignore
    from google.genai.types import HttpOptions  # type: ignore
except Exception:
    genai = None  # type: ignore[assignment]
    HttpOptions = None  # type: ignore[assignment]

from tokker.providers import Provider, register_provider
from tokker import messages


@register_provider
class ProviderGoogle(Provider):
    NAME = "Google"
    MODELS: list[str] = [
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
    ]

    # Local helper
    def __init__(
        self,
        client: Any | None = None,
        name: str = "Google",
        models: list[str] | None = None,
    ):
        self._client = client

    def _get_client(self):  # Local helper
        if self._client is not None:
            return self._client

        if genai is None or HttpOptions is None:
            raise messages.missing_dep_error("google.genai")

        project = (
            os.environ.get("GOOGLE_CLOUD_PROJECT")
            or os.environ.get("GCLOUD_PROJECT")
            or os.environ.get("CLOUD_PROJECT")
            or None
        )
        location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

        if project is None:
            gcloud = shutil.which("gcloud")
            if gcloud:
                try:
                    proc = subprocess.run(
                        [gcloud, "config", "get-value", "project"],
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    candidate = (proc.stdout or "").strip()
                    if candidate and candidate != "(unset)":
                        project = candidate
                except Exception:
                    pass

        # Let any client construction errors bubble raw
        self._client = genai.Client(
            vertexai=True,
            project=project,
            location=location,
            http_options=HttpOptions(api_version="v1"),
        )
        return self._client

    def tokenize(
        self,
        text: str,
        model_name: str,
    ) -> dict[str, str | int | list[str] | list[int]]:
        client = self._get_client()
        response = client.models.compute_tokens(
            model=model_name,
            contents=text,
        )

        token_ids: list[int] = []
        token_strings: list[str] = []

        tokens_info = getattr(response, "tokens_info", None)
        if not tokens_info:
            # Allow downstream handling to decide how to message empty tokens
            raise RuntimeError("Google compute_tokens returned no tokens_info")

        for info in tokens_info:
            token_ids.extend(getattr(info, "token_ids", []) or [])
            for t in getattr(info, "tokens", []) or []:
                if isinstance(t, bytes):
                    try:
                        token_strings.append(t.decode("utf-8", errors="replace"))
                    except Exception:
                        token_strings.append(str(t))
                else:
                    token_strings.append(str(t))

        return {
            "token_strings": token_strings,
            "token_ids": token_ids,
            "token_count": len(token_ids),
        }
