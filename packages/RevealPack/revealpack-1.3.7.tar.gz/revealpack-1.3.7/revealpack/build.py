import json
import logging
import sys
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
import glob
import argparse
import re
from urllib.parse import unquote
from html import unescape

# Import utility functions
from _utils.file_operations import (
    copy_and_overwrite, 
    copy_file_if_different,
    get_theme_path,
    cleanup_temp_files,
    parse_delimited_file,
    clean_build_directory
)
from _utils.html_operations import beautify_html, compile_scss
from _utils.config_operations import read_config, initialize_logging
from _utils.presentation_operations import (
    parse_slide,
    dict_to_html_attrs,
    validate_titlepage,
)


def get_referenced_files(html_content, libraries_dir, source_root=None, current_path=None):
    """Extract file references from HTML content that are in the libraries directory.
    
    Args:
        html_content (str): The rendered HTML content
        libraries_dir (str): The name of the libraries directory
        source_root (str, optional): The source directory root, needed for recursive HTML scanning
        current_path (str, optional): Current file path being processed, for relative path resolution
        
    Returns:
        set: Set of unique file paths referenced in the HTML that are in libraries_dir
    """
    # First unescape any HTML entities in the content
    html_content = unescape(html_content)
    
    patterns = [
        # Standard HTML attributes
        rf'(?:src|data-src|href)\s*=\s*["\']([^"\']*?{libraries_dir}/[^"\']+)["\']',
        
        # Background and other data attributes
        rf'data-background(?:-image)?\s*=\s*["\']([^"\']*?{libraries_dir}/[^"\']+)["\']',
        
        # Any other data-* attributes that might reference library files
        rf'data-[a-zA-Z-]+\s*=\s*["\']([^"\']*?{libraries_dir}/[^"\']+)["\']',
        
        # Same attributes but without quotes (rare but possible)
        rf'(?:src|data-src|href|data-background(?:-image)?)\s*=\s*([^\s>]*?{libraries_dir}/[^\s>]+)',
        
        # CSS url() function with optional quotes
        rf'url\(["\']?([^"\')\s]*?{libraries_dir}/[^"\')\s]+)["\']?\)',
        
        # Any quoted path containing libraries_dir (catch-all for other cases)
        rf'["\']([^"\']*?{libraries_dir}/[^"\']+)["\']'
    ]
    
    referenced_files = set()
    logging.debug(f"Libraries directory: {libraries_dir}")
    
    for pattern in patterns:
        logging.debug(f"  Searching with pattern: {pattern}")
        matches = re.finditer(pattern, html_content, re.IGNORECASE)
        for match in matches:
            # Always use group 1 as it contains the path without quotes/function calls
            path = unquote(match.group(1)).replace('\\', '/')
            
            # Remove URL fragments (anything after #)
            path = path.split('#')[0]
            
            logging.debug(f"    Found raw path: {path}")
            
            # Split the path into components
            path_parts = re.split(r'[/\\]', path)
            
            try:
                lib_index = path_parts.index(libraries_dir)
                # Take everything from libraries_dir onwards
                relative_parts = path_parts[lib_index:]
                if relative_parts:  # Only process if we have parts after libraries_dir
                    # Join with OS-specific separator
                    relative_path = os.path.join(*relative_parts)
                    logging.debug(f"    Adding relative path: {relative_path}")
                    referenced_files.add(relative_path)
                    
                    # If this is an HTML file and we have a source root, recursively scan it
                    if source_root and relative_path.endswith('.html'):
                        html_path = os.path.join(source_root, relative_path)
                        if os.path.exists(html_path):
                            logging.debug(f"    Recursively scanning HTML file: {html_path}")
                            with open(html_path, 'r', encoding='utf-8') as f:
                                sub_html_content = f.read()
                            # Recursively scan the HTML content
                            sub_files = get_referenced_files(
                                sub_html_content, 
                                libraries_dir,
                                source_root=source_root,
                                current_path=relative_path
                            )
                            referenced_files.update(sub_files)
            except ValueError:
                logging.debug(f"    Skipping path: {path} (no {libraries_dir} found)")
            except Exception as e:
                logging.debug(f"    Error processing path {path}: {str(e)}")
    
    if referenced_files:
        logging.debug("Found referenced files:")
        for ref in sorted(referenced_files):
            logging.debug(f"  - {ref}")
    else:
        logging.debug("No library references found")
                
    return referenced_files

def copy_libraries():
    """Copy all contents of the libraries directory to the build directory."""
    logging.info("Copying libraries...")

    # Source and destination directories
    source_dir = os.path.join(
        config["directories"]["source"]["root"],
        config["directories"]["source"]["libraries"]
    )
    dest_dir = os.path.join(
        config["directories"]["build"], 
        config["directories"]["source"]["libraries"]
    )

    # Check if source directory exists
    if not os.path.exists(source_dir):
        logging.error(f"Source directory for libraries not found: {source_dir}")
        return

    # Create destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)

    
    # Copy files
    for item in os.listdir(source_dir):
        s = os.path.join(source_dir, *[part for part in item.replace('\\', '/').split('/')])
        logging.debug(f"  Copying {s}")
        d = os.path.join(dest_dir, item)
        if os.path.exists(s):
            if os.path.isdir(s):
                copy_and_overwrite(s, d)
            else:
                copy_file_if_different(s, d)
        else:
            logging.info(f"  Could not find source file: {s}")


def copy_custom_scripts():
    """Copy custom scripts, if any, to the desired directory"""
    scripts = config.get("custom_scripts", [])
    if not len(scripts):
        logging.info("No custom scripts provided.")
        return
    logging.info("Copying custom scripts...")
    source_dir = "custom_scripts"
    dest_dir = os.path.join(
        config["directories"]["build"], 
        config["directories"]["source"]["libraries"],
        "custom_scripts"
    )
    for item in os.listdir(source_dir):
        if item not in scripts:
            continue
        s = os.path.join(source_dir,item)
        d = os.path.join(dest_dir,item)
        copy_file_if_different(s, d)
    logging.info("Custom scripts copied successfully.")

def copy_custom_css():
    """Copy custom css, if any, to the build directory"""
    css = config.get("custom_css",[])
    if not len(css):
        logging.info("No Custom CSS provided.")
        return
    logging.info("Copying Custom CSS...")
    source_dir = "custom_css"
    dest_dir = os.path.join(config["directories"]["build"], "src","css")
    for item in os.listdir(source_dir):
        if item not in css:
            continue
        s = os.path.join(source_dir,item)
        s_f, s_n = os.path.split(item)
        # new path omits any root folders
        d = os.path.join(dest_dir,s_n)
        copy_file_if_different(s,d)
    logging.info("Custom CSS copied successfully.")

def copy_plugins():
    """Copy plugins to the production directory."""
    logging.info("Copying plugins...")

    # Source and destination directories
    source_root = config["directories"]["source"]["root"]
    dest_dir = os.path.join(config["directories"]["build"], "src", "plugin")

    # Create destination directory if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)

    # Copy built-in plugins
    builtin_plugins = config["packages"]["reveal_plugins"]["built_in"]
    for plugin in builtin_plugins:
        source_path = os.path.join(source_root, "cached", "reveal.js", "plugin", plugin)
        dest_path = os.path.join(dest_dir, plugin)

        if os.path.exists(source_path):
            copy_and_overwrite(source_path, dest_path)
        else:
            logging.warning(f"Built-in plugin {plugin} not found in source directory.")

    # Copy external plugins
    external_plugins = config["packages"]["reveal_plugins"].get("external", {})
    for plugin, details in external_plugins.items():
        version = details["version"]
        alias = details.get("alias", plugin)
        external_plugin_name = f"{plugin}-{version}"
        source_path = os.path.join(source_root, "cached", external_plugin_name)
        dest_path = os.path.join(dest_dir, alias)

        if os.path.exists(source_path):
            copy_and_overwrite(source_path, dest_path)
        else:
            logging.warning(f"External plugin {plugin} not found in source directory.")
    logging.info("Plugins copied successfully.")

def copy_and_compile_styles():
    """Copy and compile styles from the assets/styles directory."""
    logging.info("Copying and compiling styles...")
    
    
    source_root = Path(config["directories"]["source"]["root"])
    
    # Source directory
    styles_dir = source_root.parent / 'assets' / 'styles'
    # Reveal theme directory
    theme_root_in_reveal = source_root / "cached" / "reveal.js" / "css" / "theme" / "source"
    # Destination directory
    target_css = Path(config["directories"]["build"]) / "src" / "css"

    # Ensure target directory exists
    target_css.mkdir(parents=True, exist_ok=True)

    # Copy styles to Reveal.js Theme Source for compilation
    files_to_parse = []
    files_to_copy = list(styles_dir.glob("*.scss")) + list(styles_dir.glob("*.sass")) + list(styles_dir.glob("*.css"))
    for file in files_to_copy:
        logging.info(f"Copying {file} to Reveal Theme Source for SASS compilation.")
        reveal_theme_file_path = theme_root_in_reveal / file.name
        copy_file_if_different(str(file), str(reveal_theme_file_path))
        files_to_parse.append(reveal_theme_file_path)
            

    # Compile SASS/SCSS files
    for file in files_to_parse:
        target_path = target_css / file.with_suffix('.css').name
        if file.suffix != ".css":
            logging.info(f"Compiling temporary SASS file '{file.stem}'...")
            compile_scss(str(file), str(target_path))
        else:
            copy_file_if_different(str(file), str(target_path))

    # Delete the copied files after compilation
    for file in files_to_parse:
        logging.info(f"Deleting temporary file '{file}'...")
        file.unlink()

    logging.info("Styles copied and compiled successfully.")

def compile_theme():
    """Compile the SCSS/SASS theme into CSS."""
    logging.info("Compiling theme...")

    source_root = Path(config["directories"]["source"]["root"])
    project_root = source_root.parent
    
    target_root = Path(config["directories"]["build"])
    target_theme_directory = target_root / "src" / "theme"
    target_theme_directory.mkdir(parents=True, exist_ok=True)
    
    reveal_root = source_root / "cached" / "reveal.js"
    theme_compiler_root = reveal_root / "css" / "theme" / "source"
    
    theme_path_str = get_theme_path(config)
    if not theme_path_str:
        logging.error("Theme could not be located!")
        sys.exit(1)
    theme_path = Path(theme_path_str)
    theme_directory = str(theme_path.parent)
    # conditionals
    is_theme_in_project_root = theme_path.parent == Path(args.root)
    is_theme_precompiled = theme_path.suffix == '.css'
    is_theme_in_reveal = "reveal.js" in str(theme_path)
    
    theme_path_in_build = (target_theme_directory / theme_path.name).with_suffix(".css")
    theme_path_in_compiler = theme_compiler_root / theme_path.name
    
    # Setup fonts directory in the theme src/dest
    fonts_path_in_root = theme_path.parent / "fonts"
    fonts_path_in_build = theme_path_in_build.parent / "fonts"
    fonts_path_in_compiler = theme_compiler_root / "fonts"

    # Theme file must exist per get_theme_path()
    logging.info(f"Copying theme '{theme_path.name}'...")
    files_copied = []
    if is_theme_precompiled:
        logging.warning("\tProvided theme is a CSS file. It will not be parsed with Reveal.js dynamic variables.")
        copy_file_if_different(
            str(theme_path), 
            str(theme_path_in_build)
            )
        if fonts_path_in_root.exists():
            logging.info(f"\tCopying fonts from '{fonts_path_in_root}' to '{fonts_path_in_build}'...")
            copy_and_overwrite(
                str(fonts_path_in_root), 
                str(fonts_path_in_build)
                )
    elif is_theme_in_reveal:
        logging.info(f"\tUsing reveal.js theme '{theme_path.stem}'.")
        # In reveal already, copy fonts if they exist
        if fonts_path_in_root.exists():
            logging.info(f"\tCopying fonts from '{fonts_path_in_root}' to '{fonts_path_in_build}'...")
            copy_and_overwrite(str(fonts_path_in_root), str(fonts_path_in_build))
            copy_and_overwrite(
                str(fonts_path_in_root), 
                str(fonts_path_in_compiler),
                files_copied
                )
            
    else:
        # Not in reveal need more copy logic
        if fonts_path_in_root.exists():
            logging.info(f"\tCopying fonts from '{fonts_path_in_root}' to '{fonts_path_in_build}'...")
            copy_and_overwrite(str(fonts_path_in_root), str(fonts_path_in_build))
            copy_and_overwrite(
                str(fonts_path_in_root), 
                str(fonts_path_in_compiler),
                files_copied
                )
        # if in "." just copy theme file and fonts (if any)
        if is_theme_in_project_root:
            logging.info(f"\tUsing theme file {theme_path.name}.")
            copy_file_if_different(
                str(theme_path),
                str(theme_path_in_compiler),
                files_copied
                )
        # if in "./dir/", copy contents of dir (ignore fonts directly)
        else:
            logging.info(f"\tUsing theme file {theme_path.name} with contents of {theme_path.parent}.")
            copy_and_overwrite(
                str(theme_path.parent), 
                str(theme_path_in_compiler.parent),
                files_copied
                ) # recursively copy contents, maintain dir structure
    
    # HIGLIGHT JS THEME
    highlight_theme = config.get("highlight_theme", "monokai")
    highlight_path = Path(highlight_theme)
    if not highlight_path.suffix:
        highlight_path = highlight_path.with_suffix(".css")

    paths_to_check = [
        highlight_path,
        source_root / "cached" / "reveal.js" / "plugin" / "highlight" / highlight_path.name,
        project_root / highlight_path.name
    ]

    highlight_css_path = None
    for path in paths_to_check:
        if path.exists():
            highlight_css_path = path            
            break
    # copy highlight to target
    if highlight_css_path:
        copy_file_if_different(
            str(highlight_css_path),
            str(target_theme_directory/highlight_css_path.name)
            )
    # Compile the target theme
    if not is_theme_precompiled:
        compile_scss(
                str(theme_path_in_compiler),
                str(theme_path_in_build)
            )
    # Cleanup
    if len(files_copied):
        logging.info("Removing temporary files from compiling theme.")
        files_copied = list(set(files_copied))
        files_copied.sort(reverse=True)
        cleanup_temp_files(files_copied)

def copy_reveal():
    """Copy relevant Reveal.js files to the build directory."""
    logging.info("Copying Reveal.js files...")

    source_root = Path(config["directories"]["source"]["root"]) / "cached" / "reveal.js"
    build_root = Path(config["directories"]["build"])
    project_root = Path(".")

    files_to_copy = [
        ("dist/reset.css", "src/css/reset.css"),
        ("dist/reveal.css", "src/css/reveal.css"),
        ("dist/reveal.js", "src/reveal.js"),
        ("dist/reveal.js.map", "src/reveal.js.map"),
        ("dist/reveal.esm.js", "src/reveal.esm.js"),
        ("dist/reveal.esm.js.map", "src/reveal.esm.js.map"),
    ]

    for src, dest in files_to_copy:
        src_path = source_root / src
        dest_path = build_root / dest

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        copy_file_if_different(str(src_path), str(dest_path))

    src_dir = source_root / "css" / "print"
    dest_dir = build_root / "src" / "css" / "print"

    dest_dir.mkdir(parents=True, exist_ok=True)
    compile_scss(str(src_dir / "paper.scss"), str(dest_dir / "paper.css"))
    compile_scss(str(src_dir / "pdf.scss"), str(dest_dir / "pdf.css"))

    logging.info("Looking for highlight.js theme...")
    highlight_theme = config.get("highlight_theme", "default")
    highlight_path = Path(highlight_theme)
    if not highlight_path.suffix:
        highlight_path = highlight_path.with_suffix(".css")

    highlight_css = None
    paths_to_check = [
        highlight_path,
        source_root / "plugin" / "highlight" / highlight_path.name,
        project_root / highlight_path.name
    ]

    for path in paths_to_check:
        if path.exists():
            highlight_css = path.name
            break

    if highlight_css:
        src_path = source_root / "plugin" / "highlight" / "monokai.css" if highlight_css == "default" else highlight_path
        dest_path = build_root / "src" / "theme" / highlight_css

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        logging.info(f"Copying {src_path} to {dest_path}")
        copy_file_if_different(str(src_path), str(dest_path))

def generate_presentation(decks=None):
    """Generate the final presentation HTML."""
    logging.info("Generating presentations...")

    # Initialize an empty array to collect presentation data for TOC
    presentations_for_toc = []
    rendered_presentations = []

    # Create a Jinja2 environment and add the custom filter
    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["to_html_attrs"] = dict_to_html_attrs

    # Load the reveal template
    pres_template_path = os.path.join(
        config["directories"]["source"]["root"], config["reveal_template"]
    ).replace("\\", "/")
    # Load your template
    template = env.get_template(pres_template_path)

    presentation_root = os.path.join(
        config["directories"]["source"]["root"],
        config["directories"]["source"]["presentation_root"],
    )

    # Get libraries directory name for reference checking
    libraries_dir = config["directories"]["source"]["libraries"]

    # First pass: render all presentations and collect file references
    for presentation_folder in os.listdir(presentation_root):
        if decks and presentation_folder not in decks:
            continue

        presentation_path = os.path.join(presentation_root, presentation_folder)

        # Check if it's a directory
        if not os.path.isdir(presentation_path):
            continue

        # Initialize deck object
        deck = {
            "title": presentation_folder,
            "slides": None,
            "titlepage": None,
            "footer": None,
            "head": None,
        }

        # Check for presentation.json
        presentation_json_path = os.path.join(presentation_path, "presentation.json")
        if os.path.exists(presentation_json_path):
            with open(presentation_json_path, "r") as f:
                presentation_data = json.load(f)
            deck.update(presentation_data)

        # Parse slides based on the conditions
        slide_order = deck.get("slides", None)

        if slide_order is None:
            # locate html files in presentation folder
            slide_order = sorted(
                [
                    os.path.basename(f)
                    for f in glob.glob(os.path.join(presentation_path, "*.html"))
                ]
            )
        elif len(slide_order):
            slide_order = [
                slide
                for slide in slide_order
                if os.path.exists(os.path.join(presentation_path, slide))
            ]

        # Clear/initialize deck["slides"] to append the parsed slides
        deck["slides"] = []
        logging.info(f"Parsing slide files: {json.dumps(slide_order)}")
        for slide_file in slide_order:
            slide_path = os.path.join(presentation_path, slide_file)
            deck["slides"].append(parse_slide(slide_path))
        logging.info("Slides parsed successfully.")

        page_title_str = deck["title"]
        logging.info(f"Parsing titlepage for '{page_title_str}'...")
        titlepage = deck.get("titlepage")
        if titlepage:
            validate_titlepage(titlepage)
            page_title_str = " ".join(titlepage["headline"]).strip()
            deck["titlepage"] = titlepage
        
        deck["title"] = str(page_title_str)    
        
        logging.info(f"Finished parsing '{str(page_title_str)}'.")

        # Render the HTML
        rendered_html = template.render(deck=deck)
        
        # Store rendered HTML for later
        rendered_presentations.append({
            'folder': presentation_folder,
            'html': rendered_html,
            'deck': deck
        })

    # Copy all library files
    copy_libraries()

    # Second pass: write out all presentations
    for presentation in rendered_presentations:
        pres_link = f"{presentation['folder']}.html"
        output_path = os.path.join(config["directories"]["build"], pres_link)
        
        with open(output_path, "w") as f:
            f.write(beautify_html(presentation['html'], 2))

        # Add to TOC data
        presentations_for_toc.append({
            "id": pres_link,
            "name": presentation['deck']["title"],
            "titlepage": presentation['deck'].get("titlepage", ""),
        })

    # Generate the TOC
    generate_toc(
        presentations_for_toc,
        os.path.join(config["directories"]["source"]["root"], config["toc_template"]),
        config["directories"]["build"],
        config["info"].get("project_title", "Table of Contents")
    )


def generate_toc(presentations, template, target, project_title):
    """
    Generate a Table of Contents (TOC) HTML file based on the given presentations and template.

    Parameters:
    - presentations (list of dict): A list of dictionaries containing 'id' and 'name' fields.
    - template (str): The file path to the HTML template.
    - target (str): The directory where the rendered HTML should be saved.

    Returns:
    None
    """
    logging.info("Preparing TOC...")
    # Set up the Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(os.path.dirname(template)),
        autoescape=select_autoescape(["html", "xml"]),
    )

    # Load the template
    toc_template = env.get_template(os.path.basename(template))
    # Prepare the data for the template
    toc_links = [
        {
            "link": f"./{presentation['id']}",
            "name": presentation["name"].title(),
            "titlepage": (
                presentation["titlepage"] if presentation.get("titlepage") else {}
            ),
        }
        for presentation in presentations
    ]

    # Render the template
    rendered_toc = toc_template.render(toc_links=toc_links, project_title=project_title)

    # Save the rendered HTML to the target directory
    target_path = os.path.join(target, "index.html")
    with open(target_path, "w") as f:
        f.write(rendered_toc)

    logging.info(f"Generated TOC and saved at {target_path}")

def get_build_decks(config, decks=None):
    if not decks:
        return None

    # Define the presentation root
    presentation_root = os.path.join(
        config["directories"]["source"]["root"],
        config["directories"]["source"]["presentation_root"],
    )

    # Initialize the list to return
    deck_list = []

    # Check if 'decks' is a path to a file or a comma-separated string
    if os.path.isfile(decks):
        deck_list = parse_delimited_file(decks)
        logging.info(f"  Parsed decks file '{decks}'")
    else:
        # If it's a comma-separated string
        deck_list = [deck.strip() for deck in decks.split(',') if deck.strip()]
        logging.info("  Parsed decks list string.")

    # Filter out directories not present in the presentation root
    valid_decks = [deck for deck in deck_list if os.path.isdir(os.path.join(presentation_root, deck))]

    if not valid_decks:
        msg = "No valid directories found in the specified decks."
        logging.error(msg)
        raise ValueError(msg)

    return valid_decks

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Setup Reveal.js presentation environment.')
    parser.add_argument('--root', type=str, default=os.getcwd(), help='Target directory for setup')
    parser.add_argument('--clean', action='store_true', help='Perform a clean build')
    parser.add_argument('--decks', type=str, default=None, help='Comma-separated list of decks or a path to a file with deck names')
    parser.add_argument('--log-level', type=str, default='INFO', help='Set the logging level')
    args = parser.parse_args()

    config = read_config(args.root)
    
    # Initialize jogger for tracking errors/success
    initialize_logging(config, args.log_level)
    
    # Log status
    logging.info(f"Building {config["info"].get("project_title", config["info"].get("short_title", "RevealPack Presentations"))}")
    
    # Handle clean build
    if args.clean:
        logging.info("Performing clean build!")
        clean_build_directory(config)

    # Determine decks to build
    decks_to_build = get_build_decks(config,args.decks)
    
    # Initialize Jinja2 environment
    env = Environment(loader=FileSystemLoader("."))

    # Step 1: Copy libraries
    # copy_libraries()

    # Step 2: Copy plugins
    copy_plugins()

    # Step 3: Compile styles
    copy_and_compile_styles()
    
    # Step 4: Compile theme
    compile_theme()

    # Step 5: Copy over Reveal.js files
    copy_reveal()

    # Step 6: Generate presentation
    generate_presentation(decks=decks_to_build)
