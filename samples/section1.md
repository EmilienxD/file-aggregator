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

