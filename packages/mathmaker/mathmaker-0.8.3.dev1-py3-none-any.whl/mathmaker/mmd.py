# -*- coding: utf-8 -*-

# Copyright 2006-2017 Nicolas Hainaux <nh.techn@gmail.com>

# This file is part of Mathmaker.

# Mathmaker is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# Mathmaker is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Mathmaker; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import sys
import signal
import socket
import logging
from pathlib import Path

import daemon
from daemon.pidfile import PIDLockFile
from waitress import serve

from mathmaker import __version__
from mathmaker.lib.tools.mmd_app import mmd_app
from mathmaker.lib.tools.config_utils import configure_logging


def get_pidfile_path():
    pid_filepath = '/var/run/mathmakerd.pid'
    if os.geteuid() != 0:
        pid_filepath = str(Path.home() / '.local/run/mathmakerd.pid')
    Path(pid_filepath).parent.mkdir(parents=True, exist_ok=True)
    return pid_filepath


def setup_working_directory():
    # /var/lib/mathmakerd requires root rights;
    # otherwise fallback to another place
    default_wd = Path('/var/lib/mathmakerd')
    try:
        default_wd.mkdir(parents=True, exist_ok=True)
        wd = default_wd
    except PermissionError:
        wd = Path.home() / '.local/share/mathmakerd'
        wd.mkdir(parents=True, exist_ok=True)
        print(f"Cannot use {default_wd}, using {wd} instead")
    return wd


def run_server(settings):
    """Run the server regardless of mode (daemon or foreground)"""
    server_logger = logging.getLogger('server')

    # Test if port is already in use
    try:
        server_logger.info(
            f"Test if port {settings['port']} is already in use")
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.bind(('', settings['port']))
        test_socket.close()
    except OSError as excinfo:
        if 'Address already in use' in str(excinfo):
            server_logger.error(f"Another process is already listening "
                                f"to port {settings['port']}. Aborting.")
            sys.exit(1)
        else:
            raise

    server_logger.info('Startup waitress server')
    serve(mmd_app(), host=settings['host'], port=settings['port'])


def handle_signal(signum, frame):
    sig_name = signal.Signals(signum).name
    logging.getLogger().info(f'Received {sig_name}, shutting down.')
    sys.exit(0)


def entry_point():
    main_logger, log_dir, settings = configure_logging()
    main_logger.info(f'Starting mathmakerd {__version__}')

    foreground_mode = '--foreground' in sys.argv

    if foreground_mode:
        main_logger.info('Running in foreground mode')
        run_server(settings)
    else:
        daemon_context = daemon.DaemonContext(
            working_directory=setup_working_directory(),
            umask=0o002,
            stdout=open(log_dir / 'stdout.log', 'w+'),
            stderr=open(log_dir / 'stderr.log', 'w+'),
            pidfile=PIDLockFile(get_pidfile_path())
        )

        daemon_context.files_preserve = [
            handler.stream.fileno() for handler in main_logger.handlers
            if hasattr(handler, 'stream') and hasattr(handler.stream, 'fileno')
        ]

        signal.signal(signal.SIGTERM, handle_signal)
        signal.signal(signal.SIGINT, handle_signal)
        # SIGHUP would mean reload configuration, not stop daemon
        # so, would require a dedicated handler.
        # signal.signal(signal.SIGHUP, handle_sighup)
        with daemon_context:
            main_logger.info('Daemon context initialized')
            run_server(settings)
