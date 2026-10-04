# km_wachter.py
# KM-Waechter decides when a Vossberg Mobility car needs a service.
# Written in 2013. Modernized and bugs fixed.

SERVICE_INTERVAL_KM: int = 15000
WARN_AT_PERCENT: int = 80


def wear_percent(km_since_service: float, interval: int) -> float:
    """Return the percentage of the service interval that has been consumed.

    Uses true division so a car at 14,900 of 15,000 km correctly shows ~99.3 %,
    not 0 % as the old floor-division version did.
    """
    return (km_since_service / interval) * 100


def needs_service(car: dict) -> bool:
    """Return True if the car has consumed >= WARN_AT_PERCENT of its service interval.

    A car with no recorded last-service reading (key absent) is treated as freshly
    serviced rather than falsely flagged as overdue.
    """
    last = car.get("last_service_km")
    if last is None:
        return False
    km_since = car["odometer"] - last
    pct = wear_percent(km_since, SERVICE_INTERVAL_KM)
    return pct >= WARN_AT_PERCENT


def check_fleet(fleet: list[dict]) -> list[str]:
    """Flag and print every car that needs a service; return their IDs."""
    flagged = []
    for car in fleet:
        if needs_service(car):
            flagged.append(car["id"])
            print(f"SERVICE DUE: {car['id']}")
    return flagged
