#!/usr/bin/env python3
"""
Runtime environment defaults.

This module intentionally performs minimal, non-fatal setup at import time:
- set sensible environment defaults for optional third-party libraries
  without importing them.
- Avoid importing `transformers` or attempting to configure its logging here;
  Transformers logging suppression has been moved into the HuggingFace provider
  so it only runs when the provider (and thus Transformers) is actually used.
"""

import os

# Environment defaults for third‑party libraries (only if not already set)
os.environ.setdefault("TRANSFORMERS_NO_TF_WARNING", "1")
os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")

# Optional Google default location; external env or gcloud config may override
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
