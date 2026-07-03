"""Vision captioner for vizier — pluggable backends.

Produces a faithful text description of a data-viz artifact screenshot,
which the text-only critique pipeline reads as an *imperfect witness*
(not ground truth).

## Backends

- **`minimax_mcp`** (default): MiniMax `understand_image` tool via
  `uvx minimax-coding-plan-mcp`. Uses the user's MiniMax Token Plan;
  ~25s per image; reads numeric values from charts (OCR-grade) and
  picks up annotations/labels reliably. Requires `MINIMAX_API_KEY`
  in env. **Switched to default** after a head-to-head on the NJ-
  schools project: minimax produces a strict superset of useful
  catches and roughly doubles the actionable-recommendation rate
  (the ollama caption hallucinates legends, projections, and color
  treatments that aren't there, leading the critique LLM to solve
  problems that don't exist).
- **`ollama`**: local via ollama HTTP, model `qwen2.5vl:7b`. Free,
  offline, moderate speed (148s/page on 3060, 893s on M1 Pro),
  describes chart structure but rarely reads exact values. Kept as
  the offline fallback. Set `VIZIER_VISION_BACKEND=ollama` to opt in.

Both backends produce plain text that's written to the same cache
layout so you can A/B different backends on identical images.

## Caching

Keyed on `sha256(image_bytes) + backend + model + PROMPT_VERSION`.
Same image + same backend = instant re-serve. A backend swap or
prompt-version bump invalidates cleanly without a manual purge.

    evals/captions/
      <sha>.<backend>.<model>.<version>.md

Each file has frontmatter (model, backend, prompt_version,
duration_s, source_path, image_bytes, cached_at) and the caption body.

## Why this bypasses somm

somm's `SommRequest` is shaped around chat completions. MCP tool calls
and ollama-native vision don't fit that surface cleanly. Once somm
grows a general MCP-client utility, the plumbing here can lift up;
the captioner concept stays in vizier.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import frontmatter
import httpx

# Default backend. minimax_mcp wins on numeric-value reading and
# annotation recognition (~25s/image vs ollama's ~2 min on M1 Pro);
# the gap is large enough that critique recommendations downstream are
# materially more actionable. ollama remains the offline fallback for
# anyone without a MiniMax key. Override with VIZIER_VISION_BACKEND.
DEFAULT_BACKEND = os.getenv("VIZIER_VISION_BACKEND", "minimax_mcp")

# Per-backend default "model" label. For MCP this is a pseudo-id because
# MiniMax doesn't disclose the underlying model.
DEFAULT_MODELS = {
    "ollama": "qwen2.5vl:7b",
    "minimax_mcp": "understand-image",
}

DEFAULT_MAX_TOKENS = 2000
PROMPT_VERSION = "v1-2026-04-20"

# Captioner prompt. Kept intentionally narrow: describe, don't critique.
# The critique pipeline wraps this output with its own rubric framing.
CAPTION_PROMPT = """\
You are describing a data visualization for someone who cannot see it. \
Produce a faithful, concrete description of the artifact. Work only \
from what's actually in the image.

Cover each chart or figure on the page:
- chart type / form
- what's encoded on each axis or in each visual channel (color, size, \
position, angle, length)
- any numeric values, labels, or annotations you can actually read \
— quote them verbatim where possible
- whether axes start at zero; whether there are error bars, MOE \
whiskers, or other uncertainty marks; whether any visual framing \
choice (axis truncation, color loading, title rhetoric) might \
mislead a reader

Also note:
- the page's headline or title if visible
- the overall layout (hero, navigation, multi-panel, scrollytelling)
- sources, credits, or methodology notes you can see

Ground rules:
- Describe, don't interpret the journalism.
- If you can't read something, say so — don't guess.
- Don't editorialize from rhetorical titles ("Soars!", "Crisis").
- If a chart form is deceptive by construction (truncated y, misleading \
encoding, double-encoding conflict), name the deception mechanism \
factually — that's part of the description, not critique.
"""


CACHE_DIR = Path(__file__).resolve().parents[2] / "evals" / "captions"


@dataclass
class Caption:
    """One captioning result — what we cache and hand to the critic."""

    text: str
    sha: str
    backend: str
    model: str
    prompt_version: str
    duration_s: float
    image_bytes: int
    source_path: str
    cached: bool  # True if we served from cache, False if we just produced it


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()[:32]


def _cache_path(sha: str, backend: str, model: str) -> Path:
    """Cache key embeds backend + model + prompt version so a backend
    swap, a model bump, or a prompt tweak invalidates cleanly. Keeps
    different-backend captions for the same image side-by-side on disk
    (supports A/B).
    """
    safe_backend = backend.replace("/", "_").replace(":", "-")
    safe_model = model.replace("/", "_").replace(":", "-")
    return CACHE_DIR / f"{sha}.{safe_backend}.{safe_model}.{PROMPT_VERSION}.md"


def _load_cached(cache_path: Path) -> Caption | None:
    if not cache_path.exists():
        return None
    post = frontmatter.load(str(cache_path))
    meta = post.metadata
    return Caption(
        text=post.content.strip(),
        sha=meta.get("sha", ""),
        backend=meta.get("backend", "ollama"),  # default for legacy caches
        model=meta.get("model", ""),
        prompt_version=meta.get("prompt_version", ""),
        duration_s=float(meta.get("duration_s", 0) or 0),
        image_bytes=int(meta.get("image_bytes", 0) or 0),
        source_path=meta.get("source_path", ""),
        cached=True,
    )


def _store_caption(cache_path: Path, cap: Caption, prompt: str) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    post = frontmatter.Post(
        cap.text,
        sha=cap.sha,
        backend=cap.backend,
        model=cap.model,
        prompt_version=cap.prompt_version,
        duration_s=round(cap.duration_s, 2),
        image_bytes=cap.image_bytes,
        source_path=cap.source_path,
        cached_at=datetime.now(timezone.utc).isoformat(),
        prompt_hash=hashlib.sha1(prompt.encode()).hexdigest()[:12],
    )
    cache_path.write_text(frontmatter.dumps(post) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Backends


def _call_ollama_stream(
    image_bytes: bytes,
    *,
    model: str,
    prompt: str,
    max_tokens: int,
    ollama_url: str,
    timeout: float | None,
) -> str:
    """Call ollama's /api/generate with streaming; return assembled text.

    Stream so we don't hit httpx's read timeout on long vision-model
    inferences. Ollama yields JSON frames per token.
    """
    img_b64 = base64.b64encode(image_bytes).decode()
    chunks: list[str] = []
    with httpx.stream(
        "POST",
        f"{ollama_url.rstrip('/')}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "images": [img_b64],
            "stream": True,
            "options": {"temperature": 0.2, "num_predict": max_tokens},
        },
        timeout=timeout,
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if not line:
                continue
            obj = json.loads(line)
            piece = obj.get("response", "")
            if piece:
                chunks.append(piece)
            if obj.get("done"):
                break
    return "".join(chunks).strip()


def _call_minimax_mcp(
    image_path: str,
    *,
    prompt: str,
    api_key: str,
    api_host: str = "https://api.minimax.io",
    timeout: float = 300.0,
) -> str:
    """Call MiniMax's `understand_image` tool via stdio MCP.

    Spawns `uvx minimax-coding-plan-mcp`, initializes the session, invokes
    the tool with the image path (the tool accepts both HTTP URLs and
    local paths), returns the concatenated text content blocks.
    """
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    async def _run() -> str:
        params = StdioServerParameters(
            command="uvx",
            args=["minimax-coding-plan-mcp"],
            env={
                "MINIMAX_API_KEY": api_key,
                "MINIMAX_API_HOST": api_host,
                "PATH": os.environ.get("PATH", ""),
                "HOME": os.environ.get("HOME", ""),
            },
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await asyncio.wait_for(
                    session.call_tool(
                        "understand_image",
                        arguments={"prompt": prompt, "image_source": image_path},
                    ),
                    timeout=timeout,
                )
                parts: list[str] = []
                for c in result.content:
                    text = getattr(c, "text", None)
                    if text:
                        parts.append(text)
                if getattr(result, "isError", False):
                    raise RuntimeError(f"minimax_mcp tool error: {' | '.join(parts)[:500]}")
                return "\n".join(parts).strip()

    return asyncio.run(_run())


# ---------------------------------------------------------------------------
# Public API


def caption(
    image_path: str | Path,
    *,
    backend: str = DEFAULT_BACKEND,
    model: str | None = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    ollama_url: str | None = None,
    use_cache: bool = True,
    timeout: float | None = None,
) -> Caption:
    """Caption an image, using the cache when possible.

    `backend` selects the captioner implementation:
      - "ollama": local via ollama HTTP (default model `qwen2.5vl:7b`)
      - "minimax_mcp": MiniMax `understand_image` via stdio MCP
    """
    img_path = Path(image_path).resolve()
    if not img_path.exists():
        raise FileNotFoundError(img_path)

    resolved_model = model or DEFAULT_MODELS.get(backend) or backend
    image_bytes = img_path.read_bytes()
    sha = _sha256_bytes(image_bytes)
    cache_path = _cache_path(sha, backend, resolved_model)

    if use_cache:
        cached = _load_cached(cache_path)
        if cached is not None:
            return cached

    t0 = time.monotonic()
    if backend == "ollama":
        base_url = ollama_url or os.environ.get("SOMM_OLLAMA_URL", "http://localhost:11434")
        text = _call_ollama_stream(
            image_bytes,
            model=resolved_model,
            prompt=CAPTION_PROMPT,
            max_tokens=max_tokens,
            ollama_url=base_url,
            timeout=timeout,
        )
    elif backend == "minimax_mcp":
        api_key = os.environ.get("MINIMAX_API_KEY")
        if not api_key:
            raise RuntimeError("minimax_mcp backend requires MINIMAX_API_KEY in env")
        api_host = os.environ.get("MINIMAX_API_HOST", "https://api.minimax.io")
        text = _call_minimax_mcp(
            str(img_path),
            prompt=CAPTION_PROMPT,
            api_key=api_key,
            api_host=api_host,
            timeout=timeout or 300.0,
        )
    else:
        raise ValueError(
            f"unknown vision backend {backend!r}. available: {list(DEFAULT_MODELS)}"
        )
    dur = time.monotonic() - t0

    cap = Caption(
        text=text,
        sha=sha,
        backend=backend,
        model=resolved_model,
        prompt_version=PROMPT_VERSION,
        duration_s=dur,
        image_bytes=len(image_bytes),
        source_path=str(img_path),
        cached=False,
    )
    _store_caption(cache_path, cap, CAPTION_PROMPT)
    return cap


def caption_for_case(case: dict, *, backend: str = DEFAULT_BACKEND) -> Caption | None:
    """Caption a case's artifact image if present; return None otherwise.

    Case frontmatter may carry `artifact_image_path` (relative to the
    cases dir) pointing at a local PNG. Vizier-internal convention: images
    live in `evals/cases/images/<case-id>.png` by default. Backend
    override: pass `backend="minimax_mcp"` for MiniMax captioning.
    """
    raw = case.get("artifact_image_path")
    cases_dir = Path(__file__).resolve().parents[2] / "evals" / "cases"
    candidates: list[Path] = []
    if raw:
        p = Path(raw)
        candidates.append(p if p.is_absolute() else cases_dir / p)
    # Default convention
    candidates.append(cases_dir / "images" / f"{case['id']}.png")
    candidates.append(cases_dir / "images" / f"{case['id']}.jpg")
    for c in candidates:
        if c.exists():
            return caption(c, backend=backend)
    return None
