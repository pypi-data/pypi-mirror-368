import os
import shutil
import argparse
import subprocess
import sys
import logging
import json
from _utils.config_operations import read_config, initialize_logging
from _utils.string_operations import sanitize_name

def create_package_json(config, dest_dir):
    package_info = config['info']
    package_title = sanitize_name(package_info.get('short_title','project_name'))
    package_json = {
        "name": package_title,
        "version": package_info.get('version','1.0.0'),
        "description": package_info.get('project_title',''),
        "main": "main.js",
        "authors": package_info['authors'],
        "author": package_info.get("author", str(package_info.get('authors')[0])),
        "license": "MIT",
        "scripts": {
            "start": "electron .",
            "package-win": "electron-builder --win",
            "package-mac": "electron-builder --mac",
            "test": "echo \"No tests specified\" && exit 1"
        },
        "keywords": package_info.get('keywords', []),
        "devDependencies": {
            "electron": "^31.4.0",
            "electron-builder": "^24.13.3"
        },
        "build": {
            "appId": f"com.{package_title.lower()}",
            "productName": package_title,
            "directories": {
                "output": "dist"
            },
            "files": [
                "src/**/*",
                "main.js"
            ],
            "win": {
                "target": [
                    {
                    "target": "nsis",
                    "arch": ["x64", "ia32"]
                    }
                ],
                "icon": "assets/icons/win/icon.ico",
                "artifactName": f"{package_title}-v${{version}}-win-${{arch}}.exe"
            },
            "mac": {
                "target": [
                    {
                    "target": "dmg",
                    "arch": ["x64", "arm64", "universal"]
                    }
                ],
                "icon": "assets/icons/mac/icon.icns",
                "minimumSystemVersion": "10.12",
                "artifactName": f"{package_title}-v${{version}}-mac-${{arch}}.dmg",
                "hardenedRuntime": True,
                "gatekeeperAssess": False
            },
            "nsis": {
                "oneClick": False,
                "allowToChangeInstallationDirectory": True,
                "createDesktopShortcut": True,
                "createStartMenuShortcut": True,
                "shortcutName": package_info.get('project_title',package_title)
            }
        }
    }
    package_json_path = os.path.join(dest_dir, 'package.json')
    with open(package_json_path, 'w') as f:
        json.dump(package_json, f, indent=2)
    logging.info(f"Created package.json at {package_json_path}")

def create_gitignore(dest_dir):
    gitignore_content = """# Node.js dependencies
node_modules/
npm-debug.log
yarn-error.log
package-lock.json
yarn.lock

# Logs
*.log
logs
*.log.*
logs/

# OS generated files
.DS_Store
Thumbs.db
ehthumbs.db
Desktop.ini

# Build directories
/dist
/out
/release-builds
/release-installers

# Temporary files
tmp/
temp/

# System files
*.swp
*.swo
*~
# Windows system files
$RECYCLE.BIN/
*.bak
*.ini
*.lnk
*.tmp
*.log
*.gid
*.dmp
*.mdmp
*.ldf
*.sdf

# Compiled binary addons (https://nodejs.org/api/addons.html)
build/Release

# Coverage directory used by tools like istanbul
coverage/

# NPM cache directory
.npm

# Grunt intermediate storage (https://gruntjs.com/creating-plugins#storing-task-files)
.grunt

# Bower dependency directory (https://bower.io/)
bower_components/

# NuGet packages
*.nupkg
*.snupkg

# VS Code directories
.vscode/

# SASS and other preprocessor cache
.sass-cache/
.ruby-sass-cache/

# lock files
*.lock
"""
    gitignore_path = os.path.join(dest_dir, '.gitignore')
    with open(gitignore_path, 'w') as f:
        f.write(gitignore_content)
    logging.info(f"Created .gitignore at {gitignore_path}")

def create_github_workflow(config, dest_dir):
    package_name = sanitize_name(config['info'].get('short_title','project_name'))
    workflow_content = f"""name: Build and Release {package_name}

on:
  push:
    tags:
      - "v*"

jobs:
  setup-release:
    runs-on: ubuntu-latest
    outputs:
      upload_url: ${{{{ steps.create_release.outputs.upload_url }}}}
    steps:
      - uses: actions/checkout@v4
      - name: Create Release
        id: create_release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
        with:
          tag_name: ${{{{ github.ref }}}}
          release_name: Release ${{{{ github.ref_name }}}}
          draft: false
          prerelease: false

  build-mac:
    needs: setup-release
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"
      - name: Install dependencies
        run: npm install
      - name: Build and package macOS
        run: |
          export GH_TOKEN=${{{{ secrets.GITHUB_TOKEN }}}}
          npm run package-mac
      - name: List output in dist directory
        run: ls -l dist/
      - name: Upload macOS Installers
        uses: softprops/action-gh-release@v2
        with:
          files: |
            ./dist/{package_name}-${{{{ github.ref_name }}}}-mac-x64.dmg
            ./dist/{package_name}-${{{{ github.ref_name }}}}-mac-arm64.dmg
            ./dist/{package_name}-${{{{ github.ref_name }}}}-mac-universal.dmg
        env:
          GITHUB_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}

  build-win:
    needs: setup-release
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"
      - name: Install dependencies
        run: npm install
      - name: Build and package Windows
        run: |
          $env:GH_TOKEN="${{{{ secrets.GITHUB_TOKEN }}}}"
          npm run package-win
        shell: pwsh
      - name: List output in dist directory
        run: dir dist
      - name: Upload Windows Installers
        uses: softprops/action-gh-release@v2
        with:
          files: |
            ./dist/{package_name}-${{{{ github.ref_name }}}}-win-x64.exe
            ./dist/{package_name}-${{{{ github.ref_name }}}}-win-ia32.exe
        env:
          GITHUB_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
"""
    workflow_path = os.path.join(dest_dir, '.github', 'workflows', 'build-and-release.yml')
    os.makedirs(os.path.dirname(workflow_path), exist_ok=True)
    with open(workflow_path, 'w') as f:
        f.write(workflow_content)
    logging.info(f"Created GitHub workflow file at {workflow_path}")

def create_main_js(dest_dir):
    main_js_content = """const { app, BrowserWindow } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1920,
        height: 1080,
        fullscreen: true,
        autoHideMenuBar: true,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true
        }
    });

    mainWindow.loadFile(path.join(__dirname, 'src', 'index.html'));

    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // Handle new window creation
    mainWindow.webContents.on('new-window', (event, url, frameName, disposition, options) => {
        event.preventDefault();
        options.width = mainWindow.getSize()[0];
        options.height = mainWindow.getSize()[1];
        event.newGuest = new BrowserWindow(options);
        event.newGuest.loadURL(url);
    });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

"""
    main_js_path = os.path.join(dest_dir, 'main.js')
    with open(main_js_path, 'w') as f:
        f.write(main_js_content)
    logging.info(f"Created main.js at {main_js_path}")

def create_readme(config,dest_dir):
    package_name = sanitize_name(config['info'].get('short_title','project_name'))
    readme_content = f"""# {package_name}

---

See releases for the current version for MacOS and Windows operating systems.
"""
    readme_path = os.path.join(dest_dir,"README.md")
    with open (readme_path,'w') as f:
        f.write(readme_content)
    logging.info(f"Created README.md at {readme_path}")

# Methods for handling argument parsing
def handle_target_dir(target_dir, config):
    if target_dir is None:
        logging.info("Using project target directory from config.json")
        target_dir = config["directories"].get("package", os.path.join(os.getcwd(), 'target'))

    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)
        logging.info(f"Created target directory: {target_dir}")
    else:
        logging.info(f"Using existing target directory: {target_dir}")
    
    return target_dir

def run_build_step(root, no_build, clean, decks):
    if not no_build:
        build_script = os.path.join(os.path.dirname(__file__), 'build.py')
        python_executable = sys.executable
        build_cmd = [python_executable, build_script, '--root', root]
        
        if clean:
            build_cmd.append('--clean')
        
        if decks:
            build_cmd.extend(['--decks', decks])

        try:
            subprocess.run(build_cmd, check=True)
            logging.info("Build completed successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"An error occurred during build: {e}")
            sys.exit(1)

def copy_build_output(build_src_dir, target_src_dir):
    # Clean Target Source
    if os.path.exists(target_src_dir):
        shutil.rmtree(target_src_dir)
        logging.info(f"Cleaned existing directory: {target_src_dir}")
    # Copy from build
    shutil.copytree(build_src_dir, target_src_dir)
    logging.info(f"Copied {build_src_dir} to {target_src_dir}")

def update_or_create_package(config, target_dir):
    package_json_path = os.path.join(target_dir, 'package.json')
    if os.path.exists(package_json_path):
        with open(package_json_path, 'r+') as f:
            existing_package_json = json.load(f)
            
            # Update the fields with new values from config, if they exist
            existing_package_json['version'] = config['info'].get('version', existing_package_json.get('version', '1.0.0'))
            existing_package_json['description'] = config['info'].get('project_title', existing_package_json.get('description', ''))
            existing_package_json['name'] = sanitize_name(config['info'].get('short_title', existing_package_json.get('name', 'project_name')))
            existing_package_json['author'] = config['info'].get("author", str(config['info'].get('authors', [existing_package_json.get('author', '')])[0]))
            existing_package_json['keywords'] = config['info'].get('keywords', existing_package_json.get('keywords', []))
            existing_package_json['build']['appId'] = f"com.{existing_package_json['name'].lower()}"
            existing_package_json['build']['productName'] = existing_package_json['name']
            existing_package_json['build']['nsis']['shortcutName'] = config['info'].get('project_title', existing_package_json['name'])

            f.seek(0)
            json.dump(existing_package_json, f, indent=2)
            f.truncate()

        logging.info(f"Updated package.json at {package_json_path}")
    else:
        create_package_json(config, target_dir)
        logging.info(f"Created package.json at {package_json_path}")
        # Handle other target creations if package.json is newly created
        create_readme(config,target_dir)
        create_gitignore(target_dir)
        create_github_workflow(config, target_dir)
        create_main_js(target_dir)

def main():
    parser = argparse.ArgumentParser(description='Package Reveal.js presentations into a distributable format.')
    parser.add_argument('-r', '--root', type=str, default=os.getcwd(), help='Root directory for packaging')
    parser.add_argument('-t', '--target-dir', type=str, default=None, help='Directory to create the package')
    parser.add_argument('-n', '--no-build', action='store_true', help='Skip the build step')
    parser.add_argument('-c', '--clean', action='store_true', help='Perform a clean build before packaging')
    parser.add_argument('-d', '--decks', type=str, help='Specify decks to build (comma-separated values or a file path)')
    args = parser.parse_args()

    # Load config and initialize logging
    config = read_config(args.root)
    initialize_logging(config)
    
    # Log status
    logging.info(f"Packaging {config['info'].get('project_title', config['info'].get('short_title', 'RevealPack Presentations'))}")

    # Build
    run_build_step(args.root, args.no_build, args.clean, args.decks)

    target_dir = handle_target_dir(args.target_dir, config)
    target_src_dir = os.path.join(target_dir, 'src')
    build_src_dir = config["directories"]["build"]
    copy_build_output(build_src_dir, target_src_dir)

    update_or_create_package(config, target_dir)

if __name__ == "__main__":
    main()
