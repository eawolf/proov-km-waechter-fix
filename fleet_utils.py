# fleet_utils.py
# Helpers for KM-Waechter. Cleaned up 2024: removed dead code, fixed km→miles constant.

MILES_PER_KM: float = 0.6214          # 1 km = 0.6214 miles (was 1.609, which is miles→km — inverted)


def km_to_miles(km: float) -> float:
    """Convert kilometres to miles.

    Note: used by the nightly run for the UK partner report.
    """
    return km * MILES_PER_KM


def format_number(value: float) -> str:
    """Format a float to one decimal place."""
    return f"{value:.1f}"
