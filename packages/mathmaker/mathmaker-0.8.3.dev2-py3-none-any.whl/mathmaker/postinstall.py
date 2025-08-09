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
import platform
from pathlib import Path


def entry_point():
    print('[mm_postinstall] Starting post-install script...')

    if platform.system().lower() != 'freebsd':
        print('[mm_postinstall] Skipped: Not running on FreeBSD.')
        return

    if os.geteuid() != 0:
        print('[mm_postinstall] Error: Must be run as root to install '
              'rc.d script.')
        return

    pyver_nodot = f'{sys.version_info.major}{sys.version_info.minor}'

    template_path = Path(__file__).parent / 'settings/default/mathmakerd.in'
    if not template_path.exists():
        print(f'[mm_postinstall] Error: Template not found at {template_path}')
        return

    try:
        content = template_path.read_text()
        content = content.replace("%%PYVER_NODOT%%", pyver_nodot)
    except Exception as e:
        print(f'[mm_postinstall] Error while reading or preparing '
              f'template: {e}')
        return

    rc_target = Path('/usr/local/etc/rc.d/mathmakerd')

    try:
        rc_target.write_text(content)
        rc_target.chmod(0o755)
        print(f'[mm_postinstall] rc.d script successfully installed '
              f'at {rc_target}')
    except Exception as e:
        print(f'[mm_postinstall] Error writing to {rc_target}: {e}')
