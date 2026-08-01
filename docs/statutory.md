# Statutory parameters

Rates, exemptions, ceilings, and bracket tables are data, not code. They
live in `src/payrun/data/parameters_<plan_year>.json` and are read through
`statutory/tables.py` — no other module parses that JSON or hardcodes a
figure from it. Loading a plan year with no matching file raises
`ParameterNotFoundError` rather than falling back to a nearby year, and
`load_parameters` caches its result, so a given plan year's parameters are
parsed once per process and are immutable afterward.

## Shape of a parameters file

```json
{
    "plan_year": 2026,
    "currency": "USD",
    "pension": {"rate": "...", "exemption_annual": "...", "ceiling_annual": "..."},
    "insurance": {"rate": "...", "annual_maximum": "..."},
    "employer": {"pension_multiplier": "...", "insurance_multiplier": "..."},
    "tax": {"basic_credit_annual": "...", "brackets": [{"threshold": "...", "rate": "..."}]}
}
```

Every numeric value is a JSON string, not a JSON number — this is what lets
`Decimal(value)` parse it exactly, with no float round-trip anywhere in the
loading path.

## Pension and insurance

Both use one rate and one annual exemption or maximum. `PensionCalculator`
and `InsuranceCalculator` each take the period's gross and the employee's
year-to-date contribution, and return the smaller of "rate times this
period's taxable amount" and "whatever room is left under the annual
maximum." This keeps the running total inside the ceiling at every period —
the ceiling is a cap on what can be withheld, not a target the final period
is required to land on exactly.

## Tax brackets

`tax/brackets.py:compute_tax` walks a sorted bracket table and taxes each
slice of income at its own marginal rate, accumulating the raw, unrounded
tax across every bracket and rounding only once at the end. `tax/credits.py`
then subtracts the basic credit, floored at zero.
`tax/withholding.py:WithholdingCalculator` is the periodic method: it
annualizes the period's gross by the frequency's periods per year, taxes
the annualized figure, applies the credit, and divides back down. This is
the only withholding method in the base repository — annualize, tax,
credit, de-annualize, in that order, every time.

## Employer contributions

`statutory/employer.py:employer_share` takes an employee's already-computed
contribution and a multiplier `Rate`, and returns the scaled employer
amount, rounded at the employee contribution's exponent. It has no
awareness of pension or insurance specifically; it is the same function
either calculator's employer share goes through.
