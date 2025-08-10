"""Wallpaper rendering utilities.

Takes a quote (and optionally title/author/cover) and renders a wallpaper PNG,
with helpers to set it as the desktop background across platforms.
"""

from __future__ import annotations

import ctypes
import math
import os
import platform
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from importlib.resources import files, as_file
import textwrap
import random
import requests
from io import BytesIO
import logging

from quotescape.quotes.kindle import KindleQuotes


class Wallpaper:
    """Render a quote-based wallpaper and set it as desktop background."""
    def __init__(self,
                 quote: str,
                 book=None,
                 author=None,
                 cover_url=None,
                 wallpaper_path: str = f'{os.getcwd()}/wallpaper',
                 width: int = 7680,
                 height: int = 4320,
                 dark_mode: bool = True,
                 background_color: str = "#1E1E2E",
                 quote_text_color: str = "#CBA6F7",
                 book_text_color: str = "#CDD6F4",
                 author_text_color: str = "#A6ADC8",
                 show_book_cover: bool = True,
                 show_title: bool = True,
                 show_author: bool = True,
                 ):

        self.default_width = 7680
        self.default_height = 4320

        self.width = width
        self.height = height

        self.quote = quote
        if not self.quote:
            raise ValueError("Provided empty quote.")
        self.book = book
        self.author = author
        self.cover_url = cover_url

        # Package assets namespace
        self.assets_pkg = "quotescape.assets"

        self.dark_mode = dark_mode
        self.background_color = background_color
        self.quote_text_color = quote_text_color

        if not dark_mode:
            self.background_color = "#EFF1F5"
            self.quote_text_color = "#8839EF"

        self.quote_font_size = 110

        if self.width != self.default_width and self.height != self.default_height:
            scale = math.sqrt(self.width * self.height) / math.sqrt(self.default_width * self.default_height)
            self.quote_font_size = int(self.quote_font_size * scale)

        # Load fonts from packaged assets
        regular_font_res = files(self.assets_pkg + ".fonts").joinpath("B612-Regular.ttf")
        with as_file(regular_font_res) as font_path:
            self.quote_font = ImageFont.truetype(str(font_path), int(self.quote_font_size))

        if not self.cover_url:
            self.show_book_cover = False
        else:
            self.show_book_cover = show_book_cover

        if not self.book:
            self.show_title = False
        else:
            self.show_title = show_title

        if not self.author:
            self.show_author = False
        else:
            self.show_author = show_author

        if self.show_title:
            self.book_text_color = book_text_color
            if not dark_mode:
                self.book_text_color = "#4C4F69"

        if self.show_author:
            self.author_text_color = author_text_color
            if not dark_mode:
                self.author_text_color = "#6C6F85"

        if self.show_title or self.show_author:
            self.book_author_font_size = 60
            if self.width != self.default_width and self.height != self.default_height:
                scale = math.sqrt(self.width * self.height) / math.sqrt(self.default_width * self.default_height)
                self.book_author_font_size = int(self.book_author_font_size * scale)

            italic_font_res = files(self.assets_pkg + ".fonts").joinpath("B612-Italic.ttf")
            with as_file(italic_font_res) as font_path:
                self.book_author_font = ImageFont.truetype(str(font_path), int(self.book_author_font_size))

        self.wallpaper_path = wallpaper_path
        os.makedirs(self.wallpaper_path, exist_ok=True)
        self.filename = self.wallpaper_path + \
            "/quotescape{}.png".format(random.randint(0000, 9999))

        self.image, self.draw = self.generateBackground()

    def generateBackground(self) -> tuple:
        """Create a new image with the selected background color."""
        image = Image.new(
            'RGB', (self.width, self.height), self.background_color)
        draw = ImageDraw.Draw(image)
        return image, draw

    def saveImage(self):
        """Write the drawn image to disk, replacing prior quotescape outputs."""
        self.writeText()
        keyword = "quotescape"
        for filename in os.listdir(self.wallpaper_path):
            if keyword in filename:
                os.remove(os.path.abspath(
                    os.path.join(self.wallpaper_path, filename)))
        self.image.save(self.filename)

    def getBookCover(self, cover_url):
        """Return a file-like cover image; fallback to packaged defaults on failure."""
        try:
            response = requests.get(cover_url)
            return BytesIO(response.content)
        except Exception:
            # Fallback to packaged default covers
            res = "default-dark-mode-book-cover.png" if self.dark_mode else "default-light-mode-book-cover.png"
            cover_res = files(self.assets_pkg).joinpath(res)
            with as_file(cover_res) as p:
                return str(p)

    def writeText(self) -> None:
        """Draw quote text and optional book/author and cover image."""
        wrapper = textwrap.TextWrapper(width=100)
        if self.show_book_cover:
            wrapper = textwrap.TextWrapper(width=60)
        lines = wrapper.wrap(self.quote)

        if self.show_title and self.show_author:
            y_coord = (self.height-len(lines)*self.quote_font_size -
                       2*self.book_author_font_size-1.5*self.book_author_font_size)//2
        elif self.show_title or self.show_author:
            y_coord = (self.height-len(lines)*self.quote_font_size -
                       2*self.book_author_font_size)//2
        else:
            y_coord = (self.height-len(lines)*self.quote_font_size)//2

        largest_quote_line_size = 0
        for line in lines:
            w = self.draw.textlength(text=line, font=self.quote_font)
            if w > largest_quote_line_size:
                largest_quote_line_size = w

        if self.show_book_cover:
            thumbnail_size = 2250
            if self.width != self.default_width and self.height != self.default_height:
                thumbnail_size *= math.sqrt(self.width *
                                            self.height)/math.sqrt(self.default_width*self.default_height)

            cover_image = Image.open(
                self.getBookCover(cover_url=self.cover_url))
            cover_image = cover_image.convert("RGBA")
            cover_image.thumbnail(
                (int(thumbnail_size), int(thumbnail_size)))
            book_cover_width, book_cover_height = cover_image.size

            book_cover_position = (
                int((self.width-largest_quote_line_size-book_cover_width)//2), (self.height-book_cover_height)//2)

            shadow_offset = 65
            if self.width != self.default_width and self.height != self.default_height:
                shadow_offset *= math.sqrt(self.width *
                                           self.height)/math.sqrt(self.default_width*self.default_height)

            shadow_color = "#11111B"
            if not self.dark_mode:
                shadow_color = "#DCE0E8"

            self.draw.rectangle(
                (
                    (self.width-largest_quote_line_size - \
                     book_cover_width)//2+shadow_offset,
                    (self.height-book_cover_height)//2+shadow_offset,
                    (self.width-largest_quote_line_size +
                        book_cover_width)//2+shadow_offset,
                    (self.height+book_cover_height)//2+shadow_offset),
                fill=shadow_color)

            self.image.paste(
                cover_image, book_cover_position, cover_image)

            after_cover_margin = 250
            if self.width != self.default_width and self.height != self.default_height:
                after_cover_margin *= math.sqrt(self.width *
                                                self.height)/math.sqrt(self.default_width*self.default_height)

            x_coord = (self.width-largest_quote_line_size +
                       book_cover_width+after_cover_margin)//2+after_cover_margin
        else:
            x_coord = (self.width-largest_quote_line_size)//2

        for line in lines:
            self.draw.text((x_coord, y_coord), line,
                           self.quote_text_color, font=self.quote_font)
            y_coord += self.quote_font_size

        if self.show_title and self.show_author:
            self.draw.text((x_coord, y_coord+2*self.book_author_font_size), self.book,
                           self.book_text_color, font=self.book_author_font)
            self.draw.text((x_coord, y_coord+2*self.book_author_font_size+1.5*self.book_author_font_size), self.author,
                           self.author_text_color, font=self.book_author_font)
        elif self.show_title:
            self.draw.text((x_coord, y_coord+2*self.book_author_font_size), self.book,
                           self.book_text_color, font=self.book_author_font)
        elif self.show_author:
            self.draw.text((x_coord, y_coord+2*self.book_author_font_size), self.author,
                           self.author_text_color, font=self.book_author_font)

    def setWallpaper(self) -> None:
        """Set the generated wallpaper as the current desktop background."""
        self.writeText()
        self.saveImage()

        system = platform.system()
        if system == "Darwin":
            script = f'tell application "System Events" to set picture of desktop 1 to "{self.filename}"'
            try:
                subprocess.run(["osascript", "-e", script], check=True)
                subprocess.run(["killall", "Dock"])  # refresh Dock
            except subprocess.CalledProcessError:
                logging.error("Desktop wallpaper could not be changed on macOS.")

        elif system == "Windows":
            wallpaper_style = 0
            SPI_SETDESKTOPWALLPAPER = 20
            image = ctypes.c_wchar_p(self.filename)
            ctypes.windll.user32.SystemParametersInfoW(  # type: ignore
                SPI_SETDESKTOPWALLPAPER, 0, image, image, wallpaper_style)

        elif system == "Linux":
            # Try common Linux desktop environment commands
            try:
                # GNOME
                subprocess.run([
                    "gsettings", "set", "org.gnome.desktop.background", "picture-uri", f"file://{self.filename}"
                ], check=True)
            except Exception:
                try:
                    # KDE Plasma
                    script = f"var Desktops = desktops();for (i=0;i<Desktops.length;i++) {{d=Desktops[i];d.wallpaperPlugin = 'org.kde.image';d.currentConfigGroup = Array('Wallpaper', 'org.kde.image', 'General');d.writeConfig('Image', 'file://{self.filename}')}}"
                    subprocess.run([
                        "qdbus", "org.kde.plasmashell", "/PlasmaShell", "org.kde.PlasmaShell.evaluateScript", script
                    ], check=True)
                except Exception:
                    try:
                        # feh (lightweight, works for many WMs)
                        subprocess.run([
                            "feh", "--bg-scale", self.filename
                        ], check=True)
                    except Exception:
                        logging.error("Could not set wallpaper automatically on Linux. Please set it manually.")


def main():
    quote, book, author, cover_url = KindleQuotes().getRandom()
    wallpaper = Wallpaper(
        quote=quote,
        book=book,
        author=author,
        cover_url=cover_url
    )
    wallpaper.writeText()
    wallpaper.saveImage()
    wallpaper.setWallpaper()


if __name__ == "__main__":
    main()
