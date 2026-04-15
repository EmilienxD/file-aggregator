# Best Practicies

> Quick list of best practicies.

1. `server/` and `client/` **never import from each other** — HTTP only.
2. `shared/` contains **no database access, no service calls, no I/O**.
3. **The database is the pipeline data bus** — tasks write results to DB; the next task reads from DB. No in-memory handoff between tasks.
4. **Tasks never call other tasks** — jobs sequence work.
5. **LLM clients** are never constructed ad hoc.
6. **Binary paths and local dirs** come from `core/config.py` or environment — never hardcoded.
7. **External service packages** in the workspace must be used when they apply.
