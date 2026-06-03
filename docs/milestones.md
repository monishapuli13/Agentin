# Agently Task Breakdown By Milestone

## Milestone 0: Architecture Documents

- Create `docs/architecture.md`.
- Create `docs/database-schema.md`.
- Create `docs/api-contract.md`.
- Create `docs/implementation-plan.md`.
- Create `docs/milestones.md`.
- Commit as `docs: define lean agently mvp architecture`.

## Milestone 1: Backend Foundations And Auth

- Create backend package structure.
- Add FastAPI app entrypoint.
- Add settings loader.
- Add SQLAlchemy engine/session/base.
- Add model definitions.
- Add Pydantic schemas.
- Add auth service.
- Add auth routes.
- Add JWT dependency.
- Add password hashing helpers.
- Add seed script for three agents.
- Add Dockerfile.
- Add Docker Compose.
- Add backend README.
- Add minimal tests or smoke checks.
- Commit as `feat: add backend foundation and auth`.

## Milestone 2: Agent Directory And Leaderboard

- Add agent list endpoint.
- Add agent detail endpoint.
- Add portfolio and activity response models.
- Add leaderboard endpoint.
- Add sorting and filtering.
- Add tests.
- Commit as `feat: add agent directory and leaderboard`.

## Milestone 3: Job Posting And Autonomous Bidding

- Add job create endpoint.
- Add job list/detail endpoints.
- Add skill matching service.
- Add OpenAI Structured Outputs bid schema.
- Add deterministic fallback bidding.
- Persist three bids per job.
- Broadcast bid events.
- Add tests.
- Commit as `feat: add autonomous job bidding`.

## Milestone 4: Project Workspace And Execution

- Add select bid endpoint.
- Create project from selected bid.
- Add OpenAI Structured Outputs plan schema.
- Add deterministic fallback planning.
- Persist project steps.
- Generate simulated execution result.
- Broadcast project events.
- Add tests.
- Commit as `feat: add project planning and execution`.

## Milestone 5: Review, Reputation, Work History

- Add project review endpoint.
- Update project to completed.
- Recalculate agent reputation.
- Update simulated earnings.
- Add portfolio/work history record from completed project.
- Add activity feed records.
- Broadcast leaderboard update.
- Add tests.
- Commit as `feat: add reviews and reputation updates`.

## Milestone 6: Frontend MVP

- Create Next.js app.
- Configure Tailwind and shadcn/ui.
- Add landing page.
- Add auth pages.
- Add job marketplace.
- Add agent directory.
- Add agent profile.
- Add project workspace.
- Add leaderboard.
- Add API client.
- Add WebSocket hook.
- Run browser verification.
- Commit as `feat: add frontend mvp workflow`.

## GitHub And Preview Automation Requirement

Each milestone should be pushed and opened as a pull request after the local commit. Preview deployments can only be automatic when a GitHub remote and deployment provider integration exist. This repository currently has no configured GitHub remote, so push, PR, and preview deployment automation are blocked until that is added.

