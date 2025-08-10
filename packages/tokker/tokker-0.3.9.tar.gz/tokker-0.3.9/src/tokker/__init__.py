# Package top-level kept intentionally minimal to avoid heavy imports on `import tokker`.
# Public API functions live in `tokker.api`. This module intentionally exposes only
# a package version to keep import-time side effects minimal for CLI and programmatic use.
#
# Breaking change: `from tokker import tokenize` no longer works. Use:
#   from tokker.api import tokenize
#
__version__ = "0.3.9"

# Do not export API symbols at package import time.
__all__ = []
