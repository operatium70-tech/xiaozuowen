# commit_push.skill

## Purpose

Standardize commit and push behavior for this novel engineering repository.

## Commit Standard

Use Conventional Commits.

Format:

```plaintext
<type>(<scope>): <summary>

<body>
```

Allowed types:

- `chore`: repository setup, structure, tooling, maintenance.
- `docs`: documentation, rules, worldbuilding notes, outlines.
- `feat`: new writing workflow, exporter feature, or major content module.
- `fix`: corrections to existing files or scripts.
- `refactor`: structural improvement without changing meaning.

Recommended scopes:

- `init`
- `rules`
- `worldbuilding`
- `characters`
- `outline`
- `prose`
- `style`
- `memory`
- `skills`
- `publish`
- `tools`
- `assets`

## Message Requirements

- The summary must clearly identify the main change.
- The body must list important content areas changed.
- The body must be searchable by future Git history review.
- Use Chinese for the key summary and body content so future history search can directly match novel project changes.
- Avoid vague messages such as `update`, `fix files`, or `initial commit`.
- Mention novel-engineering modules when relevant.

## Push Rules

- Check `git status --short --branch` before staging.
- Stage only intended files.
- Run a final status check before commit.
- Push the current branch to `origin`.
- For the first push on a branch, use upstream tracking.

## First Repository Commit Message

Recommended first commit:

```plaintext
chore(init): scaffold AI-assisted novel engineering project

- add Markdown-first project structure for the novel
- add system rules, worldbuilding, outline, style, and memory modules
- add AI skill rules for writing, pacing, suspense, battle, dialogue, emotion, foreshadowing, and git workflow
- add publishing, tools, and assets directories for long-term maintenance
```
