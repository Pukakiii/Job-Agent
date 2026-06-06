# System Requirements and Goals

This file describes how an MVP should look. Every subpoint is part of the system's core business logic and should be implemented initially. Additional functionality should work on top of these predefined features.

The application collects jobs from multiple sources (Adzuna, Jooble, Careerjet via official APIs and LinkedIn/Indeed via approved scraping providers), normalizes them, deduplicates them, enriches them with AI analysis, and helps users manage their job search workflow.

## Core business logic

### Authentication & User Management

* [ ] User can sign up and log in
* [ ] User can manage their account
* [ ] User authentication is handled through JWT
* [ ] User sessions remain persistent across visits

### CV Management

* [ ] User can upload one or more CVs
* [ ] CV files are stored in object storage
* [ ] User can select an active CV
* [ ] User can update or replace existing CVs
* [ ] User can provide custom instructions for AI-assisted matching and generation

### Job Collection & Storage

* [ ] System collects jobs from supported external sources
* [ ] System normalizes jobs into a unified internal format
* [ ] System deduplicates repeated postings across sources
* [ ] System caches previously discovered jobs
* [ ] System tracks active and inactive jobs
* [ ] User has persistent access to previously discovered jobs

### Semantic Matching & Retrieval

* [ ] System generates embeddings for job postings
* [ ] System generates embeddings for uploaded CVs
* [ ] System stores embeddings using pgvector
* [ ] System performs semantic similarity search between CVs and jobs
* [ ] System retrieves and ranks relevant jobs using vector similarity
* [ ] User receives a ranked list of relevant jobs
* [ ] User can access the original application URL for every job

### AI Analysis

* [ ] System generates AI-based job relevance scores
* [ ] System provides AI-generated explanations for job matches
* [ ] System identifies strengths and weaknesses of a job match
* [ ] System categorizes jobs automatically
* [ ] System stores AI analysis results for future access

### Scam & Risk Detection

* [ ] System evaluates jobs for potential scam indicators
* [ ] System assigns a risk score to each job
* [ ] System stores risk explanations and detected flags
* [ ] User can review scam-risk information before applying

### Resume & Cover Letter Generation

* [ ] User can generate a tailored resume for a selected job
* [ ] User can generate a tailored cover letter for a selected job
* [ ] Generated documents are based on the selected CV and job description
* [ ] Generated outputs are stored for future reuse

### Outreach & Email Automation

* [ ] User can generate AI-assisted outreach emails
* [ ] System can send emails through configured email providers
* [ ] System stores all generated emails
* [ ] System tracks email delivery status
* [ ] User can review previously generated and sent emails

### Application Tracking

* [ ] User can create and manage applications
* [ ] Applications are linked to jobs
* [ ] Applications support status transitions

Supported statuses:

* saved

* applied

* interview

* offer

* rejected

* [ ] User can attach notes to applications

* [ ] User can review application history

### Dashboard & Analytics

* [ ] User can view a centralized jobs dashboard
* [ ] User can view AI analysis results
* [ ] User can manage applications through a Kanban-style board
* [ ] User can view outreach and email activity
* [ ] System computes statistics directly from database records
* [ ] System provides application pipeline metrics
* [ ] System provides interview and conversion statistics

### Background Processing

* [ ] Long-running tasks execute asynchronously
* [ ] Job ingestion runs through background workers
* [ ] Embedding generation runs through background workers
* [ ] AI analysis runs through background workers
* [ ] Email delivery runs through background workers
* [ ] Background tasks are processed through a queue system

### Data Persistence

* [ ] Jobs remain available after collection
* [ ] AI outputs remain available after generation
* [ ] Generated resumes remain available after creation
* [ ] Generated cover letters remain available after creation
* [ ] Application records remain available across sessions
* [ ] Email history remains available across sessions
