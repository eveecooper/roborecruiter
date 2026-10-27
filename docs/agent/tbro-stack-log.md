# Running stack log

**Maintained by the `tbro` subagent.** One row per technology, added or corrected when Tbro
assesses a task that needs it. Rows are never deleted; a technology that is dropped has its status
changed to *rejected* with the reason in the row.

Status: *in plan* means the engineering plan already names it. *proposed* means Tbro named it for a
task under discussion and nothing has committed to it. *rejected* means it was considered and ruled
out.

| Technology | What it does here | Status | Updated |
| --- | --- | --- | --- |
| Python | Implementation language for the whole pipeline | in plan | 2026-10-23 |
| Typer | Command-line entry point (step 1.0) | in plan | 2026-10-23 |
| SQLite | Single-file local database; no server to run | in plan | 2026-10-23 |
| SQLModel | Typed table definitions and queries over SQLite | in plan | 2026-10-23 |
| Alembic | Schema migrations, so the database can change after data exists | in plan | 2026-10-23 |
| docxtpl | Fills Word templates from the fact bank (step 1.3) | in plan | 2026-10-23 |
| LibreOffice (pinned) | Converts the rendered Word file to PDF; pinned for layout reproducibility | in plan | 2026-10-23 |
| Streamlit | Local review console for Gate 2 (step 1.3) | in plan | 2026-10-23 |
| Overture Maps Places | Employer source for geographic discovery (Phase 2, step 2.1) | in plan | 2026-10-23 |
| DuckDB | Reads the Overture cloud files directly, only the matching portions | in plan | 2026-10-23 |
