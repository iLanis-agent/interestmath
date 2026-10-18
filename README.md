# Interest Math

Interest arithmetic. Compound interest is simple interest plus interest on the interest.

## What it computes

- **The growth truth** - simple interest next to compound interest (yearly, twice a year, four times a year or monthly) on the same money.
- **The double truth** - how many periods a balance takes to first reach twice its start.
- **The rate truth** - the least yearly rate, to hundredths of a percent, that turns one amount into another.

Compounding is exact integer arithmetic, rounded to the cent once at the end.

## Boundary

Arithmetic only, not a forecast. Interest Math leaves out fees, taxes and inflation, and real accounts may compound or round differently. Check the terms of the account itself.

## Files

- `index.html` - landing page.
- `app.html` - the interactive calculator.
- `engine.js` - the arithmetic.
- `oracle.py` - the Python mirror that generates `expected.json`.
- `test.js` - compares every engine output against `expected.json` (44 cases).
- `expected.json` - the golden answers.

## Test

```
python3 oracle.py
node test.js
```

Live: https://ilanis-agent.github.io/interestmath/
Repo: https://github.com/iLanis-agent/interestmath
