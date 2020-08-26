#
#   BuildBox staff
#
# 	Copyright (C) 2018-2020 by Ihor E. Novikov
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

import datetime
import os
import typing as tp

from .dist import SYSFACTS
from . import fsutils


TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d")


def shell(cmd: str, times: int = 1) -> int:
    """Retries execute command

    :param cmd: (str) shell command
    :param times: (int) times to retry
    :return: (int) execution exit status
    """
    for _i in range(times):
        if not os.system(cmd):
            return 0
    return 1


def clear_files(folder: str, ext: tp.Union[tp.List[str], str, None] = None) -> None:
    """Removes files recursively by extension

    :param folder: (str) working folder
    :param ext: (str|list) target extension(s)
    """
    ext = 'py' if ext is None else ext
    exts = [ext] if not isinstance(ext, list) else ext
    for ext in exts:
        for path in fsutils.get_files_tree(folder, ext):
            if os.path.exists(path) and path.endswith(ext):
                os.remove(path)


def is_path(pth: str) -> bool:
    """Checks path existence

    :param pth: (str) path string
    :return: (bool) is path exists
    """
    return os.path.exists(pth)


def get_marker(use_timestamp: bool = True) -> str:
    """Returns OS specific package marker

    :param use_timestamp: (bool) add timestamp flag
    :return: (str) package marker
    """
    ver = SYSFACTS.version
    mrk = SYSFACTS.marker
    if SYSFACTS.is_deb:
        if SYSFACTS.is_debian:
            ver = ver.split('.')[0]
        mrk = '_%s_%s_' % (SYSFACTS.marker, ver)
        if use_timestamp:
            mrk = '_%s%s' % (TIMESTAMP, mrk)
    elif SYSFACTS.is_rpm:
        if not SYSFACTS.is_opensuse and not ver.startswith('42'):
            ver = ver.split('.')[0]
        mrk = SYSFACTS.marker + ver
        if use_timestamp:
            mrk = '%s.%s' % (TIMESTAMP, mrk)
    return mrk


def get_package_name(pth: str) -> str:
    """Finds build result and returns the package name

    :param pth: (str) working directory
    :return: (str) package name
    """
    files = fsutils.get_filenames(pth)
    if SYSFACTS.is_deb:
        if len(files) == 1:
            if files[0].endswith('.deb') or files[0].endswith('.tar.gz'):
                return files[0]
    elif SYSFACTS.is_rpm:
        for fl in files:
            if fl.endswith('.rpm') and not fl.endswith('src.rpm') and 'debug' not in fl:
                return fl
    elif SYSFACTS.is_msw:
        if len(files) == 1:
            if files[0].endswith('.zip') or files[0].endswith('.msi'):
                return files[0]
    raise Exception('Build failed! There is no build result.')
