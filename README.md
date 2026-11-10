# Cuadre App

Cross-platform cash reconciliation application for CP Company retail stores.

## Purpose

Standardize the daily cash reconciliation process across stores, providing a consistent calculation, validation and submission workflow.

## Scope

- Store identification and daily reconciliation.
- Centralized cash calculation.
- Employee confirmation of expected cash.
- Mandatory discrepancy notes when cash does not match.
- Submission records and historical traceability.
- Printable reconciliation reports.

## Technology

- Python
- PySide6 (Qt)
- SQLite
- ReportLab
- pytest

## Target Platforms

- Debian Linux
- Arch Linux
- Windows

## Development

The application is developed on Arch Linux using an isolated Python virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Project Status

Initial development — Instance 1: Core reconciliation engine.

## License

Internal CP Company project. Not for public distribution.
