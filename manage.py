#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import logging
import os
import socket
import sys
import time

import coloredlogs
import django
import gunicorn.app.wsgiapp
from django.core.management import call_command, execute_from_command_line


class SiteManager:
    """Class used to manage the site infrastructure and start it up."""

    def __init__(self, debug: bool) -> None:
        self.debug = debug
        self.logger = logging.getLogger("manager")

    def wait_for_postgres(self) -> None:
        """Wait for the PostgreSQL database specified in DATABASE_HOST and DATABASE_PORT."""
        self.logger.info("Waiting for PostgreSQL database..")

        # Get database URL based on environmental variable passed in
        host = os.environ["DATABASE_HOST"]
        port = int(os.environ["DATABASE_PORT"])

        # Attempt to connect to the database socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        attempts_left = 50
        while attempts_left:
            try:
                # Ignore 'incomplete startup packet'
                s.connect((host, port))
                s.shutdown(socket.SHUT_RDWR)
                self.logger.info("Database is ready.")
                break
            except socket.error:
                attempts_left -= 1
                self.logger.debug("Not ready yet, retrying.")
                time.sleep(3)
        else:
            self.logger.error("Database could not be found, exiting.")
            sys.exit(1)

    def run_migrations(self) -> None:
        """Run Postgres migrations."""
        self.logger.info("Applying migrations..")
        call_command("migrate")

    def setup_logging(self) -> None:
        """Setup the logging facilities using coloredlogs."""
        loglevel = (os.environ.get("LOG_LEVEL") or ("DEBUG" if self.debug else "INFO")).upper()
        fmt = "%(asctime)s %(name)s %(levelname)s: %(message)s"

        coloredlogs.install(logger=self.logger, level=loglevel, fmt=fmt)

        self.logger.debug("Logging successfully setup.")

    def run_server(self) -> None:
        """Prepare and run the web server."""
        in_reloader = os.environ.get("RUN_MAIN") == "true"

        django.setup()

        if not in_reloader:
            self.setup_logging()

        self.logger.info(
            f"Starting server.. Using version {os.environ.get('GIT_SHA', '<unspecified>')!r}."
        )
        if self.debug:
            self.logger.warning("Development mode is enabled.")

            if os.environ.get("DATABASE_HOST") is not None:
                self.wait_for_postgres()

        self.logger.info(f"Using database host `{os.environ.get('DATABASE_HOST', 'db.sqlite3')}`")

        if not in_reloader:
            if os.environ.get("NO_MIGRATION") is None:
                self.run_migrations()

            if self.debug:
                if os.environ.get("NO_COLLECT") is None:
                    self.logger.info("Collecting static..")
                    call_command("collectstatic", "--no-input")

        # Run the development server
        if self.debug:
            call_command("runserver", "0.0.0.0:8000")
            return

        # Patch the arguments for gunicorn
        sys.argv = [
            "gunicorn",
            "--preload",
            "-b",
            "0.0.0.0:8000",
            "app.wsgi:application",
            "--threads",
            "4",
            "-w",
            os.environ.get("WORKER_COUNT", "4"),
            "--max-requests",
            "1000",
            "--max-requests-jitter",
            "50",
        ]

        # Run gunicorn for the production server.
        gunicorn.app.wsgiapp.run()


def main() -> None:
    """Entry point for Django management script."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

    # Use the custom site manager for launching the server
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        SiteManager(os.environ.get("DEBUG") is not None).run_server()

    # Pass any others directly to standard management commands
    else:
        execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
