# 2. AI Layer Stack
 
This application's AI layer handles two distinct phases: ingestion and query. During ingestion, scraped job postings are embedded and stored in `pgvector`, building a searchable index. During the query phase, a user's uploaded CV is parsed, a structured profile is extracted from it, and that profile is embedded to run a similarity search against the stored job vectors. The top matches are then passed back to the chat model, which re-ranks them and generates a short fit explanation for each — this is where the generation step of RAG lives. The CV itself is small enough to fit in any context window, so RAG logic applies to the job postings corpus, not to the CV.
 
**Decision**: `GPT-4o-mini` as the sole chat model and `text-embedding-3-small` as the embedding model, both from OpenAI. No orchestration framework (LlamaIndex, LangChain) — the retrieval pipeline is implemented directly via the OpenAI SDK and SQLAlchemy queries against `pgvector`. The two models serve distinct roles: `text-embedding-3-small` converts text to vectors for storage and similarity search; `GPT-4o-mini` handles structured profile extraction from the CV (validated via Pydantic) and generates ranked match explanations for the user. `pgvector` sits between the two phases as the source of truth for stored job vectors.
 
**Tradeoff**: Both models bill per token, creating a cloud dependency — downtime or API changes affect the entire AI layer. Acceptable at learning-project scale where call volume is low. Re-embedding large job corpora on every re-scrape adds incremental cost; mitigated by only embedding new or changed listings. Forgoing an orchestration framework means the retrieval pipeline is written manually, which is more code but gives complete control and avoids framework API churn.
 
**Alternatives**:
 
- *Claude Haiku* — comparable speed and cost to `GPT-4o-mini` as a chat model, but introduces a second provider (Anthropic) and splits the integration surface. A viable swap if OpenAI availability becomes an issue.
- *GPT-4o* — more capable for nuanced ranking and fit explanations, but significantly more expensive per token. Worth revisiting if match quality becomes the bottleneck in a later iteration.
- *DeepSeek R1 (rejected)* — initially considered for CV analysis. A reasoning model that burns thinking tokens on tasks that do not require deep reasoning, adding unnecessary latency and cost. Structured extraction from a CV is well within `GPT-4o-mini`'s capability.
- *text-embedding-3-large* — more accurate at 3072 dimensions versus 1536, but doubles storage size and embedding cost. Not warranted at this scale.
- *Open-source embedding models (BGE, E5)* — no per-token cost, but require self-hosted inference infrastructure. Adds operational overhead that does not suit a learning-oriented project.
- *LlamaIndex / LangChain* — natural framework choices for a RAG pipeline. Rejected because for a focused use case — embed job postings, store in `pgvector`, query by similarity — the abstraction layer adds complexity and framework API churn without meaningful benefit over direct SDK usage.
 