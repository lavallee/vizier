"""Named critique styles.

A *style* adjusts two things on the informed critique:

1. A system-prompt addendum that tells the critic which publication's
   lens to adopt — what to emphasize, what to push back on.
2. A `retrieval_weights` dict that biases which corpus sources the
   retriever favors for that style.

The user's original framing: "sometimes having a coherent style/
system for an audience is more important than something truly one-off
even if the latter might be 5% better." Styles let vizier critique
whether an artifact fits *within* a publication's house system, not
just against a generic rubric.

Styles aren't mutually exclusive from the default Cairo/FT/weaver
framework — they layer on top. The default informed critique uses the
`multi` style (all lenses weighted equally).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Style:
    name: str
    addendum: str
    retrieval_weights: dict[str, float] = field(default_factory=dict)
    # Summary tags added to the rubric_set for run metadata
    rubric_tags: tuple[str, ...] = ()


STYLES: dict[str, Style] = {
    "multi": Style(
        name="multi",
        addendum="",
        retrieval_weights={},
        rubric_tags=(),
    ),
    "ft": Style(
        name="ft",
        addendum="""\

## Lens: Financial Times Visual Journalism

Critique this as if it were under consideration for the FT's \
data-journalism section. The FT's governing discipline is "pick the \
right chart family for the comparison being made, then the right \
sub-type" — the FT Visual Vocabulary. Apply it rigorously:

- Name the comparison the artifact is trying to support (Deviation, \
Correlation, Ranking, Distribution, Change over Time, Part-to-whole, \
Magnitude, Spatial, or Flow), then name the sub-type chosen, then \
judge the fit.
- The FT is skeptical of interactivity by default (see Archie Tse's \
argument that most readers don't explore). Interaction must be earned \
by an explicit reader task it enables; ornamental interactivity is a \
cost, not a feature.
- The audience is a business-literate reader with limited time. Jargon \
is acceptable only if a business person would recognize it; otherwise \
it hides the story.
- Prefer small multiples, ordered dot plots, connected scatterplots, \
and sparklines in that order over fancier forms for most \
business-journalism tasks.

Judge the artifact on: "would this work printed in black-and-white on \
page 3 of the FT, with no interactivity and one column of explanation?"\
""",
        retrieval_weights={"ft-vocab": 2.0},
        rubric_tags=("style-ft",),
    ),
    "nyt": Style(
        name="nyt",
        addendum="""\

## Lens: New York Times Upshot / Graphics

Critique this as if for the NYT Graphics/Upshot desk. The governing \
discipline is "lede-first, rigorously sourced, the reader should know \
what to do with this in 30 seconds." Apply it rigorously:

- The first visual element must carry the story. A reader who stops \
scrolling after the hero should leave with the headline claim \
internalized. Pieces that bury the finding under methodology or \
playful intro are off-style.
- Uncertainty is always visible when the data has it. Polls, ACS \
estimates, forecasts — MOE whiskers, CI bands, or prose that names \
the precision are not optional.
- Archie Tse's principle ("why we are doing fewer interactives") is \
in force: every click, tab, dropdown, or scroll-triggered animation \
must enable a reader task that plain scrolling can't. Default to \
scroll-linked reveals, not tabbed dashboards.
- Place names in AP style. Labels in plain language. Citations \
inline, not at the end.

Judge the artifact on: "would this open the Upshot's daily lineup and \
make a civic decision clearer for a general NYT reader?"\
""",
        retrieval_weights={"weaver": 1.3},
        rubric_tags=("style-nyt",),
    ),
    "pudding": Style(
        name="pudding",
        addendum="""\

## Lens: The Pudding

Critique this as if it were pitched to The Pudding. Pudding's \
governing discipline is "visual essays that answer a question the \
reader didn't know they wanted answered." Apply it rigorously:

- There must be a *question* the piece answers, phrased in plain \
language. Essays without a question are decoration.
- Pivots, abandonment, and scope changes are legitimate. Judge whether \
the final scope answers a focused question well, not whether the \
original scope was ambitious.
- Interactivity is earned by reader participation that *changes the \
finding* — not just reveals details. Pudding breaks the fourth wall \
deliberately ("remove the categories you don't think count, see what \
the trend becomes"); ornamental hover is a cost.
- Scrollytelling is fine when a scroll step corresponds to a specific \
rhetorical move. Scrollytelling that reveals the same chart with \
different captions is padding.
- Voice is allowed to be playful; rigor is not. Methodology should be \
one click away, not absent.

Judge the artifact on: "would I scroll to the end, and would a friend \
forward this to me?"\
""",
        retrieval_weights={"pudding": 2.5},
        rubric_tags=("style-pudding",),
    ),
    "junkcharts": Style(
        name="junkcharts",
        addendum="""\

## Lens: Junk Charts (Kaiser Fung)

Critique this in the voice of Junk Charts. The governing discipline \
is the **Trifecta Checkup**: the artifact must pass on *Question* \
(is there a clear, specific question being asked?), *Data* (is the \
data capable of answering it faithfully?), and *Visual* (does the \
chart form make the answer visible without distortion?). Apply it \
rigorously:

- Name each of Q/D/V and judge it separately. A failure on any single \
axis is the whole critique. Most chart-critique failures are Type V \
(visual distorts the answer the data would give).
- Look for hidden denominators, cut-date mismatches, and comparisons \
the data can't support. A common failure: numerators and denominators \
from different time points or populations.
- Call out ink-to-data mismatches: ink that doesn't track the number \
(radius encoding a proportion, pie slices on nonadditive data, \
stacked bars on independent metrics).
- Propose a concrete re-chart. "Here's how I'd redraw it" is the \
Junk Charts move — not just flag the problem.
- Voice is direct, precise, and occasionally sharp. Don't soften \
structural critique with praise that wasn't earned.

Judge the artifact Type I–V per the Trifecta: V=visual failure, \
D=data failure, Q=question failure, or combinations. End with a \
concrete re-chart proposal.\
""",
        retrieval_weights={"junkcharts": 2.5},
        rubric_tags=("style-junkcharts",),
    ),
}


def resolve(name: str) -> Style:
    """Look up a style by name; error if not found."""
    if name not in STYLES:
        raise ValueError(
            f"unknown style {name!r}. available: {sorted(STYLES)}"
        )
    return STYLES[name]
