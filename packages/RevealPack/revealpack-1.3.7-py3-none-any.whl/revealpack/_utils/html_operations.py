import os
import sys
import shutil
import logging
import platform
import subprocess
from pathlib import Path

from bs4 import BeautifulSoup
from bs4.formatter import HTMLFormatter

# -----------------------------------------------------------------------------
# HTML formatting utility
# -----------------------------------------------------------------------------

def beautify_html(html_str, indent_size=2):
    """
    Beautify an HTML string using BeautifulSoup's prettify method.
    """
    lines = html_str.split("\n")
    stripped_lines = [line.strip() for line in lines]
    cleaned_html = "\n".join(stripped_lines)

    formatter = HTMLFormatter(indent=indent_size)
    soup = BeautifulSoup(cleaned_html, "html.parser")
    return soup.prettify(formatter=formatter)

# -----------------------------------------------------------------------------
# SCSS compilation using Dart Sass CLI
# -----------------------------------------------------------------------------

_ENV_OVERRIDE = "REVEALPACK_SASS_PATH"

def _resolve_sass_cli():
    # 1. Check for override via environment variable
    env_path = os.environ.get(_ENV_OVERRIDE)
    if env_path and Path(env_path).is_file():
        return env_path

    # 2. Check for sass in system path
    system_path = shutil.which("sass")
    if system_path:
        return system_path

    # 3. Not found: prompt user to install manually
    print(
        "\n❌ Dart Sass CLI not found.\n"
        "   Please install Dart Sass from https://sass-lang.com/install\n"
        f"   Or set the environment variable {_ENV_OVERRIDE} to its path.\n"
        "   You may need to restart your terminal after installation.\n"
    )
    sys.exit(1)

def compile_scss(input_file, output_file):
    """
    Compile an SCSS file to CSS using Dart Sass CLI.
    """
    sass = _resolve_sass_cli()
    try:
        subprocess.run(
            [sass, "--no-source-map", input_file, output_file],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logging.info(f"✅ Compiled SCSS: {input_file} → {output_file}")
    except subprocess.CalledProcessError as e:
        logging.error("❌ Sass compilation failed:\n%s", e.stderr or e.stdout)
        sys.exit(e.returncode)
