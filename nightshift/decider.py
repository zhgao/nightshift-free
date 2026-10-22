"""Decider (Jev -> free rules): deterministic typed decisions + budget gate."""
from __future__ import annotations
import dataclasses


@dataclasses.dataclass
class Decision:
    kind: str            # "Choice" | "Score" | "YesNo"
    question: str
    answer: str
    confidence: float    # 0.0-1.0, deterministic rule-based (not a model probability)
    reason: str
    approved: bool = True
    alternative: str = ""

    def to_dict(self):
        return dataclasses.asdict(self)


# Domain options in preference order, mirroring the poster:
# domain wanted $49 > $10 limit -> pick the cheaper one; free option always exists.
DOMAIN_OPTIONS = [
    {"name": "custom .com domain", "cost": 49.0},
    {"name": "cheap domain", "cost": 3.0},
    {"name": "GitHub Pages / free subdomain", "cost": 0.0},
]


def decide_budget(item: str, amount: float, cap: float) -> Decision:
    """Hard gate: any proposed spend above cap is rejected."""
    if amount <= cap:
        return Decision("YesNo", f"Spend ${amount:.2f} on {item} within cap ${cap:.2f}?",
                          "yes", 0.99, f"${amount:.2f} <= cap ${cap:.2f}", approved=True)
    return Decision("YesNo", f"Spend ${amount:.2f} on {item} within cap ${cap:.2f}?",
                      "no", 0.99, f"${amount:.2f} > cap ${cap:.2f}: hard budget gate",
                      approved=False, alternative="choose a cheaper alternative (see decide_choice)")


def decide_domain(cap: float, options=None) -> Decision:
    """Choice: first preferred option that fits the cap. Draft only — never buys."""
    opts = options if options is not None else DOMAIN_OPTIONS
    for opt in opts:
        if opt["cost"] <= cap:
            cheapest_free = opt["cost"] == 0.0
            reason = (f"first preferred option within cap ${cap:.2f}; "
                      f"rejected anything above cap")
            return Decision("Choice", "Which domain/hosting option?",
                            opt["name"], 0.95 if not cheapest_free else 0.99, reason,
                            approved=True, alternative="")
    # Should never happen because a $0 option exists, but stay safe.
    return Decision("Choice", "Which domain/hosting option?",
                    "GitHub Pages / free subdomain", 0.99,
                    "fallback free option", approved=True)


def decide_should_build(goal: str, product_name: str) -> Decision:
    has_product = bool(product_name and product_name.strip())
    has_goal = len((goal or "").strip()) >= 4
    if has_product and has_goal:
        return Decision("Score", "Build a landing page in this run?",
                        "score=0.9 build", 0.9, "goal and product name both present")
    return Decision("Score", "Build a landing page in this run?",
                    "score=0.2 skip", 0.6, "goal or product name missing")


def decide_social_draft() -> Decision:
    """Posting is public action: always draft-only."""
    return Decision("YesNo", "Auto-post the social thread?", "no", 1.0,
                    "public actions require the owner's go-ahead; draft only",
                    approved=False, alternative="write social_draft.md for manual review")


def run_all_decisions(goal: str, product_name: str, cap: float, domain_proposed: float):
    gate = decide_budget("domain", domain_proposed, cap)
    decisions = [gate, decide_domain(cap), decide_should_build(goal, product_name),
                 decide_social_draft()]
    return decisions
