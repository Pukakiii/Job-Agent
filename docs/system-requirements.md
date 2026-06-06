# System Requirements and Goals

This file describes how an MVP should look. Every subpoint is part of the system's core business logic and should be implemented initially. Additional functionality should work on top of these predefined features. The application scrapes through Adzuna, Jooble, Careerjet(Official APIs) + LinkedIn/Indeed(best-effort Apify scraping, see [jobs scraping ADR](./adr/004-jobs-scraping.md) for the detailed explanation).

## Core business logic

- [ ] User can sign up and log in 
- [ ] User can upload a CV and a prompt
- [ ] User can see the search results 
- [ ] User get a list of the most relevant jobs and direct links to them
- [ ] User has persistent access to previously found jobs
- [ ] User receives a follow-up email listing all jobs applied to
