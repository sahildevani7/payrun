#!/usr/bin/env bash
# Walks through the vertical slice in a scratch directory: add two
# employees, import a timesheet, run March 2026, then render a payslip
# and the register. Requires `pip install -e .` to have been run first.

set -euo pipefail

workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT

config="$workdir/payrun.config.json"
cat > "$config" <<JSON
{
    "database_path": "$workdir/payrun.db",
    "currency": "USD",
    "plan_year": 2026,
    "frequency": "MONTHLY"
}
JSON

timesheet="$workdir/timesheet.csv"
cat > "$timesheet" <<CSV
employee_id,work_date,hours
E0002,2026-03-02,8.00
E0002,2026-03-03,8.00
CSV

payrun --config "$config" employees add --id E0001 --first-name Jordan \
    --last-name Lee --frequency MONTHLY --hire-date 2020-01-01 \
    --pay-type SALARIED --amount 78000.00

payrun --config "$config" employees add --id E0002 --first-name Ada \
    --last-name Okafor --frequency MONTHLY --hire-date 2020-01-01 \
    --pay-type HOURLY --amount 30.00

payrun --config "$config" import "$timesheet"
payrun --config "$config" run --period 2026-03-01
payrun --config "$config" payslip --employee E0001 --period 2026-03-01
echo "---"
payrun --config "$config" register --period 2026-03-01
