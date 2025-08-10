"""Quotescape CLI entry point.

Loads configuration, selects a quote source (Kindle/custom/random), renders
the wallpaper, and optionally sets it as the system background.
"""

import argparse
import logging
from quotescape.quotes.custom import CustomQuotes
from quotescape.quotes.kindle import KindleQuotes
from quotescape.parsers.yamlconfig import YamlConfigParser
from quotescape.quotes.random import RandomQuotes
from quotescape.render.wallpaper import Wallpaper


def runQuotescape(quotescape: Wallpaper):
    """Save the rendered image and set it as wallpaper using platform helpers."""
    quotescape.saveImage()
    quotescape.setWallpaper()


def main(parseType: str = "yaml"):
    """Main CLI for quotescape.

    Options (parsed via argparse):
    --browser: preferred browser for Kindle login (overrides env)
    --login-timeout: seconds to wait for login/2FA
    """
    parser = argparse.ArgumentParser(description="Quotescape CLI")
    parser.add_argument("--browser", dest="browser", help="Browser to use for Kindle login (chrome, firefox, edge, safari, system)")
    parser.add_argument("--login-timeout", dest="login_timeout", type=int, help="Timeout (seconds) to wait for login/2FA to complete")
    parser.add_argument("--verbose", dest="verbose", action="store_true", help="Enable debug logging")
    args, unknown = parser.parse_known_args()

    # Minimal logging setup
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s"
    )

    if parseType == "yaml":
        config = YamlConfigParser()

    if config.quote_type == "kindle":
        quote, book, author, cover_url = KindleQuotes(browser=args.browser, login_timeout=args.login_timeout).getRandom()
    elif config.quote_type == "random":
        quote, author = RandomQuotes().getRandom()
        book = None
        cover_url = None
    elif config.quote_type == "custom":
        quote, author = CustomQuotes(
            quotebook_path=config.custom_quotebook_path).getRandom()  # type: ignore
        book = None
        cover_url = None

    wallpaper = Wallpaper(
        quote=quote,
        book=book if config.quote_type == "kindle" else None,
        author=author,
        cover_url=cover_url if config.quote_type == "kindle" else None,
        wallpaper_path=config.wallpaper_path,
        width=config.width,
        height=config.height,
        dark_mode=bool(config.dark_mode),
        background_color=str(config.background_color),
        quote_text_color=str(config.quote_text_color),
        book_text_color=str(config.title_text_color),
        author_text_color=str(config.author_text_color),
        show_book_cover=bool(
            config.show_book_cover) if config.quote_type == "kindle" else False,
        show_title=bool(config.show_title),
        show_author=bool(config.show_author)
    )

    runQuotescape(quotescape=wallpaper)


if __name__ == "__main__":
    main()
