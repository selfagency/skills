---
applyTo: "skills/**/SKILL.md,skills/**/scripts/**,skills/**/references/**,skills/**/assets/**,skills/**/evals/**,package.json,skills-npm.config.ts,.gitignore"
description: "Specialized instructions for creating, refining, and evaluating Agent Skills according to the Agent Skills specification and best practices, with critical dev workflow integration."
---

# Skill Creation Specialist Instructions

## Purpose

Apply these rules when creating or modifying any skill files in this repository.
These rules are additive to repository-wide critical instructions and are optimized
for correctness, trigger quality, and evaluation rigor.

## Non-negotiable priorities

1. Follow Agent Skills spec requirements exactly.
2. Preserve and apply repository critical guidance (`critically-important.instructions.md`).
3. Keep instructions concise and high-signal to protect context budget.
4. Prefer deterministic, testable workflows over ad-hoc approaches.

## Required skill shape

A skill should use this minimum structure:

```text
<skill-name>/
├── SKILL.md
├── scripts/            # optional
├── references/         # optional
├── assets/             # optional
└── evals/evals.json    # recommended
```

## SKILL.md frontmatter constraints

Enforce strictly:

- `name` (required)
  - 1 to 64 chars
  - lowercase letters, numbers, hyphens only
  - no leading/trailing hyphen
  - no consecutive hyphens
  - must match parent directory name
- `description` (required)
  - 1 to 1024 chars
  - must explain both what the skill does and when to use it

Optional fields (`license`, `compatibility`, `metadata`, `allowed-tools`) should only be included when they add clear value.

## Description quality rules (triggering)

Treat `description` as the primary trigger mechanism.

- Use imperative phrasing: “Use this skill when …”
- Describe user intent, not internal implementation
- Include likely phrasing variations and near-synonyms
- Add boundaries to prevent false triggers where needed
- Keep under 1024 characters

### Trigger validation expectations

For meaningful skill changes, evaluate triggering behavior:

- Build should-trigger and should-not-trigger query sets
- Use train/validation split to reduce overfitting
- Run each query multiple times (default 3)
- Track trigger rate and iterate based on misses/false positives

## Body authoring rules

Write procedures, not vague principles.

- Prefer concrete step sequences
- Provide defaults rather than long option menus
- Add gotchas for common model mistakes
- Add validation loops for critical outputs
- Use plan-validate-execute for destructive or stateful operations
- Avoid generic filler (“follow best practices”, “handle errors appropriately”)

## Progressive disclosure requirements

Keep `SKILL.md` lean and move detail to references:

- Target under 500 lines and roughly under 5000 tokens
- Move deep details to `references/*.md`
- Keep referenced paths one level deep from `SKILL.md`
- State exactly when each reference file should be loaded

## Scripts standards (`scripts/`)

Bundle scripts when repeated logic or deterministic reliability is needed.

Script requirements:

- Non-interactive only (no prompts or menus)
- Clear `--help` output
- Helpful, actionable error messages
- Structured data output on stdout (JSON/CSV/TSV when appropriate)
- Diagnostics/progress on stderr
- Meaningful exit codes
- Idempotent behavior where possible
- Safe defaults; `--dry-run` for destructive flows when applicable

Command guidance:

- Pin versions for one-off package commands when feasible
- Document prerequisites explicitly
- Use relative paths from skill root

## skills-npm discovery and repository integration

For this repository, npm-based skill discovery is the default approach.

- Use `skills-npm` to discover skills shipped in npm dependencies.
- Keep sync automated via the `prepare` script.
- Exclude generated symlink output from VCS (`skills/npm-*`).
- Prefer dry-run before apply when changing filters or source behavior.

### Required repository configuration

Ensure all of the following are present and consistent:

1. `skills-npm` in `devDependencies`.
2. `package.json` includes `prepare`, `skills:sync`, and `skills:sync:dry` scripts.
3. Root `skills-npm.config.ts` with explicit defaults.
4. `.gitignore` entry for `skills/npm-*`.

### Discovery defaults

- Prefer `source: 'package.json'` for reproducible and workspace-friendly discovery.
- Enable recursive scanning when monorepo/workspace packages are in play.
- Use include/exclude filters explicitly when constraining scope.
- Regenerate symlinks from dependency state; do not commit generated links.

### Package-author conventions

When authoring packages intended to ship skills:

- Place skills under `skills/<skill-name>/SKILL.md`.
- Keep each shipped skill spec-compliant.
- Ensure the published package includes the `skills/` directory.

## Eval-driven quality gate

For behavior-changing skill work, require eval iteration.

Minimum setup:

- Maintain `evals/evals.json`
- Start with 2–3 realistic cases + at least 1 edge case
- Add assertions after first output pass (when expectations are concrete)

Comparison requirement:

- Compare `with_skill` vs baseline (`without_skill` or prior snapshot)
- Capture pass/fail evidence for assertions
- Capture timing/token deltas
- Refine instructions/scripts based on measured deltas

## Integration with critical development workflow

When editing skill files, also apply the repository critical guidance:

- Clarify constraints early (security, performance, accessibility where relevant)
- Inspect before editing, then plan in verifiable subtasks
- Make surgical edits only; avoid unsolicited refactors
- Use safe file-editing methods (no shell heredoc-based file writes)
- Validate outputs before finalizing
- Keep communication precise and concise

## Security and reliability baseline

- Never hardcode secrets
- Validate inputs and file paths for scripts
- Avoid unsafe shell execution patterns
- Explicitly identify the principal threat for security-sensitive logic
- Ensure failure states are explicit and recoverable

## Maintenance expectations

When behavior changes:

- Update `SKILL.md` and related references/scripts in the same change
- Keep eval assets aligned with new behavior
- Remove stale or contradictory guidance
- Favor small, reviewable diffs

## Review checklist

- [ ] Frontmatter passes spec constraints
- [ ] Description is scoped and ≤1024 chars
- [ ] Body is procedural and high-signal
- [ ] Progressive disclosure is applied
- [ ] Scripts are non-interactive and robust
- [ ] Eval coverage exists for meaningful behavior
- [ ] Baseline comparison and deltas are documented
- [ ] No unsafe patterns or secrets introduced
