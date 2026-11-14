# Cuadre App — Architecture

## Application layers

- `calculations.py`, `validation.py`, and `models.py` contain the reconciliation engine. They remain independent of Qt.
- `store_config.py` persists only the store code and store name in the operating-system user's configuration directory.
- `gui/` contains the PySide6 presentation layer. It must call the existing core API rather than reproduce accounting calculations or validation.
- `reporting/`, `storage/`, and `integrations/` are reserved for later milestones when report generation, historical persistence, printing, and NTFY are implemented.

## GUI entry point

Run `python -m cuadre`. The application loads the saved store identity or requests it on first launch. A corrupted store configuration is shown as an explicit error and is not silently replaced.

## Presentation rules

The GUI uses the approved CP Company palette and Montserrat/Lato font stack, with system fallbacks. Visual zoom is centralized in `gui/scaling.py`; styles are generated centrally in `gui/styles.py`. Logo assets are intentionally not embedded until the two supplied logo files have been reviewed and assigned.

## Workflow boundary

The original functional workflow in `docs/requirements.md` remains authoritative:

1. Preview calculates and displays without submission.
2. Print is a separate operation and does not submit or notify.
3. Send submits and sends through NTFY.
4. Employee identification remains optional; if absent, it is requested before NTFY sending.
