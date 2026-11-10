# AGENTS.md — Cuadre App

## 1. Project Overview

Cuadre App is an internal CP Company application for standardizing daily cash reconciliation across retail stores.

The application must provide a consistent reconciliation process, calculate expected cash centrally, validate employee submissions and preserve historical records.

This is a cross-platform project intended for:

- Arch Linux (development environment)
- Debian Linux (deployment)
- Windows (deployment)

The development environment is not the deployment environment.

## 2. Primary Development Principles

1. Prioritize correctness of business calculations over interface design.
2. Keep business logic independent of the graphical interface and operating system.
3. Maintain cross-platform compatibility.
4. Prefer simple, maintainable and well-documented implementations.
5. Avoid unnecessary dependencies and infrastructure.
6. Do not introduce functionality outside the agreed project scope without authorization.
7. Never silently change established business rules.

## 3. Technology Stack

The initial technology stack is:

- Python 3
- PySide6 / Qt for the graphical interface
- SQLite for local data storage
- ReportLab for PDF generation
- pytest for automated testing
- Git for version control

Use Python virtual environments for development.

Do not install project dependencies globally or modify system Python packages.

Do not introduce additional frameworks, databases or services without explaining their necessity and obtaining approval.

## 4. Architecture Requirements

Maintain separation between:

- Business logic and calculations.
- Data models and validation.
- Database access and persistence.
- Graphical interface.
- PDF generation and reporting.
- Platform-specific deployment and integration.

The calculation engine must be usable and testable without launching the graphical interface.

Avoid embedding accounting rules directly into interface components.

## 5. Business Rules and Data Integrity

The following principles are mandatory:

- Expected cash must be calculated centrally by the application.
- Employees must not manually determine or override the calculated expected cash.
- Zero is a valid numeric value and must not be confused with an empty field.
- Missing, invalid and zero-valued inputs must be handled distinctly.
- Monetary calculations must avoid floating-point precision errors. Prefer Python Decimal or integer currency units.
- Historical submissions must not be silently overwritten.
- Every submission must retain sufficient information for later review.
- Discrepancy notes must be required when the employee reports that physical cash does not match expected cash.

The definitive accounting formula, field definitions and validation rules must be documented in `docs/requirements.md` before implementation.

Do not invent missing accounting rules. Ask for clarification when requirements are ambiguous.

## 6. Cross-Platform Compatibility

Do not assume:

- Linux-specific filesystem paths.
- Linux-only commands or services.
- A particular desktop environment.
- A specific screen resolution.
- That the application always has internet access.

Use platform-independent Python libraries wherever possible.

Keep platform-specific behavior isolated in dedicated modules or deployment scripts.

Do not compromise the core application architecture to accommodate a single operating system.

## 7. Testing Requirements

Every business calculation and validation rule must have automated tests.

Before considering a task complete:

1. Run the relevant automated tests.
2. Run the complete test suite when practical.
3. Check for regressions.
4. Report test results accurately.

Include tests for:

- Normal reconciliation cases.
- Zero-valued inputs.
- Missing inputs.
- Invalid inputs.
- Boundary conditions.
- Cash discrepancies.
- Historical record preservation.

Never claim that tests passed if they were not executed.

## 8. Git and File Management

- Respect the existing repository structure.
- Do not delete or overwrite user-created files without authorization.
- Do not rewrite Git history or force-push without authorization.
- Do not commit secrets, credentials, local databases or virtual environments.
- Keep `.gitignore` updated.
- Make changes focused and easy to review.
- Do not create unnecessary duplicate files or documentation.

Before substantial modifications, inspect the existing repository and understand its current state.

## 9. Development Scope and Authorization

Development is divided into instances and milestones.

Only implement the currently authorized milestone.

Do not prematurely implement future features, deployment mechanisms or integrations.

If a proposed change affects established architecture, accounting rules, database structure or cross-platform compatibility, explain the implications before proceeding.

When requirements are incomplete, identify the missing decisions rather than making assumptions.

## 10. Documentation

Keep documentation synchronized with the implementation.

Use:

- `README.md` for project overview and setup.
- `docs/requirements.md` for functional and business requirements.
- `docs/architecture.md` for technical architecture.
- `docs/decisions.md` for important design decisions.
- `docs/roadmap.md` for development milestones.

Document significant changes and explain any deviations from established decisions.

## 11. Agent Working Protocol

At the beginning of a task:

1. Read this file.
2. Read the README.
3. Inspect the repository structure.
4. Review relevant requirements and architecture documentation.
5. Identify the authorized scope of work.

Before modifying files:

- Explain the intended implementation when the change is substantial.
- Identify potential compatibility or data-integrity implications.
- Preserve existing working functionality.

After completing a task, report:

- What was implemented.
- Which files were created or modified.
- Dependencies added or changed.
- Tests executed and their results.
- Outstanding issues or decisions requiring human approval.

## 12. Final Principle

The application exists to enforce a reliable and consistent business reconciliation process.

Technical convenience must never take precedence over accounting correctness, data integrity or the agreed operational workflow.

When uncertain, stop and ask rather than inventing business rules.
