# Agent working rules

These rules apply to automated or AI-assisted work in The Obsession Club repository.

## Bootstrap before changing TOC

- Read `TOC_CONTEXT.md` before any non-trivial change.
- Inspect the current `obsession-rebrand` implementation relevant to the task. Current code and runtime evidence outrank old chat history.
- Preserve intentional runtime/source-repair layers until their purpose is understood. Do not reactivate older competing implementations just because a repair helper looks unusual.

## Protect existing work

- Never use destructive Git recovery (`git reset --hard`, `git restore .`, `git clean`, forced checkout, history rewrite, or equivalent) to simplify a task.
- Never discard, overwrite, or revert unrelated user changes.
- Never force-push or rewrite `obsession-rebrand` history.
- Do not delete migrations, production data, assets, or apparently-unused compatibility code without proving the removal is safe.

## Change workflow

- Use a feature branch for non-trivial work and keep changes reviewable.
- Prefer one coherent commit/PR batch for one requested feature instead of bursts of tiny Railway-triggering commits.
- Inspect files before replacing them.
- Verify production-facing changes after merge/deploy; do not equate a successful Git commit with a successful Railway deployment.
- Update `TOC_CONTEXT.md` after major features, architecture/workflow decisions, or meaningful changes in pending work.

## Architecture boundaries

- TOC owns the Flask website, its SQLAlchemy-managed data, public chat, and site-side moderation/product UX.
- `Obsession-Bot` owns Discord gateway behavior and its Prisma-managed database.
- Integrate TOC and the Discord bot through explicit service APIs/contracts. Do not make either application mutate the other application's database directly.
- Keep service-to-service secrets in environment variables only. Never commit credentials, API keys, session data, Discord tokens, or production database URLs.

## Production safety

- New external HTTP calls need explicit timeouts and graceful failure behavior.
- Treat remote data as untrusted and validate shape/size before rendering or storing it.
- Database-destructive operations require explicit review and a rollback/backout plan.
- Narrow fixes should preserve TOC-specific behavior outside the requested scope.
