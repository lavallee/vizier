"""Resilient LLM wrapper — cross-provider fallback for text calls.

somm's default `llm.generate(model=..., provider=...)` forces a single
provider. That's what we want most of the time. But for eval runs that
must survive an OpenRouter outage (or a specific model going
intermittently unavailable), we want to try a chain of
(provider, model) pairs with retry-and-backoff per attempt.

This module adds one function: `generate_resilient()`. It wraps a
somm `SommLLM` and:

- Iterates a chain of (provider, model) attempts in priority order.
- Retries each attempt on `SommRateLimited` / `SommUpstream5xx` /
  `SommTimeout` / generic `SommTransientError` with exponential
  backoff (2s → 5s → 15s by default).
- Skips to the next attempt on `SommFatalError` (400s — not going to
  fix themselves) or when the result is OK.
- Honors a wall-clock deadline so retry storms can't run forever.
- Returns the first OK `SommResult`, augmented with a `fallback_trace`
  attribute listing every attempt (provider, model, outcome, latency).

The logging still flows through somm — every attempt lands in
`.somm/calls.sqlite` with its real outcome, so the usual `somm status`
/ `somm tail` / cost tracking keeps working. No bypass; just retry
with different `model=`/`provider=` knobs.

When the somm-service `AgentWorker` sees a fallback-heavy pattern
(many calls with 2+ attempts), that's a signal to reorder the chain —
the existing sommelier decision record is where the human decision to
reorder should land.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import somm
from somm.errors import (
    SommBadRequest,
    SommFatalError,
    SommProviderError,
    SommRateLimited,
    SommTimeout,
    SommTransientError,
    SommUpstream5xx,
)
from somm_core import Outcome, SommResult


@dataclass(frozen=True)
class Attempt:
    provider: str | None  # None = let somm route
    model: str


# Default text chain: primary on OpenRouter (Opus 4.7), then
# same-provider cheaper/vision fallbacks, then cross-provider to
# MiniMax for OR-independent coverage.
DEFAULT_TEXT_CHAIN: tuple[Attempt, ...] = (
    Attempt(provider="openrouter", model="anthropic/claude-opus-4.7"),
    Attempt(provider="openrouter", model="anthropic/claude-sonnet-4.6"),
    Attempt(provider="minimax", model="MiniMax-M2.7"),
    Attempt(provider="minimax", model="MiniMax-M2"),
)

DEFAULT_BACKOFFS = (2.0, 5.0, 15.0)


@dataclass
class ResilientResult:
    """Wraps the winning SommResult + per-attempt trace."""

    result: SommResult
    fallback_trace: list[dict]  # one entry per attempt: {provider, model, outcome, error, latency_ms}

    @property
    def winner(self) -> dict:
        return self.fallback_trace[-1] if self.fallback_trace else {}


def _classify(exc: Exception) -> str:
    """Short outcome tag for the trace."""
    if isinstance(exc, SommRateLimited):
        return "rate_limited"
    if isinstance(exc, SommTimeout):
        return "timeout"
    if isinstance(exc, SommUpstream5xx):
        return "upstream_5xx"
    if isinstance(exc, SommTransientError):
        return "transient"
    if isinstance(exc, SommBadRequest):
        return "bad_request"
    if isinstance(exc, SommFatalError):
        return "fatal"
    if isinstance(exc, SommProviderError):
        return "provider_error"
    return type(exc).__name__


def generate_resilient(
    llm: somm.SommLLM,
    *,
    prompt: str,
    system: str = "",
    workload: str = "default",
    max_tokens: int = 1024,
    temperature: float = 0.2,
    chain: tuple[Attempt, ...] = DEFAULT_TEXT_CHAIN,
    backoffs: tuple[float, ...] = DEFAULT_BACKOFFS,
    deadline_seconds: float | None = 300.0,
) -> ResilientResult:
    """Try each attempt in `chain` with retries; return first OK result.

    Every attempt (success or not) is recorded in `.somm/calls.sqlite`
    via the underlying `llm.generate()`. On transient failure we pause
    `backoffs[attempt_index]` seconds; on fatal failure we skip to the
    next chain entry immediately.

    Raises `AllProvidersFailed` if no attempt succeeds before the
    deadline or chain exhausts.
    """
    t_start = time.monotonic()
    trace: list[dict] = []

    for attempt in chain:
        for retry_idx, backoff_s in enumerate((0.0, *backoffs)):
            if backoff_s > 0:
                time.sleep(backoff_s)
            if deadline_seconds is not None and (time.monotonic() - t_start) > deadline_seconds:
                trace.append({
                    "provider": attempt.provider,
                    "model": attempt.model,
                    "outcome": "deadline_exceeded",
                    "retry": retry_idx,
                })
                raise AllProvidersFailed(trace)

            t0 = time.monotonic()
            try:
                result = llm.generate(
                    prompt=prompt,
                    system=system,
                    workload=workload,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    model=attempt.model,
                    provider=attempt.provider,
                )
            except Exception as exc:
                latency_ms = int((time.monotonic() - t0) * 1000)
                tag = _classify(exc)
                trace.append({
                    "provider": attempt.provider,
                    "model": attempt.model,
                    "outcome": tag,
                    "error": str(exc)[:200],
                    "retry": retry_idx,
                    "latency_ms": latency_ms,
                })
                if isinstance(exc, SommFatalError):
                    # e.g., 400 — retries on same provider won't help
                    break
                if not isinstance(exc, SommTransientError):
                    # Unknown error class — treat as fatal for this attempt
                    break
                # transient — retry the same attempt after backoff
                continue

            latency_ms = int((time.monotonic() - t0) * 1000)
            outcome_tag = getattr(result.outcome, "value", str(result.outcome))
            trace.append({
                "provider": result.provider,
                "model": result.model,
                "outcome": outcome_tag,
                "retry": retry_idx,
                "latency_ms": latency_ms,
                "tokens_in": result.tokens_in,
                "tokens_out": result.tokens_out,
                "cost_usd": result.cost_usd,
                "call_id": result.call_id,
            })
            if result.outcome == Outcome.OK and result.text.strip():
                return ResilientResult(result=result, fallback_trace=trace)
            # somm's client catches typed exceptions and returns a
            # SommResult with a non-OK outcome. Only retry on outcomes
            # that can self-heal; skip to next chain entry otherwise.
            retryable_outcomes = {Outcome.RATE_LIMIT, Outcome.TIMEOUT, Outcome.EMPTY}
            if result.outcome not in retryable_outcomes:
                break  # UPSTREAM_ERROR / BAD_JSON / OFF_TASK — next chain entry
        # Attempt exhausted retries — next chain entry
    raise AllProvidersFailed(trace)


class AllProvidersFailed(RuntimeError):
    """Raised when every attempt in a resilient chain fails."""

    def __init__(self, trace: list[dict]):
        self.trace = trace
        msg = "all LLM providers failed after " + str(len(trace)) + " attempts: " + ", ".join(
            f"{a.get('provider')}/{a.get('model')}[{a.get('outcome')}]" for a in trace
        )
        super().__init__(msg)
