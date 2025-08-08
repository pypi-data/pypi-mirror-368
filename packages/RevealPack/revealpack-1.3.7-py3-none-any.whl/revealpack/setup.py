import logging
import os
import shutil
import sys
import tarfile
import argparse
from io import BytesIO
from pathlib import Path
from textwrap import dedent

import requests
import zipfile

from _utils.config_operations import read_config, initialize_logging, write_config
from _utils.string_operations import (
    dict_to_js_notation, 
    add_offset_to_string, 
    get_blank_scss_template
)
from _utils.file_operations import get_theme_path


def create_directories():
    """Create directories based on config.json if they don't exist."""
    # Create production directory
    os.makedirs(config["directories"]["build"], exist_ok=True)
    source_config = config["directories"]["source"]
    source_root = source_config["root"]
    # Create source directories if they don't exist.
    os.makedirs(source_root, exist_ok=True)
    for key, folder in source_config.items():
        if key == "root":
            continue
        path = os.path.join(source_root, folder)
        os.makedirs(path, exist_ok=True)


def download_and_install_packages():
    """Download and install Reveal.js and specified plugins."""
    # Create a 'cached' directory if it doesn't exist
    cached_dir = os.path.join(config["directories"]["source"]["root"], "cached")
    os.makedirs(cached_dir, exist_ok=True)

    # Check if reveal.js folder exists, then only download if forced
    reveal_js_dir = os.path.join(cached_dir, "reveal.js")
    if os.path.exists(reveal_js_dir):
        if not config.get("force_plugin_download", True):
            logging.info(
                'Skipping Reveal.js download.\nIf required, set config "force_plugin_download" to true.'
            )
    else:
        # Download and extract Reveal.js
        reveal_version = config["packages"]["reveal.js"]
        reveal_url = f"https://github.com/hakimel/reveal.js/archive/refs/tags/{reveal_version}.zip"
        try:
            response = requests.get(reveal_url)
            with zipfile.ZipFile(BytesIO(response.content)) as z:
                z.extractall(path=cached_dir)
            # Rename the folder
            if os.path.exists(reveal_js_dir):
                shutil.rmtree(reveal_js_dir)
            os.rename(
                os.path.join(cached_dir, f"reveal.js-{reveal_version}"),
                reveal_js_dir,
            )
            logging.info(f"Reveal.js version {reveal_version} installed successfully")
        except Exception as e:
            logging.error(f"Failed to download and extract Reveal.js: {e}")
            sys.exit(1)

    # Download and extract external plugins
    external_plugins = config["packages"]["reveal_plugins"].get("external", {})
    for plugin, details in external_plugins.items():
        version = details["version"]
        url = details.get("url")
        alias = details.get("alias")
        
        target_folder = os.path.join(cached_dir, f"{plugin}-{version}")
        if os.path.exists(target_folder) and not config.get("force_plugin_download", True):
            logging.info(f"Skipping download of {plugin}.")
            continue

        if url:
            try:
                response = requests.get(url)
                response.raise_for_status()

                file_ext = url.split(".")[-1].lower()
                if file_ext in ["gz", "tgz"]:
                    with tarfile.open(
                        fileobj=BytesIO(response.content), mode="r:gz"
                    ) as tar:
                        extracted_folder = tar.getmembers()[0].name.split("/")[0]
                        tar.extractall(path=cached_dir)
                elif file_ext == "zip":
                    with zipfile.ZipFile(BytesIO(response.content), "r") as zip_ref:
                        extracted_folder = zip_ref.namelist()[0].split("/")[0]
                        zip_ref.extractall(cached_dir)
                elif file_ext == "js":
                    extracted_folder = 'tmp_plugin'
                    os.makedirs(os.path.join(cached_dir, extracted_folder), exist_ok=True)
                    js_file_path = os.path.join(cached_dir, extracted_folder, f"{plugin}.js")
                    with open(js_file_path, 'wb') as js_file:
                        js_file.write(response.content)
                else:
                    raise ValueError(f"Unsupported file extension: {file_ext}")

                extracted_path = os.path.join(cached_dir, extracted_folder)
                if os.path.exists(target_folder):
                    shutil.rmtree(target_folder)
                if extracted_folder != f"{plugin}-{version}":
                    os.rename(extracted_path, target_folder)

                logging.info(
                    f"Successfully downloaded and installed {plugin} from {url}"
                )
            except Exception as e:
                logging.error(
                    f"Failed to download and install {plugin} from {url}: {e}"
                )
        else:
            if alias:
                plugin_url = f"https://registry.npmjs.org/{alias}/-/{alias}-{version}.tgz"
            else:
                plugin_url = f"https://registry.npmjs.org/{plugin}/-/{plugin}-{version}.tgz"
            try:
                response = requests.get(plugin_url)
                response.raise_for_status()

                with tarfile.open(
                    fileobj=BytesIO(response.content), mode="r:gz"
                ) as tar:
                    tar.extractall(path=cached_dir)
                extracted_folder = "package"

                extracted_path = os.path.join(cached_dir, extracted_folder)
                if os.path.exists(target_folder):
                    shutil.rmtree(target_folder)
                os.rename(extracted_path, target_folder)

                logging.info(f"Successfully downloaded and installed {plugin} from npm")
            except Exception as e:
                logging.error(f"Failed to download and install {plugin} from npm: {e}")

def update_theme():
    """Validate the theme specified in config.json."""
    theme_path_str = get_theme_path(config)
    theme_not_found = not theme_path_str
    theme_full_path = Path(theme_path_str)
    
    if theme_not_found:
        logging.warning(f"Theme file {theme_full_path} not found. Creating a template file.")
        theme_name = Path(config.get("theme","custom_theme"))
        theme_full_path = Path(args.root) / "custom_theme" / theme_name.with_suffix('.scss').name
        theme_full_path.parent.mkdir(parents=True, exist_ok=True)
        theme_full_path.write_text(get_blank_scss_template())
    if not theme_full_path.exists():
        logging.error(f"Theme {theme_full_path} not found. Update config.json!")
        sys.exit(1)
    
    write_config(args.root, "theme", str(theme_full_path), force=True)
    logging.info(f"Using theme: {theme_full_path}")

def create_reveal_template():
    """Generate Jinja2 templates for Reveal.js based on config.json."""
    source_obj = config["directories"]["source"]
    source_root = Path(source_obj.get("root", "source"))

    # Extract theme name from the path
    theme_folder, theme_name = os.path.split(config["theme"])
    theme_name = Path(theme_name).stem
    
    # Prepare the list of plugins
    builtin_plugins = config["packages"]["reveal_plugins"]["built_in"]
    external_plugins = config["packages"]["reveal_plugins"]["external"]

    # Create the list of built-in plugins
    all_plugins = []
    for plugin in builtin_plugins:
        # Built-in plugins don't have noscript/omit fields, so always include them
        all_plugins.append(f"src/plugin/{plugin}/{plugin}.js")

    # Create the list of external plugins, using alias and main if they exist
    for plugin, details in external_plugins.items():
        # Skip if noscript is true
        if details.get("noscript", False):
            continue
            
        alias = details.get("alias", plugin)
        mainjs = details.get("main", plugin)

        if mainjs.endswith(".js"):
            mainjs = mainjs[:-3]

        all_plugins.append(f"src/plugin/{alias}/{mainjs}.js")

    # Generate plugin names for Reveal.initialize()
    builtin_plugin_names = []
    for plugin in builtin_plugins:
        # Built-in plugins don't have omit field, so always include them
        builtin_plugin_names.append(f"Reveal{plugin.capitalize()}")
    
    # Check if "RevealMath" is in the list
    if "RevealMath" in builtin_plugin_names:
        # Extract the plugin configurations from the config
        plugin_config = config["packages"]["reveal_plugins"].get("plugin_configurations", {})

        # Enhanced MathJax processing - check for mathjax# pattern
        mathjax_replacement = None
        for key in plugin_config.keys():
            if key.startswith("mathjax"):
                # Extract the version number if present
                version = key[7:] if len(key) > 7 else ""
                if version in ["", "2", "3", "4"]:
                    mathjax_replacement = f"RevealMath.MathJax{version}" if version else "RevealMath"
                    break
        
        # Fallback to original logic if no mathjax# pattern found
        if mathjax_replacement is None:
            if "mathjax2" in plugin_config:
                mathjax_replacement = "RevealMath.MathJax2"
            elif "mathjax3" in plugin_config:
                mathjax_replacement = "RevealMath.MathJax3"
            elif "mathjax4" in plugin_config:
                mathjax_replacement = "RevealMath.MathJax4"
            elif "katex" in plugin_config:
                mathjax_replacement = "RevealMath.KaTeX"
            else:
                # None of the keys were found; "RevealMath" is sufficient
                mathjax_replacement = "RevealMath"

        # Modify the "RevealMath" entry in the builtin_plugin_names array
        builtin_plugin_names[builtin_plugin_names.index("RevealMath")] = mathjax_replacement

    external_plugin_names = []
    for plugin, details in external_plugins.items():
        # Skip if omit is true
        if details.get("omit", False):
            continue
        exportName = details.get("export", plugin.capitalize())
        external_plugin_names.append(exportName)

    plugin_name_list = ", ".join(builtin_plugin_names + external_plugin_names)
    
    # Check if "highlight" is in the built_in plugins or "highlight.js" is in the external plugins
    if (
        "highlight" in config["packages"]["reveal_plugins"]["built_in"]
        or "highlight.js" in config["packages"]["reveal_plugins"]["external"]
    ):
        # Get the highlight theme path or default to "monokai"
        highlight_theme = config.get("highlight_theme", "monokai")

        # Check if the provided highlight_theme is a path and whether it has a .css extension
        theme_path = Path(highlight_theme)
        if not theme_path.suffix:
            theme_path = theme_path.with_suffix('.css')

        # Paths to check
        paths_to_check = [
            theme_path,
            source_root / "cached" / "reveal.js" / "plugin" / "highlight" / theme_path.name,
            Path.cwd() / theme_path.name
        ]

        # Find the highlight CSS file
        for path in paths_to_check:
            if path.exists():
                highlight_css = path.name
                highlight_css_path = path
                break

        if highlight_css:
            highlight_str = "\n".join(
                [
                    "<!-- highlight.js theme -->",
                    f'<link rel="stylesheet" href="./src/theme/{highlight_css}" id="highlight-theme">',
                ]
            )
            write_config(
                args.root, 
                "highlight_theme", 
                str(highlight_css_path), 
                force=True
                )
        else:
            logging.warning("Highlight theme CSS not found. Defaulting to 'monokai'.")

    # Parse config["custom_css"] array and insert the stylesheet links into the template
    custom_css = config.get("custom_css", [])
    custom_css_tags = "\n".join([f'<link rel="stylesheet" href="./src/css/{css}">' for css in custom_css])

    # Parse config["custom_scripts"] array and insert them into the template
    libraries_destination_dir = Path(config["directories"]["build"]) / config["directories"]["source"]["libraries"] / "custom_scripts"
    custom_scripts = config.get("custom_scripts", [])
    custom_script_tags = "\n".join([f'<script src="{libraries_destination_dir / script}"></script>' for script in custom_scripts])

    # Reveal.js configurations
    # Create a list of formatted key-value pairs
    reveal_config_str = dict_to_js_notation(config["reveal_configurations"])
    plugin_config_str = dict_to_js_notation(config["packages"]["reveal_plugins"]["plugin_configurations"])
    favicon_path = Path(source_obj.get("libraries", "lib")) / "favicon.png"

    # Create Reveal.js template with Jinja2 placeholders for build.py
    reveal_template = f"""
<!doctype html>
<html lang="en-US">
    <head>
        <meta charset="utf-8">
        <meta name="google" content="notranslate">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>{{{{deck.title}}}}</title>
        <link rel="icon" type="image/x-icon" href="{favicon_path}">
        <link rel="stylesheet" href="./src/css/reset.css">
        <link rel="stylesheet" href="./src/css/reveal.css">
        <link rel="stylesheet" href="./src/css/revealpack.css">
        <link rel="stylesheet" href="./src/theme/{theme_name}.css" id="theme">
{add_offset_to_string(highlight_str, 8)}
        <!-- Custom CSS -->
{add_offset_to_string(custom_css_tags, 8)}
        <!-- Custom Scripts -->
{add_offset_to_string(custom_script_tags, 8)}
        <!-- Print PDF and Show logic -->
        <script>
            const params = window.location.search.replace('?', '').split('+');
            const hasPrintPDF = params.includes('print-pdf');
            const hasShow = params.includes('show');

            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.type = 'text/css';
            link.href = hasPrintPDF ? './src/css/print/pdf.css' : './src/css/print/paper.css';
            document.head.appendChild(link);

            if (hasPrintPDF && hasShow) {{
                const style = document.createElement('style');
                style.innerHTML = `
                    html.print-pdf .reveal .slides .pdf-page section .print-invisible,
                    html.reveal-print .reveal .slides .pdf-page section .print-invisible {{
                        visibility: visible !important;
                        display: block !important;
                    }}
                `;
                document.head.appendChild(style);
            }}
        </script>
        <!-- Deck CSS Injections -->
        {{% if deck.head and deck.head.styles %}}
        {{% for style in deck.head.styles %}}
        <link rel="stylesheet" href="./{config['directories']['source']['libraries']}/{{{{ style }}}}">
        {{% endfor %}}
        {{% endif %}}
        <!-- Deck Script Injections -->
        {{% if deck.head and deck.head.scripts %}}
        {{% for script in deck.head.scripts %}}
        <script src="./{config['directories']['source']['libraries']}/{{{{ script }}}}"></script>
        {{% endfor %}}
        {{% endif %}}
        <!-- Deck Raw Injections -->
        {{% if deck.head and deck.head.raw %}}
        {{% for entry in deck.head.raw %}}
        {{{{ entry }}}}
        
        {{% endfor %}}
        {{% endif %}}
    </head>
    <body>
        <div class="reveal">
            <div class="slides">
                {{% if deck.titlepage %}}
                <section id="deck-title-slide" {{%- if deck.titlepage.background -%}}{{%- for i, v in deck.titlepage.background.items() -%}} data-background-{{{{ i }}}}="{{{{ v }}}}"{{%- endfor -%}}{{%- endif -%}}>
                    <div class="title-slide{{%- if deck.titlepage.background %}} background{{%- endif -%}}">
                    {{% if deck.titlepage.image %}}
                        <div class="image" style="background-image: url({{{{ deck.titlepage.image }}}});"></div>
                    {{% endif %}}
                        <div class="headline">
                            {{% if deck.titlepage.headline %}}
                            {{% for line in deck.titlepage.headline %}}
                            {{% if loop.first %}}
                            <h2 class="r-fit-text">{{{{ line|title }}}}</h2>
                            {{% else %}}
                            <h3>{{{{ line }}}}</h3>
                            {{% endif %}}
                            {{% endfor %}}
                            {{% endif %}}
                        </div>
                        <div class="sub-header">
                            {{% if deck.titlepage.by %}}
                            {{% for by in deck.titlepage.by %}}
                            <p class="by">{{{{ by }}}}</p>
                            {{% endfor %}}
                            {{% endif %}}
                        </div>
                        <div class="byline">
                            {{% if deck.titlepage.byinfo %}}
                            {{% for byinfo in deck.titlepage.byinfo %}}
                            <p class="byinfo">{{{{ byinfo }}}}</p>
                            {{% endfor %}}
                            {{% endif %}}
                        </div>
                    </div>
                    {{% if deck.titlepage.notes %}}
                    <aside class="notes">
                    {{% for note in deck.titlepage.notes %}}<p>{{{{ note }}}}</p>
                    {{% endfor %}}
                    </aside>
                    {{% endif %}}
                </section>
                {{% endif %}}
                {{% set section_count = namespace(n = 0) -%}}
                {{% for slide in deck.slides %}}
                {{% if slide.sectiontitle %}}
                {{% set section_count.n = section_count.n + 1 %}}
                <section id="section-title-{{{{ section_count.n }}}}"{{% if slide.sectiontitle.image -%}}
                 data-background-image="{{{{ slide.sectiontitle.image.url }}}}"{{% for key, value in slide.sectiontitle.image.items() if key != 'url' -%}} data-background-{{{{ key }}}}="{{{{ value }}}}"{{% endfor -%}}
                 {{%- elif slide.sectiontitle.color -%}}
                 data-background-color="{{{{ slide.sectiontitle.color }}}}"
                 {{%- elif slide.sectiontitle.gradient -%}}
                 data-background-gradient="{{{{ slide.sectiontitle.gradient }}}}"
                 {{%- endif -%}}>
                    <div class="grid-wrapper">
                        <div class="section-title-content" id="section-content-{{{{ section_count.n }}}}">
                        <div class="section-number">
                            <span class="large-number">{{{{ section_count.n }}}}</span>
                        </div>
                        <div class="headlines">
                            {{% for line in slide.sectiontitle.headline %}}
                            {{% if loop.first %}}
                            <h2 class="r-fit-text">{{{{ line|title }}}}</h2>
                            {{% else %}}
                            <h3>{{{{ line|title }}}}</h3>
                            {{% endif %}}
                            {{% endfor %}}
                        </div>
                        </div>
                    </div>
                    {{{{ slide.content }}}}
                {{% else %}}
                <section {{{{ slide.attributes|to_html_attrs|safe }}}}>
                    {{{{ slide.content }}}}
                {{% endif %}}
                </section>
                {{% endfor %}}
            </div>
            {{% if deck.footer %}}
            <footer class="main-footer">
                <span>{{{{ deck.footer.left if deck.footer.left is defined else '' }}}}</span>
                <span style="text-align:center;">{{{{ deck.footer.middle if deck.footer.middle is defined else '' }}}}</span>
                <span style="text-align:right;">{{{{ deck.footer.right if deck.footer.right is defined else '' }}}}</span>
            </footer>
            {{% endif %}}
        </div>
        <script src="./src/reveal.js"></script>
{add_offset_to_string('\n'.join([f'<script src="./{plugin}"></script>' for plugin in all_plugins]), 8)}
        <script>
            Reveal.initialize({{
{ add_offset_to_string(reveal_config_str, 14) }
{ add_offset_to_string(plugin_config_str, 14) }
            plugins: [{plugin_name_list}]
            }});
        </script>
    </body>
</html>
"""

    reveal_template_path = source_root / config["reveal_template"]
    with reveal_template_path.open("w") as f:
        f.write(reveal_template)

    logging.info(f"Reveal template created at {reveal_template_path}")

def create_toc_template():
    """Create the TOC template and save it to the source root directory."""
    source_obj = config["directories"]["source"]
    favicon_path = os.path.join(source_obj.get("libraries","lib"), "favicon.png")
    toc_str = f"""
    <!DOCTYPE html>
    <html lang="en-US">
    <head>
        <meta charset="UTF-8">
        <meta name="google" content="notranslate">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Table of Contents</title>
        <link rel="icon" type="image/x-icon" href="{favicon_path}">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                height: 100vh;
                overflow: hidden;
            }}

            .topbar {{
                background-color: #333;
                color: white;
                padding: 10px;
                display: flex;
                align-items: center;
                height: 40px;
            }}

            #menu-toggle {{
                background: none;
                border: none;
                color: white;
                font-size: 1.5em;
                cursor: pointer;
                padding: 0 15px;
            }}

            .heading {{
                margin-left: 15px;
            }}

            .container {{
                display: flex;
                height: calc(100vh - 60px);
            }}

            .sidebar {{
                background-color: #f4f4f4;
                width: 300px;
                overflow-y: auto;
                transition: transform 0.3s ease;
                position: absolute;
                top: 60px;
                bottom: 0;
                left: 0;
                z-index: 100;
                box-shadow: 2px 0 5px rgba(0,0,0,0.1);
            }}

            .sidebar.closed {{
                transform: translateX(-300px);
            }}

            .content {{
                flex-grow: 1;
                height: 100%;
            }}

            #presentation-frame {{
                width: 100%;
                height: 100%;
                border: none;
            }}

            .toc-item {{
                padding: 15px;
                border-bottom: 1px solid #ddd;
                display: flex;
                justify-content: space-between;
                align-items: center;
                background-color: white;
            }}

            .toc-item:hover {{
                background-color: #f8f8f8;
            }}

            .toc-link {{
                text-decoration: none;
                color: #333;
                flex-grow: 1;
                margin-right: 10px;
            }}

            .external-link {{
                color: #666;
                font-size: 1.2em;
            }}

            .external-link:hover {{
                color: #000;
            }}
        </style>
    </head>
    <body>
        <div class="topbar">
            <button id="menu-toggle"><i class="fas fa-bars"></i></button>
            <h1 class="heading">{{{{ project_title|title }}}}</h1>
        </div>
        <div class="container">
            <nav class="sidebar">
                <div class="toc-list">
                    {{% for presentation in toc_links %}}
                        <div class="toc-item">
                            <a href="{{{{ presentation.link|safe }}}}" class="toc-link" data-src="{{{{ presentation.link|safe }}}}">
                                {{{{ presentation.name|title }}}}
                            </a>
                            <a href="{{{{ presentation.link|safe }}}}" class="external-link" target="_blank" title="Open in new tab">
                                <i class="fas fa-external-link-alt"></i>
                            </a>
                        </div>
                    {{% endfor %}}
                </div>
            </nav>
            <main class="content">
                <iframe id="presentation-frame" title="Presentation Viewer"></iframe>
            </main>
        </div>

        <script>
            const menuToggle = document.getElementById('menu-toggle');
            const sidebar = document.querySelector('.sidebar');
            const iframe = document.getElementById('presentation-frame');
            const tocLinks = document.querySelectorAll('.toc-link');

            // Toggle sidebar
            menuToggle.addEventListener('click', () => {{
                sidebar.classList.toggle('closed');
                reloadIframe();
            }});

            // Handle presentation links
            tocLinks.forEach(link => {{
                link.addEventListener('click', (e) => {{
                    e.preventDefault();
                    const src = link.getAttribute('data-src');
                    iframe.src = src;
                    
                    // On mobile or narrow screens, close the sidebar after selection
                    if (window.innerWidth <= 768) {{
                        sidebar.classList.add('closed');
                    }}
                }});
            }});

            // Handle window resize
            let resizeTimer;
            window.addEventListener('resize', () => {{
                clearTimeout(resizeTimer);
                resizeTimer = setTimeout(reloadIframe, 250);
            }});

            function reloadIframe() {{
                if (iframe.src) {{
                    iframe.src = iframe.src;
                }}
            }}

            // Load first presentation by default
            if (tocLinks.length > 0) {{
                const firstLink = tocLinks[0];
                iframe.src = firstLink.getAttribute('data-src');
            }}
        </script>
    </body>
    </html>
    """
    toc_template_content = dedent(toc_str)

    toc_template_path = os.path.join(
        config["directories"]["source"]["root"], config["toc_template"]
    )
    with open(toc_template_path, "w") as f:
        f.write(toc_template_content)

    logging.info(f"TOC template created at {toc_template_path}")


def main():
    initialize_logging(config)
    create_directories()
    download_and_install_packages()
    update_theme()
    create_reveal_template()
    create_toc_template()
    
    # After initialization set force download off
    write_config(args.root,"force_plugin_download",False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Setup Reveal.js presentation environment.')
    parser.add_argument('--root', type=str, default=os.getcwd(), help='Target directory for setup')
    parser.add_argument('--force-plugin-download', '-f', action='store_true', help='Force plugin download')
    args = parser.parse_args() #global
    
    if args.force_plugin_download:
        write_config(args.root, "force_plugin_download", True, force=True)

    config = read_config(args.root)
    main()
