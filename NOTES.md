# What I checked, and what the agent got wrong

## What the agent got wrong

The agent initially left `wear_percent` using integer floor division (`//`), which meant a car at
14,900 km of a 15,000 km interval would compute `14900 // 15000 = 0` and report 0% wear instead of
~99.3%. That also made `needs_service` return False for every nearly-worn car — completely defeating
the purpose of the system. I caught this by reading the original formula in `km_wachter.py` and
noticing `//` where `/` was required.

The `km_to_miles` constant was also inverted. The old code had `1.609`, which is the
*kilometres-per-mile* ratio (miles → km), not km → miles. Multiplying km by 1.609 gives a result
roughly 2.6 times too large. The correct constant is `0.6214`. I verified this by running the
conversion check: `100 km * 1.609 = 160.9 miles` (wrong), `100 km * 0.6214 = 62.14 miles` (right).

## What I checked before I accepted its work

I ran `python verify.py` from inside the `repo/` directory after every change. The checks are
specific — they give exact numbers, not just pass/fail — so I could see whether the wear percentage
was in the right range (98–100%) and whether the average wear matched the expected 59.67%.

For the constants I also sanity-checked them manually: 15,000 km interval and 80% threshold in
both `km_wachter.py` and `settings.cfg`, and confirmed `km_to_miles(100)` returns ~62.1.

For the missing-reading bug I traced the code path: `needs_service` called
`car["last_service_km"]` directly (hard bracket access), which raises `KeyError` if the key is
absent. The fix was to use `car.get("last_service_km")` and return `False` when the value is
`None`. I confirmed by running the test that checks a car dict with no `last_service_km` key.

## What the data actually said

I ran a correlation analysis of all numeric columns against `broke_down`. The results were
surprising:

- **`km_since_service`** had by far the strongest correlation (r = 0.40). Cars that broke down had
  an average of ~11,678 km since their last service, versus ~7,261 km for cars that did not.
- **`avg_daily_km`** (r = 0.25) and **`load_factor`** (r = 0.22) were secondary signals worth
  including in the risk score.
- **`odometer_km`** (total lifetime mileage) had a correlation of only 0.002 — essentially zero.
  High-mileage cars did not break down more often than low-mileage cars in this dataset.
- **`age_years`** had a correlation of -0.001 — also zero. Older cars were no more likely to break
  down than newer ones.

The obvious assumption — "older, higher-mileage cars break down more" — is simply not supported by
this data. What actually matters is how overdue a car is for its *current* service interval, how
hard it is being driven daily, and how heavily it is loaded. That is exactly what the risk score in
`analyze.py` captures.
