"""Custom quotes source.

Provides a simple JSON-backed quotebook the user can edit or populate via methods.
Default location is ./settings/custom_quotebook.json.
"""

import json
import random
from pathlib import Path


class CustomQuotes:
    """Load, manage, and sample quotes from a local JSON quotebook.

    The JSON file is a mapping of lower-cased author names to lists of quotes.
    Example: {"yoda": ["Do or do not..."]}
    """

    def __init__(self, quotebook_path: str | None = None) -> None:
        """Initialize the custom quotebook.

        If quotebook_path is None, uses ./settings/custom_quotebook.json.
        Creates the file and parent folder if missing.
        """
        if quotebook_path is None:
            # Default to user-accessible settings/custom_quotebook.json in CWD
            default_path = Path.cwd() / "settings" / "custom_quotebook.json"
            self.quotebook_path = str(default_path)
        else:
            self.quotebook_path = quotebook_path
        self.quotebook = self.getQuotebook()

    def getQuotebook(self) -> dict[str, list[str]]:
        """Load the quotebook JSON or create an empty one if missing."""
        quotebook_file = Path(self.quotebook_path)
        quotebook_file.parent.mkdir(parents=True, exist_ok=True)
        if not quotebook_file.exists():
            with open(quotebook_file, "w+") as quotebook:
                json.dump({}, quotebook, indent=4)
            return {}
        else:
            with open(quotebook_file) as quotebook:
                return json.load(quotebook)

    def addQuote(self, author: str, quote: str) -> None:
        """Add a quote under an author's name (case-insensitive)."""
        if author.lower() in self.quotebook.keys():
            if not quote in self.quotebook[author.lower()]:
                self.quotebook[author.lower()].append(quote)
        else:
            self.quotebook[author.lower()] = [quote]

    def removeQuote(self, author: str, quote: str) -> None:
        """Remove a specific quote for an author; drop author if list becomes empty."""
        if author.lower() in self.quotebook.keys():
            self.quotebook[author.lower()].remove(quote)
            if not self.quotebook[author.lower()]:
                self.removeAuthor(author=author)
        else:
            raise KeyError(
                f"{author}'s quotes does not exist in this quotebook.")

    def removeAuthor(self, author: str) -> None:
        """Remove an author entirely from the quotebook."""
        if author.lower() not in self.quotebook:
            raise KeyError(f"{author}'s quotes does not exist in this quotebook.")
        self.quotebook.pop(author.lower())

    def writeQuotebook(self) -> None:
        """Persist the current quotebook to disk."""
        with open(self.quotebook_path, "w+") as quotebook:
            json.dump(self.quotebook, quotebook, indent=4)

    def getRandom(self) -> tuple[str, str] | tuple[()]:
        """Return a random (quote, author) pair or empty tuple if none exist."""
        if self.quotebook:
            author = random.choice(list(self.quotebook.keys()))
            quote = random.choice(self.quotebook[author])
            return (quote, author.title())
        else:
            return ()


def main():
    quotes = CustomQuotes()
    quotes.addQuote(
        "Yoda",  "You must unlearn what you have learned. Try not. Do. Or do not. There is no try.")
    quotes.addQuote(
        "Yoda",  "There is no try.")
    quotes.writeQuotebook()
    print(quotes.getRandom())


if __name__ == "__main__":
    main()
