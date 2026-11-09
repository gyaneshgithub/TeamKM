"""Golden-query retrieval evaluation (REQUIREMENTS §11)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TextIO

from ki.retrieve import retrieve_candidates, rerank


@dataclass(frozen=True)
class GoldenQuerySpec:
    id: str
    query: str
    expected_doc_contains: str


@dataclass
class GoldenQueryResult:
    spec: GoldenQuerySpec
    recall_at_k: bool
    first_hit_rank: int | None  # 1-based within top-k
    mrr: float
    paths_at_k: list[str]

    @property
    def passed(self) -> bool:
        return self.recall_at_k


def load_golden_file(data: dict[str, Any]) -> tuple[int, list[GoldenQuerySpec]]:
    at_k = int(data.get("recall_at_k", 5))
    queries_raw = data.get("queries") or []
    specs: list[GoldenQuerySpec] = []
    for q in queries_raw:
        specs.append(
            GoldenQuerySpec(
                id=str(q.get("id", "?")),
                query=str(q.get("query", "")),
                expected_doc_contains=str(q.get("expected_doc_contains", "")),
            )
        )
    return at_k, specs


def eval_one(index: Any, spec: GoldenQuerySpec, *, at_k: int) -> GoldenQueryResult:
    needle = spec.expected_doc_contains
    cands = retrieve_candidates(index, spec.query, top_n=max(at_k * 2, at_k))
    ranked = rerank(spec.query, cands, take=at_k)
    paths = [s.doc_path for s in ranked]
    first_rank: int | None = None
    for i, p in enumerate(paths, start=1):
        if needle in p:
            first_rank = i
            break
    recall = first_rank is not None
    mrr = (1.0 / first_rank) if first_rank else 0.0
    return GoldenQueryResult(
        spec=spec,
        recall_at_k=recall,
        first_hit_rank=first_rank,
        mrr=mrr,
        paths_at_k=paths,
    )


def run_eval(index: Any, specs: list[GoldenQuerySpec], *, at_k: int) -> list[GoldenQueryResult]:
    return [eval_one(index, s, at_k=at_k) for s in specs]


def summarize(results: list[GoldenQueryResult]) -> dict[str, Any]:
    n = len(results) or 1
    passed = sum(1 for r in results if r.passed)
    mean_mrr = sum(r.mrr for r in results) / n
    return {
        "query_count": len(results),
        "recall_at_k_pass": passed,
        "recall_at_k_fail": len(results) - passed,
        "recall_at_k_rate": passed / n,
        "mean_mrr_at_k": mean_mrr,
    }


def emit_text_report(
    results: list[GoldenQueryResult],
    summary: dict[str, Any],
    *,
    at_k: int,
    stream: TextIO | None = None,
) -> None:
    import sys

    out = stream or sys.stdout
    out.write(f"Golden queries (recall@{at_k})\n")
    out.write(f"  pass: {summary['recall_at_k_pass']}/{summary['query_count']}\n")
    out.write(f"  mean MRR@{at_k}: {summary['mean_mrr_at_k']:.3f}\n\n")
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        rank = r.first_hit_rank if r.first_hit_rank is not None else "-"
        out.write(
            f"{status} {r.spec.id}  rank={rank}  mrr={r.mrr:.3f}  "
            f"needle={r.spec.expected_doc_contains!r}\n"
        )
        if not r.passed:
            out.write(f"       paths: {r.paths_at_k}\n")


def emit_markdown_report(
    results: list[GoldenQueryResult],
    summary: dict[str, Any],
    *,
    at_k: int,
    stream: TextIO | None = None,
) -> None:
    import sys

    out = stream or sys.stdout
    out.write("# Golden query evaluation report\n\n")
    out.write(f"- **recall@{at_k}:** {summary['recall_at_k_pass']}/{summary['query_count']} passed\n")
    out.write(f"- **Mean MRR@{at_k}:** {summary['mean_mrr_at_k']:.3f}\n\n")
    out.write("| id | pass | rank | MRR | expected (substring) | top path |\n")
    out.write("|----|------|------|-----|----------------------|----------|\n")
    for r in results:
        top = r.paths_at_k[0] if r.paths_at_k else ""
        out.write(
            f"| {r.spec.id} | {'yes' if r.passed else '**no**'} | "
            f"{r.first_hit_rank or '-'} | {r.mrr:.3f} | "
            f"`{r.spec.expected_doc_contains}` | `{top}` |\n"
        )
