# Working in this repository

Guidance for anyone (human or automated tool) making changes here.

## Commits

- Commit messages are a single line: imperative mood, under ~70 characters, no
  trailing period. No body, no bullet list, no multi-paragraph explanation.
- Never add a co-author trailer, a "generated with" footer, or any assistance
  attribution to a commit message, PR description, or code comment.
- Run the full test suite and confirm it is green before committing.
- Never push automatically. Commit locally and leave pushing to the repository
  owner unless explicitly asked to push.

## Determinism

- All dates and times come from an injected `Clock` (see `payrun.clock`).
  Never call `datetime.now()` or `date.today()` directly outside `SystemClock`.
- All randomness comes from an explicitly seeded generator. No module-level
  `random` use.
- No network access anywhere, including in tests.
- Any output derived from a dict or set must be sorted before rendering. Line
  ordering on a payslip, row ordering in a register, and key ordering in
  rendered output are part of the public contract.
- Tests build their own in-memory database. No shared mutable fixtures, no
  ordering dependence between tests.

## Money and quantities

- All money arithmetic goes through `payrun.money.Money`. Never use raw `float`
  for an amount. Never mix rounding policies implicitly — pass the rounding mode
  explicitly at the boundary that requires it.
- Rounding is to the currency's smallest unit, taken from the currency's
  exponent. Never hardcode two decimal places.
- Rates and percentages use `payrun.rate.Rate`, hours use `payrun.hours.Hours`.
  Both are exact over `Decimal`. A rate is never a `float` and never a bare
  string.
- A calculation that combines multiple `Money` values requires them to share a
  currency, and raises rather than coercing.

## Statutory parameters

- Rates, exemptions, ceilings, bracket tables, and credit amounts live in the
  parameter files under `src/payrun/data/` and are read through
  `payrun.statutory.tables`. No calculation module hardcodes a jurisdiction
  figure.
- Parameter files are keyed by plan year. Loading a year that is not present
  raises a typed error rather than falling back to the nearest year.
- Loaded parameters are immutable in memory.

## Errors

- Every failure raises from the hierarchy in `payrun.errors`. No bare
  `ValueError`, no `assert` used for validation, no returning `None` to signal a
  problem.
- Validation happens at the boundary. Once a value is inside a domain type it is
  assumed valid.

## Tests

- Tests live in `tests/` only. Never co-locate a test module with the source
  module it exercises, and never add doctests to a source module.
- Tests assert through public APIs and observable output, not private helpers.

## Naming

- No module may shadow a standard library name. The pay calendar package is
  `calendarx` for exactly this reason.

## Code hygiene

- No `TODO` or `FIXME` comments describing unimplemented features. If it isn't
  built, it isn't mentioned in a comment.
- No dead code: every protocol, registry, and abstract base has at least one
  real implementation in active use.
- Dependencies are pinned to exact versions in `pyproject.toml`.
- Public API is what `payrun/__init__.py` exports. Anything new that is part of
  the supported surface is exported there.
- `ruff` and `mypy` must be clean before committing.
