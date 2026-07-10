"""Deterministic (non-LLM) analysis of a chart's colors.

vizier's first computed signal: everything else in the critique pipeline is
LLM-mediated (vision caption -> text critique). This package measures what is
*measurable from color alone* — colorblind separation, WCAG contrast, OKLCH
lightness/chroma — so a critique can carry ground truth instead of an eyeballed
guess. See `color` for the checks and `extract` for pulling exact swatches out of
an SVG/HTML artifact.

The color math is a faithful port of the `dataviz` skill's `validate_palette.js`
(same thresholds, same Machado-2009 CVD transforms) so vizier and that skill never
disagree on a verdict.
"""

from .color import (  # noqa: F401
    Report,
    Check,
    contrast,
    delta_e,
    oklch,
    validate_categorical,
    validate_ordinal,
    format_report,
)
from .generate import (  # noqa: F401
    suggest_palette,
    suggest_ramp,
    ink_on,
)
from .forms import recommend_form  # noqa: F401
from .guidance import implementation_guide  # noqa: F401
from .structure import lint_svg  # noqa: F401
