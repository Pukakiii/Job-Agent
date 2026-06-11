---
Applies to: frontend/ (Next.js, TypeScript, Tailwind CSS)
---

### Next.js App Router conventions

- Use route groups: (auth) for unauthenticated, (dashboard) for authenticated areas
- Pages are thin — compose feature components, call typed API helpers, no logic in page files
- No direct DB access from any frontend file — all data comes from FastAPI
- No server actions that hit the DB

### Component structure

- Shared primitives go in src/components/
- Domain logic and domain components go in src/features/<domain>/
- API calls go in src/lib/api/ — one module per backend resource, fully typed
- No inline API calls in components — always go through src/lib/api/

### TypeScript

- Strict mode on — no any, no type assertions without a comment explaining why
- All API response shapes must have explicit types — no implicit any from fetch
- Use Zod or equivalent for runtime validation of API responses where data integrity matters

### Styling

- Tailwind CSS only — no inline styles, no CSS modules unless Tailwind cannot cover the case
- Follow existing component patterns before introducing new UI primitives
