# RevealPack

**A comprehensive CLI tool for managing and building multiple Reveal.js presentations with shared themes and resources.**

RevealPack is designed for creating suites of presentations that share themes and resources, such as lecture series, multi-day seminars, or training programs. It abstracts the slide deck creation process while providing complete control over individual slides or groups of slides within each presentation.

## 🚀 Key Features

- **Multi-Presentation Management**: Create and manage multiple presentations from a single project
- **Shared Resources**: Common libraries, themes, and assets across all presentations
- **Flexible Content**: Support for HTML, Markdown, and mixed content slides
- **Live Development**: Real-time preview with automatic rebuilds on file changes
- **Theme Compilation**: SCSS/SASS support with Dart Sass compilation
- **Plugin Management**: Built-in and external plugin support with automatic downloading
- **Distribution Ready**: Package presentations for standalone distribution
- **Customizable**: Extensive configuration options for themes, plugins, and presentation settings
- **Print Control**: Enhanced print functionality with `print-invisible` class and `+show` parameter support

## 📋 Requirements

- **Python** >= 3.12 (3.9+ supported, 3.12+ recommended)
- **Dart Sass CLI** - Required for SCSS/SASS theme compilation
- **Reveal.js** >= 4.0.0 (tested with 5.2.1, backwards compatible with 4.x)

### Install Dart Sass

RevealPack requires the Dart Sass CLI to compile SCSS/SASS theme files. **The build process will fail without it.**

**Install Dart Sass from the official website:**
- Visit [https://sass-lang.com/install](https://sass-lang.com/install)
- Follow the installation instructions for your operating system
- Ensure `sass` is available in your system PATH

**Alternative installation methods:**
```bash
# macOS (using Homebrew)
brew install sass/sass/sass

# Windows (using Chocolatey)
choco install sass

# Linux (using npm)
npm install -g sass
```

**Verify installation:**
```bash
sass --version
```

## 🛠️ Installation

### Install RevealPack from PyPI

```bash
pip install revealpack
```

*Note: Use the appropriate method for your setup, e.g., `pip3` or `python -m pip...`*

## 🏗️ Project Structure

RevealPack creates a structured project with the following organization:

```
your-project/
├── config.json              # Project configuration
├── assets/                  # RevealPack assets and themes
├── source/                  # Source files
│   ├── lib/                 # Shared libraries and assets
│   ├── decks/               # Individual presentation decks
│   │   ├── lecture-01/      # Each subdirectory = one presentation
│   │   │   ├── slide1.html
│   │   │   ├── slide2.html
│   │   │   └── presentation.json
│   │   └── lecture-02/
│   ├── cached/              # Downloaded packages (Reveal.js, plugins)
│   ├── reveal_template.html # Generated presentation template
│   └── toc_template.html    # Generated table of contents template
└── build/                   # Built presentations (output)
    ├── index.html           # Table of contents
    ├── lecture-01/
    └── lecture-02/
```

## 🚀 Quick Start

### 1. Initialize a New Project

```bash
# Create a new directory and navigate to it
mkdir my-presentations
cd my-presentations

# Initialize RevealPack project
revealpack init
```

This creates:
- `config.json` with default settings
- `assets/` directory with RevealPack resources

### 2. Configure Your Project

Edit `config.json` to customize:
- Project information (title, authors, version)
- Directory structure
- Reveal.js version and plugins
- Theme settings
- Presentation configurations

### 3. Set Up Development Environment

```bash
revealpack setup
```

This:
- Creates necessary directories
- Downloads Reveal.js and specified plugins
- Validates theme configuration
- Generates presentation templates

### 4. Create Your Presentations

Add content to `source/decks/`:
- Each subdirectory becomes a separate presentation
- Use HTML or Markdown for slides
- Optionally add `presentation.json` for metadata

### 5. Build Presentations

```bash
revealpack build
```

This compiles all presentations with:
- Theme compilation (SCSS → CSS)
- Plugin integration
- Asset copying
- HTML generation

### 6. Serve for Development

```bash
revealpack serve
```

Starts a local server with live reloading for development.

## 📖 Commands Reference

### `revealpack init [--destination PATH]`
Initialize a new RevealPack project by copying configuration and assets.

### `revealpack setup [--root PATH]`
Set up the development environment:
- Creates project directories
- Downloads Reveal.js and plugins
- Validates theme configuration
- Generates templates

### `revealpack build [OPTIONS]`
Build all presentations or specified decks.

**Options:**
- `--root PATH`: Root directory (default: current directory)
- `--clean`: Perform clean build (removes existing build files)
- `--decks LIST`: Build specific decks (comma-separated or file path)
- `--log-level LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### `revealpack serve [OPTIONS]`
Serve presentations with live reloading for development.

**Options:**
- `--root PATH`: Root directory (default: current directory)
- `--no-build`: Skip initial build, serve existing files only
- `--clean`: Perform clean build before serving
- `--decks LIST`: Build and serve specific decks

### `revealpack package [OPTIONS]`
Package presentations for distribution (creates Electron app).

**Options:**
- `--root PATH`: Root directory (default: current directory)
- `--target-dir PATH`: Output directory for package
- `--no-build`: Skip build step
- `--clean`: Perform clean build before packaging
- `--decks LIST`: Package specific decks

### `revealpack docs`
Open RevealPack documentation in your browser.

## ⚙️ Configuration

The `config.json` file controls all aspects of your project:

### Project Information
```json
{
  "info": {
    "authors": ["Your Name"],
    "short_title": "Lectures",
    "project_title": "Science Lectures",
    "year": "2024",
    "version": "1.0.0"
  }
}
```

### Directory Structure
```json
{
  "directories": {
    "build": "build",
    "package": "dist",
    "source": {
      "root": "source",
      "presentation_root": "decks",
      "libraries": "lib"
    }
  }
}
```

### Reveal.js and Plugins
```json
{
  "packages": {
    "reveal.js": "5.2.1",
    "reveal_plugins": {
      "built_in": ["notes", "highlight", "math"],
      "external": {
        "plugin-name": {
          "version": "1.0.0",
          "url": "https://example.com/plugin.zip",
          "alias": "optional-alias",
          "main": "main-file"
        }
      }
    }
  }
}
```

**Note:** RevealPack is tested with Reveal.js 5.2.1 and is backwards compatible with Reveal.js 4.x versions.

### Theme Configuration
```json
{
  "theme": "path/to/theme.scss",
  "highlight_theme": "monokai",
  "custom_scripts": ["path/to/script.js"]
}
```

### Reveal.js Settings
```json
{
  "reveal_configurations": {
    "center": false,
    "controls": true,
    "transition": "fade",
    "width": 1920,
    "height": 1080
  }
}
```

## 🎨 Theming

RevealPack supports both pre-compiled CSS and SCSS/SASS themes:

### SCSS/SASS Themes
- Create `.scss` or `.sass` files
- Use variables, mixins, and nested rules
- Automatic compilation with Dart Sass
- Hot reloading during development

### Theme Structure
```scss
// Example theme.scss
$primary-color: #007acc;
$background-color: #f8f9fa;

.reveal {
  background-color: $background-color;
  
  .slides section {
    color: $primary-color;
  }
}
```

## 📝 Content Creation

### HTML Slides
Create individual HTML files for each slide:

```html
<!-- slide1.html -->
<section>
  <h1>Welcome to My Presentation</h1>
  <p>This is the first slide</p>
</section>
```

### Markdown Support
Use Markdown for simpler content:

```markdown
# Welcome to My Presentation

This is the first slide

---

## Second Slide

- Point 1
- Point 2
- Point 3
```

### Presentation Metadata
Add `presentation.json` to customize individual presentations:

```json
{
  "titlepage": {
    "headline": [
      "Lecture 01",
      "Introduction"
    ],
    "background": {
      "image": "lib/img/cover.png",
      "size": "cover"
    },
    "by": "Author Name",
    "byinfo": [
      "Date",
      "Course Info"
    ],
    "notes": []
  },
  "footer": {
    "left": "Lecture 01",
    "right": "<a href=\"https:\\\\github.com\\Khlick\\revealpack\" target=\"_blank\" rel=\"noopener noreferrer\">&#169;2025</a>"
  },
  "slides": [
    "intro.html",
    "group1.html",
    "group2.html",
    "outro.html"
  ]
}
```

## 🖨️ Print Functionality

RevealPack includes enhanced print functionality that extends Reveal.js's built-in print capabilities:

### Print Modes

- **Normal Print**: `?print-pdf` - Standard Reveal.js print mode
- **Show Hidden Elements**: `?print-pdf+show` - Shows elements with the `print-invisible` class

### Print-Invisible Class

Use the `print-invisible` CSS class to hide elements during normal print mode:

```html
<div class="print-invisible">
  <p>This content is hidden in print mode by default</p>
</div>
```

When using `?print-pdf+show`, these elements become visible in the printed output.

### Use Cases

- **Speaker Notes**: Hide speaker notes in normal print but show them when needed
- **Interactive Elements**: Hide interactive elements that don't work in print
- **Supplementary Content**: Hide additional content that's only relevant during presentation
- **Debug Information**: Hide development/debug information in final prints

## 🔧 Troubleshooting

### Dart Sass Issues

If you encounter errors related to SCSS compilation:

1. **Check if Dart Sass is installed:**
   ```bash
   sass --version
   ```

2. **If not installed, install Dart Sass:**
   - Visit [https://sass-lang.com/install](https://sass-lang.com/install)
   - Follow the installation instructions for your operating system

3. **If installed but not found, check your PATH:**
   - Ensure the directory containing the `sass` executable is in your system PATH
   - Restart your terminal/command prompt after installation

4. **Environment variable override:**
   You can specify a custom path to the Dart Sass executable using the `REVEALPACK_SASS_PATH` environment variable:
   ```bash
   export REVEALPACK_SASS_PATH=/path/to/your/sass
   revealpack build
   ```

### Common Error Messages

- **"Dart Sass CLI not found"**: Install Dart Sass from the official website
- **"SCSS compilation failed"**: Check your SCSS syntax and ensure Dart Sass is properly installed
- **"Plugin download failed"**: Check your internet connection and plugin URLs
- **"Theme not found"**: Verify the theme path in `config.json`

## 🤝 Contributing

For more detailed information on development, see the [Developer's Guide](https://revealpack.readthedocs.io/en/latest/dev/).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.