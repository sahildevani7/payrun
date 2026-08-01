# Running a pay period

`run/engine.py:PayRunEngine.run` is the single entry point that turns a
list of employees, a pay period, and a map of hours worked into a
`PayRunResult`. This is what `payrun run` calls, and what any other caller
should call rather than re-deriving the sequence below.

## What happens, in order

1. **Validate.** `run/validation.py:validate_run` checks the run before any
   money moves: no duplicate employee ids, every employee active on the
   period's end date, and an hours entry present for every hourly
   employee. A failure here raises `RunError` before any calculation runs.
2. **Compute earnings.** For a salaried employee this is the annual amount
   divided by the frequency's periods per year. For an hourly employee, the
   engine splits the reported hours into a regular portion (capped at the
   configured weekly overtime threshold) and an overtime portion above it,
   so straight-time pay is never double-counted under the overtime
   premium.
3. **Compute statutory withholding.** Pension and insurance both take the
   period's gross and the employee's year-to-date contribution so far, and
   cap the current period's amount at whatever room remains under the
   annual maximum — the running total across a year can fall short of the
   maximum by a few cents through ordinary rounding, but it never exceeds
   it. Tax withholding annualizes the period's gross, taxes it against the
   bracket table, applies the basic credit, and divides back down to a
   per-period figure.
4. **Apply voluntary deductions.** Any deduction codes named for the
   employee in `voluntary_codes_by_employee` are looked up in the
   `DeductionRegistry` and calculated against gross, alongside the three
   statutory lines.
5. **Compute employer contributions.** The employer's pension and
   insurance shares are the employee's contributions scaled by the
   configured multipliers — a straight percentage of what the employee
   paid, not an independent calculation.
6. **Record year-to-date totals** for the employee, then build the
   `PaySlip`: earnings sorted by code, deductions sorted by code, employer
   contributions, gross, and net.

## What the base engine does not do

It runs one frequency at a time. An employee's own `frequency` field
supports per-employee pay calendars in the domain model, but a single
`PayRunEngine.run` call processes the employees on one frequency for one
period — the way a business with a single pay calendar actually runs
payroll. It also does not persist anything; `SqlitePayRunRepository` and
`save_ytd_store` are separate, explicit steps the CLI's `run` command takes
after the engine returns.
