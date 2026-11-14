# Cuadre App — Implementation Decisions

## Phase 3 workflow

**Decision:** Retain the original workflow defined in `docs/requirements.md`; the later GUI handoff does not replace it.

- Preview, print, and send remain separate operations.
- Preview does not create a submitted historical record.
- Printing alone does not submit or notify.
- Sending submits the reconciliation and sends it through NTFY.
- Employee name is optional during ordinary use. If missing when NTFY is initiated, request it before sending.

## GUI foundation defaults (provisional)

The first GUI shell uses a starting window size of 1180 × 780 logical pixels, a minimum size of 960 × 640, and zoom from 80% to 130% in 10% increments. These are implementation defaults and can be adjusted after testing on target store displays.

Logo placement is not finalized until the supplied assets are inspected.
