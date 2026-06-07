# 1. Queue Tool
 
A queue tool is a non-negotiable component for this application. The full pipeline — scraping job postings via Apify, embedding results, running LLM analysis, and delivering follow-up emails — requires multiple asynchronous workers running concurrently. There are many tools that solve this problem, ranging from lightweight to production-grade solutions like Celery and others.
 
**Decision**: [ARQ](https://github.com/python-arq/arq) is a lightweight, Redis-based solution that naturally pairs with FastAPI's async model. It includes built-in support for retries, result storage, and cron scheduling — useful for periodic re-scraping and queued email delivery. All of these traits align well with [MVP requirements](../system-requirements.md), and the learning curve is gentle.
 
