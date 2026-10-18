// Interest Math engine - simple vs compound growth, time to double, and the rate between two amounts.
// Mirrored by oracle.py; keep the op order identical.
// Money is rounded to cents and rates to hundredths of a percent on the way in. Rounding is half up.
// Compounding is exact integer (BigInt) arithmetic, rounded to the cent once at the end.

function _c(x, msg, min, max, allowZero) {
  if (typeof x !== "number" || !isFinite(x) || x < min || x > max || (!allowZero && x === 0)) throw new Error(msg);
  return Math.floor(x * 100 + 0.5);
}

function _whole(x, msg, min, max) {
  if (typeof x !== "number" || !isFinite(x) || Math.floor(x) !== x || x < min || x > max) throw new Error(msg);
  return x;
}

function _fmt(h) {
  var whole = Math.floor(h / 100), frac = h % 100;
  if (frac === 0) return String(whole);
  var f = (frac < 10 ? "0" : "") + frac;
  if (f.charAt(1) === "0") f = f.charAt(0);
  return whole + "." + f;
}

function _money(c) {
  var whole = String(Math.floor(c / 100)), frac = c % 100;
  var out = "";
  while (whole.length > 3) { out = "," + whole.slice(-3) + out; whole = whole.slice(0, -3); }
  return whole + out + "." + (frac < 10 ? "0" : "") + frac;
}

function _n(x) {
  if (x !== 1 && x !== 2 && x !== 4 && x !== 12) throw new Error("compounding must be 1, 2, 4 or 12 times a year");
  return x;
}

function _freq(n) {
  return n === 1 ? "yearly" : n === 2 ? "twice a year" : n === 4 ? "four times a year" : "monthly";
}

function _years(y) {
  return y + (y === 1 ? " year" : " years");
}

// numerator * (num/den)^k / denominator, rounded half up, in exact integers.
function _grow(amount, num, den, k) {
  var top = amount * num ** BigInt(k), bottom = den ** BigInt(k);
  return (2n * top + bottom) / (2n * bottom);
}

// The growth truth: simple interest next to compound interest on the same money.
function growthTruth(principal, rate, years, perYear) {
  var p = _c(principal, "principal must be above 0 and at most 1000000", 0, 1000000, false);
  var r = _c(rate, "rate must be between 0 and 20", 0, 20, true);
  var y = _whole(years, "years must be a whole number from 1 to 30", 1, 30);
  var n = _n(perYear);
  var simple = Math.floor((2 * p * (10000 + r * y) + 10000) / 20000);
  var comp = Number(_grow(BigInt(p), BigInt(10000 * n + r), BigInt(10000 * n), y * n));
  var head = _money(p) + " at " + _fmt(r) + "% for " + _years(y) + ": simple interest ends at " + _money(simple) + "; compounding " + _freq(n) + " ends at " + _money(comp) + ". ";
  if (comp > simple) return head + "Compounding adds " + _money(comp - simple) + " over simple interest.";
  return head + "The two end at the same amount.";
}

// The double truth: periods until a balance first reaches twice its start.
function doubleTruth(rate, perYear) {
  var r = _c(rate, "rate must be from 0.1 to 100", 0.1, 100, true);
  var n = _n(perYear);
  var num = BigInt(10000 * n + r), den = BigInt(10000 * n), top = 1n, bottom = 1n, periods = 0;
  while (top < 2n * bottom) { top *= num; bottom *= den; periods++; }
  var lead = "At " + _fmt(r) + "% compounded " + _freq(n) + ", a balance first reaches double after ";
  if (n === 1) return lead + _years(periods) + ".";
  var yrs = Math.floor((2 * periods * 100 + n) / (2 * n));
  return lead + periods + " periods (about " + _fmt(yrs) + " years).";
}

// The rate truth: the least yearly rate, to hundredths of a percent, that turns one amount into another.
function rateTruth(start, end, years) {
  var s = _c(start, "start amount must be above 0 and at most 1000000", 0, 1000000, false);
  var e = _c(end, "end amount must be between 0 and 1000000000", 0, 1000000000, true);
  var y = _whole(years, "years must be a whole number from 1 to 50", 1, 50);
  if (e < s) throw new Error("end amount must be at least the start amount");
  var S = BigInt(s), E = BigInt(e), base = 10000n, Y = BigInt(y);
  function ok(r) { return S * (base + BigInt(r)) ** Y >= E * base ** Y; }
  if (!ok(100000)) throw new Error("the rate needed is over 1000%");
  var lo = 0, hi = 100000;
  while (lo < hi) {
    var mid = Math.floor((lo + hi) / 2);
    if (ok(mid)) hi = mid; else lo = mid + 1;
  }
  return "To turn " + _money(s) + " into " + _money(e) + " in " + _years(y) + ", the least yearly rate is " + _fmt(lo) + "%, compounded yearly.";
}
