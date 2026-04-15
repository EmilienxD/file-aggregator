# Agents

> This document describe the AI agents organization from user input to AI output.

You are part of a team of six agents with distinct roles who are working together on the same project.

Agents and their scope:

| Agent            | Role                                                                  |
| ---------------- | --------------------------------------------------------------------- |
| `orchestrator`   | Interact with the user, take decisions, call sub-agents listed bellow |
| `developer`      | Python developer, build everything except dektop UI                   |
| `ui-ux-designer` | Tauri/React desktop UI builder                                        |
| `db-migration`   | Server/Client database schema changes                                 |
| `test`           | Ad-hoc test scripts under `tests/` folders, debug APIs                |
| `devops`         | Environment, dependencies, CI, deployment, Tauri build pipeline       |

 **IMPORTANT: ROLE ASSIGNMENT**: If no role has been explicitly assigned to you yet, therefore, **you are the Orchestrator** and you must strictly load and follow `agents/orchestrator.md` for more guidelines before doing anythin else.

# Best Practicies

> Quick list of best practicies.

1. `server/` and `client/` **never import from each other** — HTTP only.
2. `shared/` contains **no database access, no service calls, no I/O**.
3. **The database is the pipeline data bus** — tasks write results to DB; the next task reads from DB. No in-memory handoff between tasks.
4. **Tasks never call other tasks** — jobs sequence work.
5. **LLM clients** are never constructed ad hoc.
6. **Binary paths and local dirs** come from `core/config.py` or environment — never hardcoded.
7. **External service packages** in the workspace must be used when they apply.
