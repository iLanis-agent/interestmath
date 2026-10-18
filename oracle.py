#!/usr/bin/env python3
# Interest Math oracle - mirrors engine.js.
import json, math

def _c(x, msg, lo, hi, allow_zero):
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or x < lo or x > hi or (not allow_zero and x == 0):
        raise ValueError(msg)
    return math.floor(x * 100 + 0.5)

def _whole(x, msg, lo, hi):
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) or math.floor(x) != x or x < lo or x > hi:
        raise ValueError(msg)
    return int(x)

def _fmt(h):
    whole, frac = divmod(h, 100)
    if frac == 0:
        return str(whole)
    f = f"{frac:02d}"
    if f[1] == "0":
        f = f[0]
    return f"{whole}.{f}"

def _money(c):
    whole, frac = divmod(c, 100)
    return f"{whole:,}.{frac:02d}"

def _n(x):
    if x not in (1, 2, 4, 12) or isinstance(x, bool):
        raise ValueError("compounding must be 1, 2, 4 or 12 times a year")
    return int(x)

def _freq(n):
    return {1: "yearly", 2: "twice a year", 4: "four times a year", 12: "monthly"}[n]

def _years(y):
    return f"{y} year" if y == 1 else f"{y} years"

def _grow(amount, num, den, k):
    top = amount * num ** k; bottom = den ** k
    return (2 * top + bottom) // (2 * bottom)

def growth_truth(principal, rate, years, per_year):
    p = _c(principal, "principal must be above 0 and at most 1000000", 0, 1000000, False)
    r = _c(rate, "rate must be between 0 and 20", 0, 20, True)
    y = _whole(years, "years must be a whole number from 1 to 30", 1, 30)
    n = _n(per_year)
    simple = (2 * p * (10000 + r * y) + 10000) // 20000
    comp = _grow(p, 10000 * n + r, 10000 * n, y * n)
    head = f"{_money(p)} at {_fmt(r)}% for {_years(y)}: simple interest ends at {_money(simple)}; compounding {_freq(n)} ends at {_money(comp)}. "
    if comp > simple:
        return head + f"Compounding adds {_money(comp - simple)} over simple interest."
    return head + "The two end at the same amount."

def double_truth(rate, per_year):
    r = _c(rate, "rate must be from 0.1 to 100", 0.1, 100, True)
    n = _n(per_year)
    num = 10000 * n + r; den = 10000 * n; top = 1; bottom = 1; periods = 0
    while top < 2 * bottom:
        top *= num; bottom *= den; periods += 1
    lead = f"At {_fmt(r)}% compounded {_freq(n)}, a balance first reaches double after "
    if n == 1:
        return lead + _years(periods) + "."
    yrs = (2 * periods * 100 + n) // (2 * n)
    return lead + f"{periods} periods (about {_fmt(yrs)} years)."

def rate_truth(start, end, years):
    s = _c(start, "start amount must be above 0 and at most 1000000", 0, 1000000, False)
    e = _c(end, "end amount must be between 0 and 1000000000", 0, 1000000000, True)
    y = _whole(years, "years must be a whole number from 1 to 50", 1, 50)
    if e < s:
        raise ValueError("end amount must be at least the start amount")
    ok = lambda r: s * (10000 + r) ** y >= e * 10000 ** y
    if not ok(100000):
        raise ValueError("the rate needed is over 1000%")
    lo, hi = 0, 100000
    while lo < hi:
        mid = (lo + hi) // 2
        if ok(mid):
            hi = mid
        else:
            lo = mid + 1
    return f"To turn {_money(s)} into {_money(e)} in {_years(y)}, the least yearly rate is {_fmt(lo)}%, compounded yearly."

FNS = {"growthTruth": growth_truth, "doubleTruth": double_truth, "rateTruth": rate_truth}

CASES = [
    ("growthTruth", [100000, 5, 10, 12]), ("growthTruth", [1000, 5, 1, 1]), ("growthTruth", [1000, 0, 5, 12]),
    ("growthTruth", [1000, 5, 10, 1]), ("growthTruth", [1000, 5, 10, 2]), ("growthTruth", [1000, 5, 10, 4]),
    ("growthTruth", [1000000, 20, 30, 12]), ("growthTruth", [0.01, 0.01, 2, 12]), ("growthTruth", [1.5, 3, 30, 12]),
    ("growthTruth", [250.75, 4.25, 7, 4]), ("growthTruth", [0, 5, 10, 12]), ("growthTruth", [1000001, 5, 10, 12]),
    ("growthTruth", [1000, 21, 10, 12]), ("growthTruth", [1000, -1, 10, 12]), ("growthTruth", [1000, 5, 0, 12]),
    ("growthTruth", [1000, 5, 31, 12]), ("growthTruth", [1000, 5, 2.5, 12]), ("growthTruth", [1000, 5, 10, 3]),
    ("doubleTruth", [7, 1]), ("doubleTruth", [7, 12]), ("doubleTruth", [100, 1]), ("doubleTruth", [100, 12]),
    ("doubleTruth", [1, 1]), ("doubleTruth", [3.5, 4]), ("doubleTruth", [0.5, 2]), ("doubleTruth", [0.01, 1]), ("doubleTruth", [0.1, 12]), ("doubleTruth", [0.1, 1]), ("doubleTruth", [0.09, 1]),
    ("doubleTruth", [0, 1]), ("doubleTruth", [101, 1]), ("doubleTruth", [7, 365]),
    ("rateTruth", [10000, 20000, 10]), ("rateTruth", [1000, 1000, 5]), ("rateTruth", [1000, 1000.01, 1]),
    ("rateTruth", [1000, 1100, 1]), ("rateTruth", [1, 1000000, 50]), ("rateTruth", [1000, 500, 5]),
    ("rateTruth", [1000, 2000, 0]), ("rateTruth", [1000, 2000, 51]), ("rateTruth", [0, 2000, 5]),
    ("rateTruth", [1000, 1000000001, 5]), ("rateTruth", [1, 1000000, 1]), ("rateTruth", [50000, 120000, 12]),
]

out = []
for fn, args in CASES:
    try:
        exp = FNS[fn](*args)
    except ValueError as e:
        exp = "ERR:" + str(e)
    out.append({"fn": fn, "args": args, "expected": exp})
with open("expected.json", "w") as f:
    json.dump(out, f, indent=1)
    f.write("\n")
print(len(out), "cases")
