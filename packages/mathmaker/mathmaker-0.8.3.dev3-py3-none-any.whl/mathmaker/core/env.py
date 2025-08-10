# -*- coding: utf-8 -*-

# Mathmaker creates automatically maths exercises sheets
# with their answers
# Copyright 2006-2017 Nicolas Hainaux <nh.techn@gmail.com>

# This file is part of Mathmaker.

# Mathmaker is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.

# Mathmaker is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Mathmaker; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import logging
from pathlib import Path

__myname__ = 'mathmaker'


def safe_home():
    """
    Return a usable ‘home’ path even if Path.home() or $HOME is invalid.
    Logs the decision steps.
    """
    logger = logging.getLogger(__name__)

    env_home = os.environ.get("HOME")
    path_home = Path.home()
    logger.debug(f"$HOME={env_home!r} ; Path.home()={str(path_home)!r}")

    # Usual case
    if path_home != Path("/") and path_home.exists():
        logger.debug(f"Using Path.home() : {path_home}")
        return path_home

    # Case of root with invalid home (or / as home)
    if os.geteuid() == 0:
        root_path = Path("/root")
        if root_path.exists():
            logger.warning(
                f"Invalid Path.home() ({path_home}) for root, "
                f"making use of {root_path}"
            )
            return root_path

    # Final fallback
    fallback = Path("/var/lib/mathmaker")
    if not fallback.exists():
        try:
            fallback.mkdir(parents=True, exist_ok=True)
            logger.warning(
                f"Create fallback directory {fallback} "
                f"because Path.home() is invalid ({path_home})"
            )
        except Exception as e:
            logger.error(f"Unable to create the fallback directory "
                         f"{fallback}: {e}")
    else:
        logger.warning(
            f"Making use of fallback directory {fallback} "
            f"because Path.home() is invalid ({path_home})"
        )

    return fallback


USER_LOCAL_SHARE = os.path.join(str(safe_home()), '.local', 'share',
                                __myname__)
