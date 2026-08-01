# CLI reference

`payrun` reads a small, flat JSON config file (`--config`, defaulting to
`payrun.config.json` in the current directory) before dispatching to a
subcommand. Every key is required — there is no implicit default for a
missing one.

```json
{
    "database_path": "payrun.db",
    "currency": "USD",
    "plan_year": 2026,
    "frequency": "BIWEEKLY"
}
```

`frequency` is the company's pay calendar — one of `WEEKLY`, `BIWEEKLY`,
`SEMIMONTHLY`, `MONTHLY`. A `run` invocation processes employees on this
frequency for one period at a time; employees carry their own `frequency`
field too, and only those matching the config's frequency are included in
a given run.

## Commands

**`payrun employees add`** registers an employee.

```
payrun employees add --id E0007 --first-name Jordan --last-name Lee \
    --frequency BIWEEKLY --hire-date 2020-01-01 \
    --pay-type SALARIED --amount 78000.00
```

`--pay-type` is `SALARIED` or `HOURLY`; `--amount` is the annual salary or
the hourly rate accordingly, in the config's currency.

**`payrun import <csv-path>`** loads a timesheet CSV — header
`employee_id,work_date,hours`, one row per employee per day — into
storage. Re-importing the same employee and date replaces that day's
entry.

**`payrun run --period <date>`** runs payroll for the period whose start
date matches `<date>` on the configured frequency's schedule for
`plan_year`. It reads timesheet hours already imported for that date
range, computes every payslip, and persists both the payslips and the
updated year-to-date totals.

**`payrun payslip --employee <id> --period <date>`** renders one employee's
payslip from a previously run period.

**`payrun register --period <date>`** renders the whole period's register:
one row per employee, gross and net.

## Exit codes

`0` on success. `1` when a `payrun.errors.PayrunError` is raised — a
missing config key, an unreachable period, a payslip that has not been run
yet — with the message on stderr prefixed `error:`. `2` on an
argument-parsing failure, via argparse's own default behavior.
