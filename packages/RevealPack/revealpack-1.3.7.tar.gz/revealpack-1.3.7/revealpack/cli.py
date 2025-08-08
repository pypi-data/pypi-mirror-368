import click
import os
import subprocess
import sys
import webbrowser
import http.server
import socketserver
from revealpack import copy_config_and_assets
from ._version import get_version, get_description

@click.group()
@click.version_option(
    version=get_version(),
    message=(
        '%(prog)s version %(version)s\n'
        f'{get_description()}'
    ),
    prog_name="RevealPack"
)
def cli():
    """RevealPack - A CLI tool for managing Reveal.js presentation packages"""
    pass

@cli.command()
@click.option('--destination', default=None, help='Destination path to copy config.json and assets')
def init(destination):
    """Initialize the file structure and copy config.json and assets to the specified destination."""
    copy_config_and_assets(destination)

@cli.command()
@click.argument('args', nargs=-1)
@click.option('-r', '--root', default=os.getcwd(), help='Root directory for setup')
def setup(args, root):
    """Setup the environment for building presentations."""
    setup_script = os.path.join(os.path.dirname(__file__), 'setup.py')
    python_executable = sys.executable
    try:
        subprocess.run([python_executable, setup_script, '--root', root] + list(args), check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during setup: {e}")

@cli.command()
@click.argument('args', nargs=-1)
@click.option('-r', '--root', default=os.getcwd(), help='Root directory for build')
@click.option('-c', '--clean', is_flag=True, help='Perform a clean build')
@click.option('-d', '--decks', type=click.Path(exists=True, dir_okay=False, readable=True), help='Specify decks to build (comma-separated values or a file path)')
@click.option('-l', '--log-level', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']), default='INFO', help='Set the logging level')
def build(args, root, clean, decks, log_level):
    """Build the presentation package."""

    build_script = os.path.join(os.path.dirname(__file__), 'build.py')
    python_executable = sys.executable
    build_args = ['--root', root] + list(args)

    # Handle clean build
    if clean:
        build_args.append('--clean')

    # Handle deck specification
    if decks:
        build_args.append('--decks')
        build_args.append(decks)

    # Handle log level
    if log_level:
        build_args.append('--log-level')
        build_args.append(log_level)

    try:
        subprocess.run([python_executable, build_script] + build_args, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during build: {e}")

@cli.command()
@click.argument('args', nargs=-1)
@click.option('-r', '--root', default=os.getcwd(), help='Root directory for serve')
@click.option('-n', '--no-build', is_flag=True, help='Skip build and only run the server')
@click.option('-c', '--clean', is_flag=True, help='Perform a clean build before serving')
@click.option('-d', '--decks', type=str, help='Specify decks to build (comma-separated values or a file path)')
def serve(args, root, no_build, clean, decks):
    """Serve the presentation for live editing."""
    serve_script = os.path.join(os.path.dirname(__file__), 'serve.py')
    python_executable = sys.executable
    try:
        cmd = [python_executable, serve_script, '--root', root]
        if no_build:
            cmd.append('--no-build')
        if clean:
            cmd.append('--clean')
        if decks:
            cmd.extend(['--decks', decks])
        cmd += list(args)
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during serve: {e}")


@cli.command()
@click.argument('args', nargs=-1)
@click.option('-r', '--root', default=os.getcwd(), help='Root directory for package')
@click.option('-t', '--target-dir', default=None, help='Directory to create the package')
@click.option('-n', '--no-build', is_flag=True, help='Skip the build step')
@click.option('-c', '--clean', is_flag=True, help='Perform a clean build before packaging')
@click.option('-d','--decks', type=click.Path(exists=True, dir_okay=False, readable=True), help='Specify decks to build (comma-separated values or a file path)')
def package(args, root, target_dir, no_build, clean, decks):
    """Package the presentation into a distributable format."""
    package_script = os.path.join(os.path.dirname(__file__), 'package.py')
    python_executable = sys.executable
    try:
        cmd = [python_executable, package_script, '--root', root]
        
        if target_dir is not None:
            cmd.extend(['--target-dir', target_dir])
        
        if no_build:
            cmd.append('--no-build')
        
        if clean or decks:
            cmd.append('--clean')
        
        if decks:
            cmd.extend(['--decks', decks])
        
        subprocess.run(cmd + list(args), check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during packaging: {e}")


@cli.command()
def docs():
    """Display the documentation for revealpack."""
    doc_dir = os.path.join(os.path.dirname(__file__), 'site')

    if os.path.exists(doc_dir):
        port = 8000
        os.chdir(doc_dir)
        
        handler = http.server.SimpleHTTPRequestHandler
        httpd = socketserver.TCPServer(("", port), handler)

        webbrowser.open(f"http://127.0.0.1:{port}")
        print(f"Serving documentation on port {port}...")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down server.")
            httpd.shutdown()
    else:
        print("Documentation not found.")

if __name__ == '__main__':
    cli()
