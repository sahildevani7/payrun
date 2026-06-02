# payrun

A gross-to-net payroll engine with a command-line interface.

`payrun` holds an employer's employees and pay calendar, ingests timesheet
CSVs, runs a pay period end to end, persists results to SQLite, maintains
year-to-date accumulators, and renders pay statements and a pay-run register.

## Install

```
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Requires Python 3.12.

## Usage

```
payrun employees add --id E0007 --name "Jordan Lee" --frequency BIWEEKLY --rate 32.50
payrun import timesheet.csv
payrun run --period 2026-03-01
payrun payslip --employee E0007 --period 2026-03-01
payrun register --period 2026-03-01
```

Run `payrun --help` or `payrun <command> --help` for the full option list.

## Design

- **Money is exact.** All monetary arithmetic goes through `payrun.money.Money`,
  a `Decimal`-backed value type. No `float` ever touches an amount.
- **Statutory parameters are data.** Rates, exemptions, ceilings, and bracket
  tables live under `src/payrun/data/` as versioned JSON, loaded through
  `payrun.statutory.tables`. Calculation code never hardcodes a figure.
- **Time is injected.** Every date-consuming call takes a `payrun.clock.Clock`.
  Only `SystemClock` reads the real clock, so runs are reproducible in tests.
- **Storage is SQLite** with a small forward-only migration runner and an
  explicit unit-of-work boundary around each write.

## Development

```
pytest
ruff check src tests
mypy
```

See `CLAUDE.md` for the conventions this codebase follows.
