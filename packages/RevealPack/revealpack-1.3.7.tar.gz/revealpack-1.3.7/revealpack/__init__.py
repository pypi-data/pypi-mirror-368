import os
import json
import shutil

__version__ = "1.3.7"
__description__ = f"RevealPack v{__version__} - A CLI tool for managing Reveal.js presentation packages"

def copy_file_or_directory(src, dest):
    """Copy a file or directory to the specified destination."""
    if os.path.isdir(src):
        if os.path.exists(dest):
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
    else:
        shutil.copy(src, dest)

def generate_config(destination):
    config_data = {
        "info": {
            "author": "Your Name",
            "authors": [
                "Your Name"
            ],
            "short_title": "Lectures",
            "project_title": "Science Lectures",
            "year": "2024",
            "version": "1.0.0",
            "keywords": []
        },
        "directories": {
            "build": "build",
            "package": "dist",
            "source": {
                "root": "source",
                "presentation_root": "decks",
                "libraries": "lib"
            }
        },
        "packages": {
            "reveal.js": "5.2.1",
            "reveal_plugins": {
                "built_in": [
                    "notes",
                    "highlight",
                    "math"
                ],
                "external": {},
                "plugin_configurations": {
                    "mathjax3": {
                        "loader": {
                            "load": [
                                "[tex]/html"
                            ]
                        },
                        "tex": {
                            "packages": {
                                "'[+]'": [
                                    "html"
                                ]
                            },
                            "inlineMath": [
                                ["$", "$"],
                                ["\\(", "\\)"]
                            ]
                        },
                        "options": {
                            "skipHtmlTags": [
                                "script",
                                "noscript",
                                "style",
                                "textarea",
                                "pre"
                            ]
                        }
                    },
                    "notes": {},
                    "highlight": {}
                }
            }
        },
        "theme": "simple",
        "reveal_template": "reveal_template.html",
        "toc_template": "toc_template.html",
        "logging": "info",
        "highlight_theme": "monokai",
        "custom_scripts": [],
        "force_plugin_download": True,
        "reveal_configurations": {
            "center": False,
            "controls": True,
            "controlsBackArrows": "faded",
            "controlsLayout": "bottom-right",
            "display": "block",
            "fragments": True,
            "hideAddressBar": True,
            "hideCursorTime": 5000,
            "keyboard": True,
            "mobileViewDistance": 3,
            "mouseWheel": False,
            "navigationMode": "default",
            "overview": True,
            "pdfMaxPagesPerSlide": 1,
            "pdfSeparateFragments": False,
            "preloadIframes": True,
            "progress": False,
            "showSlideNumber": "print",
            "sortFragmentsOnSync": True,
            "touch": True,
            "transition": "fade",
            "transitionSpeed": "default",
            "viewDistance": 3,
            "width": 1920,
            "height": 1080,
            "margin": 0.081,
            "minScale": 0.1,
            "maxScale": 1.56,
        }
    }

    # Determine the path to save the config.json file
    if destination:
        config_path = os.path.join(destination, "config.json")
    else:
        config_path = "config.json"

    # Write the config data to the config.json file
    with open(config_path, 'w') as config_file:
        json.dump(config_data, config_file, indent=4)

def copy_config_and_assets(destination=None):
    """Copy config.json and assets to the specified destination or current working directory."""
    current_dir = os.path.dirname(__file__)
    config_file = os.path.join(current_dir, 'config.json')
    assets_dir = os.path.join(current_dir, 'assets')

    if not destination:
        destination = os.getcwd()

    destination_assets = os.path.join(destination, 'assets')

    generate_config(destination)
    copy_file_or_directory(assets_dir, destination_assets)
    print(f"config.json and assets have been copied to {destination}")
