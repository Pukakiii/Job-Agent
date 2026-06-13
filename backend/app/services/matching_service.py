import json
from uuid import UUID

from pydantic import BaseModel, TypeAdapter, ValidationError

from app.core.logger import get_logger
from app.exceptions import CVNotFound, CVNotParsed, LLMOutputInvalid, NoMatchesFound
from app.integrations.embeddings import Embedder
from app.integrations.openai_client import OpenAIClient
from app.models.job import Job
from app.models.search import Search
from app.repositories.cv_repo import CVRepository
from app.repositories.job_repo import JobRepository
from app.repositories.search_repo import SearchRepository

logger = get_logger("app.services.matching_service")

CANDIDATE_LIMIT = 20   # vector-search breadth before rerank
MAX_RESULTS = 10       # hard cap on returned links (ADR-003)


class _Ranked(BaseModel):
    """One rerank entry. `index` references the candidate list, never a DB id —
    the model cannot invent UUIDs this way, and we validate the index range below."""
    index: int
    score: float
    explanation: str


_RANK_SYSTEM = (
    "You re-rank job postings for a candidate. You are given the candidate profile, "
    "their instructions, and a numbered list of candidate jobs. Return ONLY a JSON "
    'object of the form {"matches": [{"index": <int>, "score": <float 0..1>, '
    '"explanation": <one short sentence>}]}. Include only genuinely relevant jobs, '
    f"best first, at most {MAX_RESULTS}. Each 'index' must reference a job in the list."
)


class MatchingService:
    """Embed a query from the CV + prompt, vector-search candidate jobs, LLM-rerank
    into explained matches (capped at 10), and persist the Search. HTTP-agnostic."""

    def __init__(
        self,
        cv_repo: CVRepository,
        job_repo: JobRepository,
        search_repo: SearchRepository,
        embedder: Embedder,
        openai: OpenAIClient,
    ):
        self.cv_repo = cv_repo
        self.job_repo = job_repo
        self.search_repo = search_repo
        self.embedder = embedder
        self.openai = openai

    async def find_matches(self, user_id: UUID, cv_id: UUID, prompt: str) -> Search:
        cv = await self.cv_repo.get_by_id(cv_id)
        if cv is None or cv.user_id != user_id:
            raise CVNotFound("CV not found.")
        if not cv.extracted_text:
            raise CVNotParsed("CV has not been parsed yet — try again shortly.")

        query_vec = await self.embedder.embed_query(self._query_text(cv, prompt))
        candidates = await self.job_repo.search_by_vector(query_vec, limit=CANDIDATE_LIMIT)
        if not candidates:
            raise NoMatchesFound("No jobs available to match against.")

        ranked = await self._rerank(cv, prompt, candidates)
        if not ranked:
            raise NoMatchesFound("No relevant jobs found for this search.")

        rows = [(candidates[r.index].id, r.score, r.explanation) for r in ranked]
        saved = await self.search_repo.save_search(user_id, cv_id, prompt, rows)
        # Reload with results + jobs eager-loaded so the response can serialize without
        # lazy I/O (and ordered by rank via the relationship's order_by).
        return await self.search_repo.get_with_results(saved.id)

    @staticmethod
    def _query_text(cv, prompt: str) -> str:
        profile = cv.parsed_profile or {}
        parts = [prompt, profile.get("summary") or "", cv.extracted_text or ""]
        return "\n\n".join(p for p in parts if p).strip()

    async def _rerank(self, cv, prompt: str, candidates: list[Job]) -> list[_Ranked]:
        listing = "\n".join(
            f"[{i}] {j.title} @ {j.company or '?'} — {(j.description or '')[:300]}"
            for i, j in enumerate(candidates)
        )
        user_prompt = (
            f"Candidate profile:\n{(cv.extracted_text or '')[:4000]}\n\n"
            f"Instructions: {prompt}\n\nJobs:\n{listing}"
        )
        raw = await self.openai.chat(
            system_prompt=_RANK_SYSTEM, user_prompt=user_prompt, json_mode=True
        )
        if not raw:
            raise LLMOutputInvalid("Re-rank returned no output.")
        try:
            payload = json.loads(raw)
            ranked = TypeAdapter(list[_Ranked]).validate_python(payload["matches"])
        except (ValueError, KeyError, TypeError, ValidationError) as exc:
            raise LLMOutputInvalid(f"Re-rank JSON invalid: {exc}") from exc

        seen: set[int] = set()
        out: list[_Ranked] = []
        for r in ranked:
            if 0 <= r.index < len(candidates) and r.index not in seen:
                seen.add(r.index)
                out.append(r)
            if len(out) >= MAX_RESULTS:
                break
        return out
