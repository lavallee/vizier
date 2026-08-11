"""Environment checks for the optional, key-bearing paths.

The computable core needs nothing: no extras, no keys, no network. The
critique path needs the `[critique]` extra (which brings `somm`, vizier's
LLM gateway) and at least one provider key. When either is missing, the
useful thing to print is the one command that fixes it — not a traceback
from three frames deep in an import.

Everything here is import-safe: no optional dependency is imported at
module scope, so `vizier doctor` runs on a bare core install.
"""

from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass
from pathlib import Path

#: Provider keys somm can route on. First entry is what vizier reaches for
#: by default (`vizier critique` synthesizes with gemini-2.5-pro).
PROVIDER_KEYS: tuple[tuple[str, str], ...] = (
    ("GEMINI_API_KEY", "Google Gemini — vizier's default critique model"),
    ("OPENROUTER_API_KEY", "OpenRouter — routes to most models"),
    ("ANTHROPIC_API_KEY", "Anthropic"),
    ("OPENAI_API_KEY", "OpenAI"),
    ("MINIMAX_API_KEY", "MiniMax — also the default vision captioner"),
    ("DEEPSEEK_API_KEY", "DeepSeek"),
)

#: The captioner reads the chart image before the critic reasons about it.
VISION_KEYS = {"minimax_mcp": "MINIMAX_API_KEY"}

_env_loaded = False


def load_env() -> list[Path]:
    """Load `.env` from the working directory upward. Returns what was read.

    Installed packages have no repo root to read a `.env` from, so the
    search starts at the CWD — the project the agent is actually working
    in — and walks up. Real environment variables always win; `.env` only
    fills gaps.
    """
    global _env_loaded
    if _env_loaded:
        return []
    _env_loaded = True
    try:
        from dotenv import load_dotenv
    except ModuleNotFoundError:  # pragma: no cover - python-dotenv is a core dep
        return []
    loaded: list[Path] = []
    here = Path.cwd().resolve()
    for directory in [here, *here.parents]:
        candidate = directory / ".env"
        if candidate.is_file():
            load_dotenv(candidate, override=False)
            loaded.append(candidate)
    return loaded


def has_module(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


def present_provider_keys() -> list[str]:
    load_env()
    return [name for name, _ in PROVIDER_KEYS if os.environ.get(name, "").strip()]


class CritiqueUnavailable(RuntimeError):
    """Raised when the critique path can't run. The message is the fix."""


def require_critique(*, vision_backend: str | None = None) -> None:
    """Assert the critique path can actually run, or explain what's missing."""
    if not has_module("somm"):
        raise CritiqueUnavailable(
            "`vizier critique` needs the critique extra, which is not installed.\n"
            "\n"
            "    pip install 'datavizier[critique]'\n"
            "\n"
            "That pulls in somm — vizier's LLM gateway — plus retrieval. The\n"
            "computable commands (recommend-form, guide, validate, suggest-palette,\n"
            "suggest-ramp, analyze, ink, patterns) need none of it and keep working."
        )

    keys = present_provider_keys()
    if not keys:
        listed = "\n".join(f"      {name:<20} {why}" for name, why in PROVIDER_KEYS)
        raise CritiqueUnavailable(
            "No LLM provider key found, so there is nothing to critique with.\n"
            "\n"
            "Set one in the environment, or put it in a `.env` file in this\n"
            "project (vizier reads `.env` from here upward):\n"
            "\n"
            "    echo 'GEMINI_API_KEY=…' >> .env\n"
            "\n"
            "Keys somm can route on:\n"
            f"{listed}\n"
            "\n"
            "Nothing else in vizier needs a key."
        )

    backend = vision_backend or os.getenv("VIZIER_VISION_BACKEND", "minimax_mcp")
    needed = VISION_KEYS.get(backend)
    if needed and needed not in keys:
        raise CritiqueUnavailable(
            f"The `{backend}` vision backend reads the chart image before the\n"
            f"critic reasons about it, and it needs {needed}.\n"
            "\n"
            f"    echo '{needed}=…' >> .env\n"
            "\n"
            "Or run a local captioner instead: `--vision-backend ollama`\n"
            "(needs ollama serving a vision model), or set VIZIER_VISION_BACKEND."
        )


@dataclass
class Report:
    """What `vizier doctor` found. Serializable; `ok` gates the exit code."""

    version: str
    corpus_root: str
    corpus_packaged: bool
    db_path: str
    items: int
    embeddings: int
    extras: dict[str, bool]
    provider_keys: list[str]
    env_files: list[str]
    problems: list[str]
    notes: list[str]

    @property
    def ok(self) -> bool:
        return not self.problems


def doctor() -> Report:
    """Check every install surface and say which features are live."""
    from . import __version__, storage

    env_files = [str(p) for p in load_env()]
    extras = {
        "search": has_module("fastembed"),
        "critique": has_module("somm"),
        "ingest": has_module("bs4") and has_module("lxml"),
    }
    keys = present_provider_keys()

    problems: list[str] = []
    notes: list[str] = []

    root = storage.corpus_root()
    if not root.is_dir():
        problems.append(
            f"No corpus at {root}. Reinstall datavizier, or point "
            "VIZIER_CORPUS_ROOT at a corpus directory."
        )

    items = embeddings = 0
    try:
        from .db import query as Q

        stats = Q.stats(include_extensions=False)
        items, embeddings = stats["items"], stats["embeddings"]
    except Exception as exc:  # noqa: BLE001 - reported, not raised
        problems.append(f"Could not read the corpus index: {exc}")

    if not problems and items == 0:
        problems.append(
            "The corpus index is empty — form recommendation will return "
            "nothing. Run `vizier db build`."
        )

    if not extras["critique"]:
        notes.append(
            "critique: not installed. `pip install 'datavizier[critique]'` for "
            "`vizier critique` and the eval harness."
        )
    elif not keys:
        notes.append(
            "critique: installed, but no provider key found. Put GEMINI_API_KEY "
            "in a `.env` here (see `vizier doctor` output above for the full list)."
        )
    if not extras["search"]:
        notes.append(
            "search: not installed. `find_similar` (semantic retrieval) is off; "
            "BM25 `search` works. `pip install 'datavizier[search]'`."
        )
    elif embeddings < items:
        notes.append(
            f"search: {items - embeddings} items lack embeddings. "
            "Run `vizier db embed` to enable `find_similar`."
        )

    return Report(
        version=__version__,
        corpus_root=str(root),
        corpus_packaged=storage.is_packaged_corpus(root),
        db_path=str(storage.db_path()),
        items=items,
        embeddings=embeddings,
        extras=extras,
        provider_keys=keys,
        env_files=env_files,
        problems=problems,
        notes=notes,
    )
