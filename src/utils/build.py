#
#   Build utils
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

from distutils.core import Extension
import logging
import os
import platform
import shutil
import sys
import typing as tp

from . import fsutils

INIT_FILE = '__init__.py'
LOG = logging.getLogger(__name__)


def get_resources(pkg_path: str, path: str) -> tp.List[str]:
    """Scans recursively python package resources

    :param pkg_path: (str) path to python package
    :param path: (str) path to package resource directory
    :return: (list) list of resource directories with wildcard
    """
    path = os.path.normpath(path)
    pkg_path = os.path.normpath(pkg_path)
    size = len(pkg_path) + 1
    dirs = fsutils.get_dirs_tree(path)
    dirs.append(path)
    res_dirs = []
    for item in dirs:
        res_dirs.append(os.path.join(item[size:], '*.*'))
    return res_dirs


def clear_build() -> None:
    """Clears build result.
    """
    if os.path.exists('build'):
        shutil.rmtree('build', ignore_errors=True)


def clear_msw_build() -> None:
    """Clears build result on MS Windows.
    """
    if os.path.exists('build'):
        shutil.rmtree('build', ignore_errors=True)


def make_source_list(path: str, file_list: tp.Optional[tp.List[str]] = None):
    """Returns list of paths for provided file list.

    :param path: (str) the directory path
    :param file_list: (list) file names int the directory
    :return: (list) file paths
    """
    return [os.path.join(path, item) for item in file_list or []]


def is_package(path):
    """Checks is provided directory a python package.

    :param path: (str) directory path
    :return: (bool) is directory a python package
    """
    return os.path.isdir(path) and '-' not in os.path.basename(path) and \
        os.path.isfile(os.path.join(path, INIT_FILE))


def get_packages(path: str) -> tp.List[str]:
    """Collects recursively python packages.

    :param path: (str) root package path
    :return: (list) recursive list of subpackages
    """
    packages = []
    if os.path.isdir(path):
        try:
            for item in os.listdir(path):
                if item.startswith('.'):
                    continue
                folder = os.path.join(path, item)
                if is_package(folder):
                    packages.append(folder)
                    packages += get_packages(folder)
        except os.error:
            pass
    return sorted(packages)


def get_package_dirs(path: str = 'src', excludes: tp.Optional[tp.List[str]] = None) -> tp.Dict[str, str]:
    """Collects root packages.

    :param path: (str) source root path
    :param excludes: (list) excluded names
    :return: (dict) package name/path dict
    """
    excludes = excludes or []
    dirs = {}
    if os.path.isdir(path):
        try:
            for item in os.listdir(path):
                if item in excludes or item.startswith('.'):
                    continue
                folder = os.path.join(path, item)
                if is_package(folder):
                    dirs[item] = folder
        except os.error:
            pass
    return dirs


def get_source_structure(path: str = 'src', excludes: tp.Optional[tp.List[None]] = None) -> tp.List[str]:
    """Returns recursive list of python packages.

    :param path: (str) root source code directory, default 'src'
    :param excludes: (list|None) list of excluded prefixes
    :return: (list) list of python packages into source code directory
    """
    excludes = excludes or []
    packages = []
    for item in get_packages(path):
        res = item.replace('\\', '.').replace('/', '.').split('src.')[1]
        if all([not res.startswith(exclude) for exclude in excludes]):
            packages.append(res)
    return packages


def compile_sources(path: str = 'build') -> None:
    """Compiles recursively python sources in provided directory.

    :param path: (str) root source code directory, default 'build'
    """
    import compileall
    compileall.compile_dir(path, quiet=1)


def _find_extension(path: str, prefix: str, suffix: str) -> tp.Optional[str]:
    """Searches extension in directory by prefix and suffix

    :param path: (str) extesion directory
    :param prefix: (str) extension prefix
    :param suffix: (str) extension suffix
    :return: (str|None) extension file name or None
    """
    for item in os.listdir(path):
        if item.startswith(prefix) and item.endswith(suffix):
            return item


def copy_modules(modules: tp.List[Extension], src_root: str = 'src') -> None:
    """Copies native modules into source code tree.
    The routine implements 'build_update' command
    functionality and executed after 'setup.py build' command.

    :param modules: (list) distutils Extensions
    :param src_root: (str) path to root source code directory
    """
    version = '.'.join(sys.version.split()[0].split('.')[:2])
    machine = platform.machine()
    ext = '.so'
    prefix = f'build/lib.linux-{machine}-{version}'
    marker = ''

    if os.name == 'nt' and platform.architecture()[0] == '32bit':
        prefix = f'build/lib.win32-{version}'
        ext = '.pyd'
        marker = 'win32'
    elif os.name == 'nt' and platform.architecture()[0] == '64bit':
        prefix = f'build/lib.win-amd64-{version}'
        ext = '.pyd'
        marker = 'win64'

    for item in modules:
        path = os.path.join(*item.name.split('.'))
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)
        filename = _find_extension(os.path.join(prefix, dirname), basename, ext)
        if not filename:
            continue
        path = os.path.join(dirname, filename)

        src = os.path.join(prefix, path)
        dst = os.path.join(src_root, path)
        if os.path.exists(dst):
            os.remove(dst)
        shutil.copy(src, dst)
        if os.name == 'nt':
            dst2 = os.path.join(f'{marker}-devres', 'pyd', os.path.basename(src))
            if os.path.exists(dst2):
                os.remove(dst2)
            shutil.copy(src, dst)
        LOG.info(f'>>>Module {path} has been copied to src/ directory')
