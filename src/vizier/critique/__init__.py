"""Critique emitters.

- `naive`: plain LLM call, no corpus, no rubric. Baseline for tracking
  whether vizier's informed critique actually adds value over time.
- Future: `informed` — retrieves from corpus and applies named rubrics.
"""
