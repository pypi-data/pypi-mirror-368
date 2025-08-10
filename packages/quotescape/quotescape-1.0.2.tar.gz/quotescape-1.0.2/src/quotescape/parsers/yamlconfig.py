import yaml
import argparse
import os
import re
from pathlib import Path


class YamlConfigParser:

    def __init__(self, config_file: str | None = None) -> None:

        # Resolve config path (from explicit path or CWD/settings/config.yaml)
        if config_file is not None:
            config_path = Path(config_file)
            if not config_path.exists():
                raise FileNotFoundError(f"Config file not found at explicit path: {config_path}")
        else:
            config_path = Path.cwd() / "settings" / "config.yaml"
            if not config_path.exists():
                raise FileNotFoundError(
                    f"No configuration file found. Expected at: {config_path}"
                )

        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        wallpaper_path = config['wallpaper_path'] if config[
            'wallpaper_path'] else f'{os.getcwd()}/wallpaper'

        width = config['dimension']['width']
        height = config['dimension']['height']
        self.isValidWidth(width)
        self.isValidHeight(height)

        quote_type = config['type']
        dark_mode = config['dark_mode']

        if dark_mode:
            background_color = config['colors']['dark']['background_color']
            quote_text_color = config['colors']['dark']['quote_text_color']
            author_text_color = config['colors']['dark']['author_text_color']
            title_text_color = config['colors']['dark']['title_text_color']
        else:
            background_color = config['colors']['light']['background_color']
            quote_text_color = config['colors']['light']['quote_text_color']
            author_text_color = config['colors']['light']['author_text_color']
            title_text_color = config['colors']['light']['title_text_color']

        self.isValidHexColorCode(background_color)
        self.isValidHexColorCode(quote_text_color)
        self.isValidHexColorCode(author_text_color)
        self.isValidHexColorCode(title_text_color)

        show_author = config.get('show_author', True)

        show_book_cover = False
        show_title = False

        if quote_type == "kindle":
            show_book_cover = config['kindle_highlight_settings']['show_book_cover']
            show_title = config['kindle_highlight_settings']['show_book_title']
        elif quote_type == "custom":
            # Prefer user-provided path; fallback to settings/custom_quotebook.json
            custom_section = config.get('custom_quote_settings', {}) or {}
            custom_quotebook_path = custom_section.get('custom_quotebook_path')
            if not custom_quotebook_path:
                custom_quotebook_path = str(Path.cwd() / "settings" / "custom_quotebook.json")
        else:
            raise TypeError(
                f"quotescape does not support \"{quote_type}\" quotes. Please select between \"kindle\", \"random\", and \"custom\" quotes.")

        self.quote_type = quote_type
        self.wallpaper_path = wallpaper_path
        self.width = width
        self.height = height
        self.dark_mode = dark_mode
        self.background_color = background_color
        self.quote_text_color = quote_text_color
        self.title_text_color = title_text_color
        self.author_text_color = author_text_color
        self.show_author = show_author
        self.show_book_cover = show_book_cover if quote_type == "kindle" else False
        self.show_title = show_title if quote_type == "kindle" else False
        self.custom_quotebook_path = custom_quotebook_path if quote_type == "custom" else None

    def isValidHexColorCode(self, color_code: str):
        pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
        validity = bool(re.match(pattern, color_code))
        if not validity:
            raise argparse.ArgumentTypeError(
                "%s is an invalid value. It must be a hexadecimal color code." % color_code)
        return color_code

    def isValidWidth(self, width):
        int_width = int(width)
        if int_width < 1280 or int_width > 7680:
            raise argparse.ArgumentTypeError(
                "%s is an invalid value. It must be an integer between 1280 and 7680, inclusive." % width)
        return int_width

    def isValidHeight(self, height):
        int_height = int(height)
        if int_height < 720 or int_height > 4320:
            raise argparse.ArgumentTypeError(
                "%s is an invalid value. It must be an integer between 720 and 4320, inclusive." % height)
        return int_height


if __name__ == "__main__":
    print(YamlConfigParser())
