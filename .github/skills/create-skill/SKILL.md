---
name: create-skill
description: 'Create and initialize a reusable SKILL.md for VS Code agent workflows. Use when setting up new skills, defining step-by-step procedures, and validating frontmatter and folder structure.'
argument-hint: 'Skill purpose and scope (workspace or personal)'
user-invocable: true
disable-model-invocation: false
---

# Create Skill Initializer

## What This Skill Produces
- A valid skill folder with `SKILL.md`.
- Frontmatter that passes naming and discovery requirements.
- A first draft workflow that can be refined with user input.

## When To Use
- You want a new slash-invocable workflow in chat.
- You need repeatable steps with optional assets/scripts/references.
- You want to standardize how skills are authored in this repo.

## Required Permit Before Running
- Confirm write access to this workspace.
- Confirm target scope:
  - Workspace: `.github/skills/<name>/`
  - Personal: `~/.copilot/skills/<name>/`

## Procedure
1. Confirm outcome and scope.
2. Choose a lowercase hyphenated skill name matching folder name.
3. Create folder `.github/skills/<name>/`.
4. Create `SKILL.md` with valid YAML frontmatter.
5. Draft sections:
   - What the skill produces
   - When to use
   - Procedure
   - Completion checks
6. Validate:
   - `name` matches folder name
   - `description` has trigger keywords
   - Markdown links to any assets use `./` relative paths
7. Iterate on ambiguous areas with focused questions.

## Completion Checks
- Skill appears in slash command list.
- Workflow steps are explicit and executable.
- No missing prerequisites or unclear decision points.

## Example Invocation
`/create-skill Build a review workflow skill for backend API changes in workspace scope`
