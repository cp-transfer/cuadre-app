# Cuadre App — Functional Requirements

**Project:** CP Company  
**Instance:** 1 — Core Reconciliation Engine  
**Status:** Core reconciliation engine implemented — Phase 2 audit in progress

## 1. Purpose

Standardize daily cash reconciliation across CP Company retail stores.

The application must collect reconciliation data, calculate expected cash centrally, validate employee submissions and preserve historical records.

The application is intended for store employees and administrators.

## 2. Reconciliation Data

Each reconciliation must contain the following fields:

| Field | Description | Type |
|---|---|---|
| DATE | Reconciliation date | Date |
| STORE | Store identifier | Text |
| NET_SALES | Net sales after refunds | Monetary |
| CARDS | Card payments | Monetary |
| QR | QR payments | Monetary |
| SISTECREDITO | Sistecrédito sales | Monetary |
| ADDI | Addi sales | Monetary |
| COUPONS_REDEEMED | Redeemed coupons | Monetary |
| EXPENSES | Store expenses | Monetary |
| SISTECREDITO_COLLECTIONS | Sistecrédito collections | Monetary |
| COUPONS_SOLD_CASH | Coupons sold and paid in cash | Monetary |
| COUPONS_SOLD_OTHER_METHOD | Coupons sold and paid using another payment method | Monetary |
| BAGS | Bolsas | Integer |
| GARMENTS | Prendas | Integer |
| GARMENTS_EXCHANGE | Prendas por Canje | Integer |

### 2.1 Coupon Sales Details

Coupon sales must be recorded separately according to payment method:

- COUPONS_SOLD_CASH increases expected cash.
- COUPONS_SOLD_OTHER_METHOD decreases expected cash.
- When COUPONS_SOLD_OTHER_METHOD is greater than zero, an explanatory detail is mandatory.
- No detail is required when COUPONS_SOLD_OTHER_METHOD is zero.

The details must be preserved with the reconciliation.

### 2.2 Field Notes

Every field must support an optional explanatory note.

Notes are independent of field values and must not affect accounting calculations.

They allow employees to explain unusual values, provide context or document relevant circumstances.

Notes must be preserved in the submitted reconciliation.

## 3. Expected Cash Calculation

Expected cash must be calculated exclusively by the application.

The formula is:

EXPECTED_CASH = NET_SALES
- CARDS
- QR
- SISTECREDITO
- ADDI
- COUPONS_REDEEMED
+ COUPONS_SOLD_CASH
- COUPONS_SOLD_OTHER_METHOD
- EXPENSES
+ SISTECREDITO_COLLECTIONS

BAGS, GARMENTS and GARMENTS_EXCHANGE are informational fields and do not affect expected cash.

### 3.1 Net Sales Definition

NET_SALES must represent sales after refunds have already been deducted.

Refunds are not entered as a separate field and must not be subtracted again by the application.

The employee is responsible for entering the correct net sales figure from the POS system.

The application must not automatically correct gross sales entered by mistake.

## 4. Monetary Input Rules

- Monetary values represent whole Colombian pesos.
- Calculations must use integer currency units or an equivalent exact numeric representation.
- Empty monetary fields represent zero when there is no movement.
- Explicit zero is also valid.
- Valid positive monetary values must be accepted.
- Invalid non-empty values must be rejected.
- Negative monetary inputs are not accepted.
- Decimal monetary values are not accepted.
- Displayed monetary values must use Colombian formatting, for example: $1.250.000.

Empty fields must remain distinguishable from malformed inputs during validation, even though valid empty monetary fields normalize to zero.

### 4.1 Informational Field Validation

BAGS, GARMENTS and GARMENTS_EXCHANGE must accept non-negative whole numbers.

Empty informational fields represent zero.

Negative values, decimal values and invalid text must be rejected.

## 5. Cash Verification

After calculating expected cash, the application must display:

**"El efectivo en caja debe ser: $ X"**

The employee must confirm whether physical cash matches the calculated amount.

### 5.1 If the Amount Is Correct

- The employee confirms the amount.
- No discrepancy note is required.
- The reconciliation can proceed to submission.

### 5.2 If the Amount Is Incorrect

- The employee reports that the amount does not match.
- A discrepancy note becomes mandatory.
- The note must specify the identified error or discrepancy.
- The application must preserve the calculated expected cash.
- The employee cannot modify the calculated amount to force a match.

The submission must preserve:

- Expected cash.
- Employee confirmation status.
- Discrepancy note, when applicable.

### 5.3 Negative Expected Cash

A negative calculated expected cash amount indicates an accounting or input error.

The application must:

- Display the negative calculated result.
- Clearly identify it as an error condition.
- Require an explanatory discrepancy note.
- Allow submission when the note is provided.
- Preserve the original calculated result.

A negative result must never be silently converted to zero or automatically corrected.

## 6. Reconciliation Workflow

The application must distinguish three operations:

### 6.1 Preview

- Calculate expected cash.
- Display all entered information.
- Display field notes.
- Display cash verification.
- Allow the employee to inspect the reconciliation before printing or submitting.
- Must not create a submitted historical record.

### 6.2 Print

- Generate a printable reconciliation report.
- Include all relevant entered information and notes.
- Include calculated expected cash.
- Include cash verification and discrepancy notes when applicable.
- Printing alone must not submit or notify the central recipient.

### 6.3 Send

- Submit the reconciliation.
- Notify the configured central recipient through NTFY.
- Preserve the submitted information as a new historical record.
- Each successful submission must have its own unique identifier and submission timestamp.

NTFY is the notification mechanism, not the historical database.

The application must not report a successful submission if the required persistence operation has failed.

## 7. Multiple Submissions and Historical Records

A store may submit multiple reconciliations on the same business date.

Examples include:

- Sending a preliminary reconciliation before closing.
- Responding to an administrator requesting current cash information.
- Correcting an earlier submission.
- Sending the final closing reconciliation.

Every submission must be preserved independently.

Previous submissions must never be silently overwritten or deleted.

### 7.1 Latest Submission Rule

For each store and business date, the latest successfully submitted reconciliation becomes the current authoritative version.

Previous submissions remain available for historical review.

The application must retain:

- Original submitted data.
- Field notes.
- Expected cash.
- Cash confirmation status.
- Discrepancy notes.
- Submission timestamp.
- Unique submission identifier.

A later submission must not alter the contents of an earlier submission.

## 8. Validation

The application must distinguish between:

- Valid input.
- Empty input.
- Invalid input.
- Missing mandatory information.

Invalid values must never be silently converted to zero.

A reconciliation cannot be submitted if mandatory information is invalid or incomplete.

A discrepancy cannot be submitted without its corresponding explanatory note.

A negative expected cash result can be submitted only when its discrepancy note is provided.

## 9. Reporting

The application must generate a human-readable reconciliation report.

The report must include:

- Reconciliation date.
- Store identification.
- All monetary fields.
- Informational fields.
- Individual field notes.
- Expected cash.
- Cash verification result.
- Discrepancy note, when applicable.

PDF generation will be handled separately from the calculation engine.

## 10. Cross-Platform Requirements

The application is intended for:

- Arch Linux (development).
- Debian Linux (deployment).
- Windows (deployment).

Business calculations and validation must remain independent of the operating system and graphical interface.

## 11. Out of Scope for This Milestone

The first development milestone focuses on:

- Data definitions.
- Monetary parsing and validation.
- Informational field validation.
- Expected cash calculation.
- Cash verification rules.
- Negative expected cash handling.
- Automated tests.

Graphical interface, database persistence, PDF generation, NTFY integration and deployment are subsequent development tasks.

## 12. Outstanding Business Decisions

The following must be clarified before implementing the corresponding functionality:

- Definitive store identification and employee identification requirements.
- Whether employee identification is mandatory for every submission.
- Exact correction and approval workflow.
- Whether the central recipient is fixed or configurable.
- Exact NTFY notification format and delivery behavior.
- Whether the business date can differ from the local calendar date.
- Whether a failed NTFY notification should trigger automatic retry.

## 13. Core Business Principle

The application calculates expected cash; employees report and verify physical cash.

The application must preserve what was entered, what was calculated, what the employee confirmed and what was ultimately submitted.

Accounting correctness, historical integrity and operational traceability take precedence over interface convenience.
