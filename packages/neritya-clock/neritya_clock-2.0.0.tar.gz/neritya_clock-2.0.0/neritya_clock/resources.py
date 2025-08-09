import os
import importlib.resources as pkg_resources

def get_font_path(font_name: str) -> str:
    """
    Returns an absolute path to a font file packaged in neritya_clock/fonts.
    Works both in development and after pip install.
    """
    try:
        # Open the font as a resource from the installed package
        with pkg_resources.path("neritya_clock.fonts", font_name) as font_path:
            return str(font_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Font {font_name} not found in neritya_clock/fonts")
