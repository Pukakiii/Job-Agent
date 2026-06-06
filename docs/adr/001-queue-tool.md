# 1. Queue Tool
 
A queue tool is a non-negotiable component for this application. The full pipeline — scraping job postings via Apify, embedding results, running LLM analysis, and delivering follow-up emails — requires multiple asynchronous workers running concurrently. There are many tools that solve this problem, ranging from lightweight to production-grade solutions like Celery and others.
 
**Decision**: [ARQ](https://github.com/python-arq/arq) is a lightweight, Redis-based solution that naturally pairs with FastAPI's async model. It includes built-in support for retries, result storage, and cron scheduling — useful for periodic re-scraping and queued email delivery. All of these traits align well with [MVP requirements](../system-requirements.md), and the learning curve is gentle.
 
**Tradeoff**: Ease of implementation and the lightweight footprint come with a potential production scaling ceiling. If the project grows to serve a very large number of users, a more robust solution may fit better.
 
**Alternatives**:
 
- *Celery* — the mature default. Huge ecosystem, battle-tested, but heavyweight, sync-first (awkward with async FastAPI), and requires significant configuration overhead. Overkill for a learning-oriented project not targeting thousands of concurrent users.
- *Redis Queue (RQ)* — battle-tested with good documentation. However, RQ is designed for CPU-bound or short-lived tasks, whereas our pipeline is dominated by I/O (LLM API calls, scraping, database writes). Its synchronous fork-per-job workers block on I/O and waste the worker process — achieving concurrency requires spinning up more processes rather than leveraging async. A poor fit for our workload.
- *Dramatiq* — a middle ground between RQ and Celery. Simpler than Celery with a cleaner API, but still sync-first and a less natural fit with FastAPI's async model compared to ARQ.
 