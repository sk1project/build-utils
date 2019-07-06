# -*- coding: utf-8 -*-
#
#   macOS dmg build
#
# 	Copyright (C) 2019 by Igor E. Novikov
#
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
# 	along with this program.  If not, see <https://www.gnu.org/licenses/>.

#   Requires hfsprogs:
#   sudo apt-get install hfsprogs

import math
import os
import shutil

from . import fsutils


def dmg_build(targets=None,
              dmg_filename='test.dmg',
              volume_name='Install',
              dist_dir='.'):

    if not targets:
        raise Exception('DMG payload is not provided!')

    sz = 0
    for item in targets:
        sz += fsutils.getsize(item)
    size = int(math.ceil(sz/10**6)) or 1

    # File allocation
    os.system('dd if=/dev/zero of=/tmp/%s bs=1M '
              'count=%d status=progress' % (dmg_filename, size))
    # Formatting for HFS+
    os.system('mkfs.hfsplus -v "%s" /tmp/%s' % (volume_name, dmg_filename))

    # Mounting
    os.system('mkdir -pv /mnt/tmp_dmg && '
              'mount -o loop /tmp/%s /mnt/tmp_dmg' % dmg_filename)
    # Copying
    for item in targets:
        if os.path.isfile(item):
            shutil.copy(item, '/mnt/tmp_dmg')
        else:
            dst = os.path.join('/mnt/tmp_dmg', os.path.basename(item))
            shutil.copytree(item, dst)

    # Unmounting
    os.system('umount /mnt/tmp_dmg && rm -rf /mnt/tmp_dmg')
    dst = os.path.join(dist_dir, dmg_filename)
    shutil.move('/tmp/%s' % dmg_filename, dst)
