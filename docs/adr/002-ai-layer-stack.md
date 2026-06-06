# 2. AI Layer Stack

This application's AI layer handles two distinct phases: ingestion and query.

During ingestion, scraped job postings are normalized, embedded, and stored in `pgvector`, building a searchable semantic index. Only new or modified jobs are embedded to avoid unnecessary processing.

During the query phase, a user's uploaded CV is parsed and converted into a structured candidate profile. The CV is embedded and used to perform semantic similarity search against stored job embeddings. The highest-ranked results are then passed to a language model, which performs re-ranking, generates fit explanations, identifies strengths and weaknesses, performs scam-risk analysis, and powers downstream features such as resume generation, cover letter generation, and outreach email generation.

The CV itself is small enough to fit comfortably within modern context windows. Retrieval is therefore applied to the job corpus rather than the CV.

## Model Providers

The platform supports two AI execution modes:

### Local Models (Ollama)

Models run entirely on the user's machine through Ollama.

Recommended local configuration:

#### Embedding Model

* `nomic-embed-text`

Responsibilities:

* Generate job embeddings
* Generate CV embeddings
* Support semantic search through pgvector

#### Language Models

##### Primary Recommendation

* `gemma3:4b`

Responsibilities:

* CV profile extraction
* Job scoring
* Match explanations
* Scam-risk analysis
* Resume generation
* Cover letter generation
* Outreach email generation

##### Lightweight Alternatives

* `qwen3:1.7b`
* `phi4-mini`

These models provide lower hardware requirements and faster inference while supporting the same feature set.

### API Models (Bring Your Own API Key)

Users may connect their own API keys and choose supported cloud providers.

Supported provider types include:

* OpenAI
* Anthropic
* Google
* OpenRouter-compatible providers

Recommended cloud configuration:

#### Embedding Model

* `text-embedding-3-small`

Responsibilities:

* Generate job embeddings
* Generate CV embeddings
* Support semantic search through pgvector

#### Language Model

* `any model connected via API`

Responsibilities:

* CV profile extraction
* Job scoring
* Match explanations
* Scam-risk analysis
* Resume generation
* Cover letter generation
* Outreach email generation

## Retrieval Pipeline

The retrieval pipeline is implemented directly through FastAPI services, SQLAlchemy, and pgvector queries.

Workflow:

Job Ingestion

1. Job collected from external source
2. Job normalized
3. Job embedded
4. Embedding stored in pgvector
5. AI analysis generated
6. Results persisted

User Query

1. User uploads CV
2. CV parsed into structured profile
3. CV embedded
4. Similarity search executed against pgvector
5. Top matching jobs retrieved
6. Language model performs re-ranking
7. Fit explanations generated
8. Results returned to the user

## Background Processing

Long-running AI operations execute asynchronously through ARQ workers.

Background tasks include:

* Job embedding generation
* CV embedding generation
* AI job analysis
* Scam-risk analysis
* Resume generation
* Cover letter generation
* Email generation

PostgreSQL with pgvector serves as the system's semantic retrieval layer and source of truth for all stored embeddings.
