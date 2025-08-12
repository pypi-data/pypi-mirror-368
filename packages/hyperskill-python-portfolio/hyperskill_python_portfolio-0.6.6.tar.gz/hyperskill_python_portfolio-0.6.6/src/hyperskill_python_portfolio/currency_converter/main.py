"""Currency Converter."""

from __future__ import annotations

import requests

BASE_URL = "https://www.floatrates.com/daily/{code}.json"


def main() -> None:
    """Processes currency conversion requests with caching to improve efficiency."""
    source_code = input().lower()
    url = BASE_URL.format(code=source_code)
    response = requests.get(url, timeout=10)
    data = response.json()

    rates = {}
    if source_code != "usd":
        rates["usd"] = data["usd"]["rate"]
    if source_code != "eur":
        rates["eur"] = data["eur"]["rate"]

    while target_code := input().lower():
        amount = int(input())

        print("Checking the cache...")
        rate = rates.get(target_code, 0)
        if rate:
            print("Oh! It is in the cache!")
        else:
            print("Sorry, but it is not in the cache!")
            rate = data[target_code]["rate"]
            rates[target_code] = rate

        print(f"You received {amount * rate:.2f} {target_code.upper()}.")


if __name__ == "__main__":
    main()
