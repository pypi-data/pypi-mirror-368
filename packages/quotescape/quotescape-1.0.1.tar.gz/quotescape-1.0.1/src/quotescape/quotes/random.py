"""Random quotes source backed by quotable.io."""

import requests
import json
from typing import Any


class RandomQuotes:

    def __init__(self, url: str = "https://api.quotable.io/quotes/random") -> None:
        """Configure the API endpoint for random quotes."""
        self.url = url

    def fetchData(self) -> list[dict[str, Any]]:
        """Fetch a random quote from the API.

        Returns a list with one object; raises TimeoutError on network issues.
        """
        timeout = 10
        try:
            resp = requests.get(self.url, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise TimeoutError("Could not connect to the quotable API") from e

    def getRandom(self) -> tuple[str, str]:
        """Return a (quote, author) pair from the API response."""
        data = self.fetchData()
        return (data[0]['content'], data[0]['author'])


def main():
    random_quote = RandomQuotes()
    print(random_quote.getRandom())


if __name__ == "__main__":
    main()
