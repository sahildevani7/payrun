# Architecture

`payrun` is a library first and a CLI second. Every command in
`src/payrun/cli/` is a thin wrapper around calls that work identically from
a Python shell, a test, or a script.

## Package layout

```
src/payrun/
├── money.py, rate.py, hours.py, rounding.py   exact value types over Decimal
├── ids.py, clock.py, errors.py, config.py     shared primitives
├── calendarx/                                 pay frequencies and schedules
├── people/                                    employees, employment, compensation
├── storage/                                   SQLite engine, migrations, repositories
├── earnings/                                  earning codes, lines, calculators
├── deductions/                                deduction codes, lines, calculators
├── statutory/                                 parameter tables, pension, insurance, employer share
├── tax/                                       bracket table, credits, withholding
├── run/                                       the pay-run engine, results, validation, YTD
├── importers/                                 timesheet ingestion
├── reporting/                                 pay slip and register rendering
└── cli/                                       argument parsing and command handlers
```

Each package below `payrun/` owns exactly one concern and depends only on
packages above it in this list, plus the shared primitives. `run/engine.py`
is the only module that reaches into every other package — it is the
orchestrator, not a library of its own logic.

## Value types over side effects

Every domain quantity is a value type: `Money`, `Rate`, `Hours`, the id
types, `EarningLine`, `DeductionLine`, `PaySlip`. They are immutable
(`@dataclass(frozen=True)` or a hand-written equivalent) and validate
themselves once at construction. Code that holds one of these values never
re-validates it — the type is the proof.

Two consequences follow from this:

- Comparisons and arithmetic between mismatched types (two currencies, two
  id kinds) raise immediately rather than coercing silently.
- A function that accepts a `Money` or an `Hours` argument does not need a
  defensive check at the top — the caller could not have constructed an
  invalid one.

## Seams

A seam is a registry with exactly one real entry: `earnings/registry.py`,
`deductions/registry.py`, `importers/registry.py`, `reporting/renderer.py`.
Each defines a `Protocol` and a registration mechanism. The base repository
ships one or two implementations per seam — enough to prove the pattern
works, not a menu of interchangeable options. Extending the domain means
writing a new implementation and registering it; nothing about the
registries themselves needs to change.

## Determinism

Nothing in `src/payrun/` reads the system clock or an unseeded random
source outside of `clock.SystemClock`, which exists precisely so that
everything else can take a `Clock` argument instead. Rendered output —
payslip lines, register rows — is built from tuples that are already
sorted by code or by employee id before they reach the renderer, so two
runs against the same data produce byte-identical text.

## Storage

`storage/engine.py` is the only module that calls `sqlite3.connect`.
Schema changes are forward-only migrations under `storage/migrations/`,
applied in a fixed order and tracked in a `schema_migrations` table.
Repositories translate between domain value types and rows; nothing above
the storage layer sees a `sqlite3.Row` or writes SQL.
