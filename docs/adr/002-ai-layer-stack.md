# 2. AI Layer Stack

The application's AI layer handles two distinct phases: ingestion and query.

During ingestion, scraped job postings are normalized, embedded, and stored in `pgvector`, building a searchable semantic index. Only new or modified jobs are embedded to avoid unnecessary processing.

During the query phase, a user's uploaded CV is parsed into a structured candidate profile and embedded. This embedding is used to perform semantic similarity search against stored job embeddings. The top results are then passed to a language model for re-ranking, generating fit explanations, identifying strengths and weaknesses, performing scam-risk analysis, and powering downstream generation tasks such as resume generation, cover letter generation, and outreach email generation.

The CV is small enough to fit comfortably within modern context windows, so retrieval is applied to the job corpus rather than the CV.

Long-running AI operations execute asynchronously through ARQ workers.

---

## Model Providers

The platform supports two AI execution modes: local inference and bring-your-own-key (BYOK) cloud inference.

---

### Local Models (Ollama)

All models run locally on the user’s machine via Ollama, with no external API calls required.

#### Embedding Model

* `nomic-embed-text`

**Responsibilities:**

* Generate job embeddings
* Generate CV embeddings
* Support semantic similarity search via pgvector

---

#### Language Model

**Primary Recommendation:**

* `gemma3:4b`

**Responsibilities:**

* CV profile extraction
* Job scoring and ranking
* Match explanations
* Scam-risk analysis
* Resume generation
* Cover letter generation
* Outreach email generation

**Lightweight Alternatives:**

* `qwen3:1.7b`
* `phi4-mini`

These models are optimized for lower hardware requirements and faster inference while maintaining acceptable quality for core tasks.

---

### API Models (Bring Your Own Key)

Users may connect their own API keys for supported cloud providers.

Supported providers:

* OpenAI
* Anthropic
* Google
* OpenRouter-compatible providers

---

#### Embedding Model

* `text-embedding-3-small`

**Responsibilities:**

* Generate job embeddings
* Generate CV embeddings
* Support semantic similarity search via pgvector

---

#### Language Model

Any user-selected API model can be used.

**Responsibilities:**

* CV profile extraction
* Job scoring and ranking
* Match explanations
* Scam-risk analysis
* Resume generation
* Cover letter generation
* Outreach email generation

---

## Retrieval Pipeline

The retrieval pipeline is implemented using FastAPI services, SQLAlchemy, and pgvector queries.

---

### Job Ingestion Flow

```text
1. Job collected from external source
2. Job normalized
3. Job embedded
4. Embedding stored in pgvector
5. AI analysis generated
6. Results persisted in database
```

---

### User Query Flow

```text
1. User uploads CV
2. CV parsed into structured profile
3. CV embedded
4. Similarity search executed against pgvector
5. Top matching jobs retrieved
6. Language model re-ranks results
7. Fit explanations generated
8. Final results returned to the user
```

---

## Background Processing

All long-running AI tasks are executed asynchronously using ARQ workers.

---

### Background Tasks

* Job embedding generation
* CV embedding generation
* AI job analysis
* Scam-risk analysis
* Resume generation
* Cover letter generation
* Email generation

---

## Tradeoffs

### Local AI (Ollama)

Local inference provides:

* Full data privacy
* No per-request cost
* No dependency on external APIs

However:

* Requires sufficient hardware (e.g. `gemma3:4b` baseline)
* Lower quality compared to frontier cloud models
* Limited reasoning depth for complex generation tasks

---

### Cloud AI (BYOK)

Cloud inference provides:

* Higher model quality
* Better reasoning and writing quality
* More stable performance across tasks

However:

* Requires API key setup
* Introduces per-token costs
* Sends CV and job data to external providers

---

## Alternative Models

The system supports flexible model configuration depending on user needs.

### Embeddings

* Local: `nomic-embed-text`
* Cloud: `text-embedding-3-small`

---

### Language Models

* Local primary: `gemma3:4b`
* Lightweight local alternatives: `qwen3:1.7b`, `phi4-mini`
* Cloud (BYOK): any OpenAI / Anthropic / Google / OpenRouter-compatible model