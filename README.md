# Jira Weekly Status Reports

The supported application is being built as a React 18 + Vite frontend, a Node.js 22 LTS + Express backend, and a PostgreSQL 15 data store. This workspace is the initial application scaffold; report generation and Docker orchestration are added by later implementation tasks.

## Prerequisites

- Node.js 22 LTS
- npm 10 or later

## Workspace commands

Run these commands from this directory:

```sh
npm install
npm run dev
```

`npm run dev` starts the backend and frontend. During this scaffold stage, the Vite frontend is at `http://127.0.0.1:5173` and the API scaffold is at `http://127.0.0.1:3001`.

Individual workspace scripts:

| Workspace | Development | Build/check | Lint | Test |
|---|---|---|---|---|
| Frontend | `npm run dev --workspace @weekly-status/frontend` | `npm run build --workspace @weekly-status/frontend` | `npm run lint --workspace @weekly-status/frontend` | `npm run test --workspace @weekly-status/frontend` |
| Backend | `npm run dev --workspace @weekly-status/backend` | `npm run build --workspace @weekly-status/backend` | `npm run lint --workspace @weekly-status/backend` | `npm run test --workspace @weekly-status/backend` |

Root-level checks are available with `npm run build`, `npm run lint`, and `npm test`.

## Workspace layout

- `frontend/` — React/Vite browser application.
- `backend/` — Express API application.
- `packages/contracts/` — shared JSON Schema contract used by both workspaces.
- `spec/` — project constitution, specification, implementation plan, tasks, and reviews.

This web application replaces the previous Python CLI workflow. CLI compatibility and import of prior filesystem reports are not part of the initial release. Do not place Jira credentials in frontend files; backend configuration and Docker setup are added in subsequent tasks.
