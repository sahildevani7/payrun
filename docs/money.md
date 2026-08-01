# Money, rates, and hours

## `Money`

`Money` wraps a `Decimal` amount and a currency code. It never wraps a
`float`. Each currency carries a minor-unit exponent in
`CURRENCY_EXPONENTS` — 2 for USD, CAD, GBP, and EUR, 0 for JPY — but a
`Money` value is not forced onto that exponent at construction. Arithmetic
between two `Money` values (`+`, `-`, comparisons) requires the same
currency and raises `CurrencyMismatchError` otherwise. Multiplication by an
`int` or `Decimal` scalar is allowed; multiplication by a `bool` or `float`
is rejected, since a `bool` is a subtype of `int` in Python and would
otherwise pass silently.

Rounding is never implicit. `Money.rounded(mode)` takes an explicit
`RoundingMode` and returns a new, rounded `Money`. `to_minor_units()`
converts to an integer count of the currency's smallest unit, and raises if
the amount is not already exact at that exponent — this is what
`allocate()` uses internally to guarantee its shares sum to an exact whole.

## `allocate()`

`allocate(total, weights)` splits a `Money` value proportionally using the
largest-remainder method: each share is floored to its integer minor-unit
count, then the leftover units are handed out one at a time to the shares
with the largest fractional remainder, breaking ties by ascending index.
The shares always sum to exactly `total` — this is the one rounding-residue
rule the base repository ships, and it is deliberately the *only* one.
Nothing here decides where a *different* kind of residue should land; that
is decided per use case, by the code that calls `allocate`.

## `Rate`

`Rate` holds a non-negative `Decimal` fraction — `0.0525` for 5.25%, not a
`float` and not a percentage integer. `Rate.of(money)` returns the exact,
unrounded product as a `Decimal`; the caller rounds explicitly at whatever
exponent the situation calls for. A `Rate` can exceed 1 — an employer
multiplier of 1.4 is a valid `Rate`, not a special case.

## `Hours`

`Hours` holds a non-negative `Decimal` that must be an exact multiple of a
quarter hour. This is enforced once, at construction, so every downstream
consumer — earnings calculators, timesheet importers, overtime
calculations — can assume the invariant rather than re-checking it.

## Rounding

`rounding.py` exposes exactly two modes, `HALF_UP` and `HALF_EVEN`, over
`round_to_exponent(amount, exponent, mode)`. Every calculation module in
this repository picks one explicitly at the point it rounds; there is no
default rounding mode anywhere, by design.
