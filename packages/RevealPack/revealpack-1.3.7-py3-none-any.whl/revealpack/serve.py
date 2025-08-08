import os
import sys
import subprocess
import time
import shutil
import threading
import logging
import glob
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from _utils.config_operations import read_config, initialize_logging


class Watcher:
    def __init__(self, watch_directory, build_directory, clean=False, decks=None):
        self.watch_directory = watch_directory
        self.build_directory = build_directory
        self.clean = clean
        self.decks = decks
        self.event_handler = WatchHandler(clean=self.clean, decks=self.decks)
        self.observer = Observer()

    def run(self):
        self.observer.schedule(self.event_handler, self.watch_directory, recursive=True)
        self.observer.start()
        try:
            while True:
                pass
        except:
            self.observer.stop()
            logging.info("Observer stopped")


class WatchHandler(FileSystemEventHandler):
    debounce_delay = 3  # prevent multiple rapid triggers
    cooldown_time = 35  # refractory period after first build
    last_build_time = 0
    timer = None
    pending_trigger = False

    def __init__(self, clean=False, decks=None):
        self.clean = clean
        self.decks = decks

    def trigger(self):
        current_time = time.time()
        if current_time - WatchHandler.last_build_time < WatchHandler.cooldown_time:
            logging.info("Build request ignored due to cooldown.")
            return

        logging.info("Triggering build...")
        build_command = ["revealpack", "build"]
        if self.clean:
            build_command.append("--clean")
        if self.decks:
            build_command.extend(["--decks", self.decks])

        try:
            subprocess.run(build_command)
            WatchHandler.last_build_time = time.time()
            logging.info("Successfully ran build.py")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to run build.py: {e}")

    def process(self, event):
        logging.info(f"Event type: {event.event_type} at {event.src_path}")

        if WatchHandler.pending_trigger:
            if WatchHandler.timer:
                WatchHandler.timer.cancel()
        else:
            WatchHandler.pending_trigger = True

        WatchHandler.timer = threading.Timer(
            WatchHandler.debounce_delay, self.trigger
        )
        WatchHandler.timer.start()

    def on_modified(self, event):
        self.process(event)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Serve the presentation with watcher.')
    parser.add_argument('--root', type=str, default=os.getcwd(), help='Target directory for setup')
    parser.add_argument('-n', '--no-build', action='store_true', help='Skip build and only run the server')
    parser.add_argument('-c', '--clean', action='store_true', help='Perform a clean build before serving')
    parser.add_argument('-d', '--decks', type=str, help='Specify decks to build (comma-separated values or a file path)')
    args = parser.parse_args()

    config = read_config(args.root)
    initialize_logging(config)

    watch_directory = os.path.join(
        config["directories"]["source"]["root"],
        config["directories"]["source"]["presentation_root"],
    )
    build_directory = config["directories"]["build"]

    if not args.no_build:
        logging.info(f"Starting build watch on {watch_directory}")
        watcher = Watcher(watch_directory, build_directory, clean=args.clean, decks=args.decks)
        watcher_thread = threading.Thread(target=watcher.run)
        watcher_thread.daemon = True
        watcher_thread.start()

    http_service = subprocess.Popen(f"http-server {build_directory} -o", shell=True)

    try:
        while True:
            pass
    except KeyboardInterrupt:
        logging.info("Shutting down server.")
        if not args.no_build:
            watcher.observer.stop()
            watcher.observer.join()
        http_service.kill()
