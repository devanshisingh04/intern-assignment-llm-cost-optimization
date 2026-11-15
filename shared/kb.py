from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from shared.tokens import count_tokens

KB_DIR = Path(__file__).resolve().parents[1] / "data" / "kb"


@lru_cache
def article_ids() -> list[str]:
    return sorted(p.stem for p in KB_DIR.glob("*.md"))


@lru_cache
def load_article(article_id: str) -> str:
    return (KB_DIR / f"{article_id}.md").read_text()


@lru_cache
def all_articles_blob() -> str:
    """Concatenated help-center articles for Question 1."""
    parts = []
    for aid in article_ids():
        parts.append(f"--- {aid} ---\n{load_article(aid)}\n")
    return "\n".join(parts)


@lru_cache
def expanded_help_center_blob() -> str:
    """Expanded help center for Question 2."""
    base = all_articles_blob()
    filler = (
        "## Internal routing note\n"
        "Carrier pickup windows, warehouse bin labels, and CS macro catalog. "
        "Does not change customer policy unless an article id is cited.\n"
    )

    target = 210_000

    def build_blob(n: int) -> str:
        chunks = [base]
        for i in range(n):
            chunks.append(
                filler + f"Batch {i}\n" + ("-" * 40 + "\n") * 30
            )
        return "\n".join(chunks)

    base_tokens = count_tokens(base)

    if base_tokens >= target:
        return base

    sample = filler + "Batch 0\n" + ("-" * 40 + "\n") * 30
    chunk_tokens = max(1, count_tokens(sample))

    low = 0
    high = max(1, (target - base_tokens) // chunk_tokens)

    while count_tokens(build_blob(high)) < target:
        low = high
        high *= 2

    while low + 1 < high:
        mid = (low + high) // 2

        if count_tokens(build_blob(mid)) >= target:
            high = mid
        else:
            low = mid

    return build_blob(high)
