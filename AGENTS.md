# AGENTS.md

## Project context

This repository is the working area for the NASA Space Challenge POLARIS. At the moment, the workspace does not contain project-specific source files or documentation, so the default assumption is that the codebase is still being created or scaffolded.

Use this file as the baseline instruction set for any AI coding agent working in this repo.

## Operating principles

- Keep changes focused and small. Prefer the minimum necessary edit that satisfies the task.
- Before making large structural changes, inspect the current repo state and confirm the intended stack and naming patterns.
- Do not invent architecture or dependencies when the project is still empty; create the smallest sensible structure and document it.
- Preserve a clean repository root. Put implementation details in appropriately named folders instead of scattering files at the top level.
- Favor explicit, readable code and clear naming over clever abstractions.

## Expected workflow for agents

1. Inspect the repository before writing code.
2. Confirm whether the project is front-end, back-end, Python, or mixed.
3. Create or update the smallest set of files needed for the feature or fix.
4. Validate with the smallest relevant command available (for example, a targeted test, lint, or build step).
5. Keep documentation and code aligned as the project evolves.

## Coding conventions

- Prefer existing project conventions over generic defaults when they exist.
- Add comments only where they clarify intent or non-obvious logic.
- Avoid broad refactors during feature work unless the task explicitly requires them.
- When creating new folders, use clear domain names such as `src/`, `app/`, `tests/`, `docs/`, `scripts/`, or other task-appropriate structure.
- If the repo grows beyond a single app, create per-area conventions rather than mixing unrelated responsibilities.

## Validation guidance

- Run the narrowest relevant validation command for the task.
- If the task is a new feature, prefer a focused smoke check over a broad suite when the repo is still early-stage.
- If no automated checks exist yet, validate by running the relevant interpreter, build command, or startup command for the created component.

## When the repo is empty

If the workspace is still empty or missing project files:

- Do not assume a framework or language without checking the environment.
- Create a minimal, consistent starter structure instead of duplicating boilerplate.
- Add brief documentation when a new pattern or setup is introduced.
- Keep agent instructions in this file updated as the project grows and conventions become clearer.

## Future maintenance

As the project matures, this file should evolve to include:

- the chosen language/framework and setup commands,
- repository-specific architecture notes,
- testing and linting conventions,
- deployment or simulation guidance,
- any project-specific constraints from the NASA challenge.

This file should remain concise and actionable, and it should complement, not duplicate, deeper project documentation.
