#
#   DEB builder
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

import logging
import os
import platform
import sys
import typing as tp

LOG = logging.getLogger(__name__)

RM_CODE = 21
MK_CODE = 22
CP_CODE = 23

logging.addLevelName(RM_CODE, 'REMOVING')
logging.addLevelName(MK_CODE, 'CREATING')
logging.addLevelName(CP_CODE, 'COPYING')


def get_size(start_path: str = '.') -> int:
    """Calcs recursively total file size in directory

    :param start_path: (str) target directory
    :return: (int) total file size
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def _make_dir(path: str) -> None:
    """Creates directory if not exists it

    :param path: (str) directory path
    """
    if not os.path.exists(path):
        LOG.log(MK_CODE, f'{path} directory.')
        # noinspection PyBroadException
        try:
            os.makedirs(path)
        except Exception:
            raise IOError(f'Error while creating {path} directory.')


def copy_scripts(path: str, scripts: tp.List[str]) -> None:
    """Copies scripts into destination directory and makes them executable.
    If directory not exists creates it.

    :param path: (str) destination directory
    :param scripts: (list) list of scripts
    """
    if not scripts:
        return
    _make_dir(path)
    for item in scripts:
        LOG.log(CP_CODE, f'{item} -> {path}')
        if os.system(f'cp {item} {path}'):
            raise IOError(f'Cannot copying {item} -> {path}')
        filename = os.path.basename(item)
        filepath = os.path.join(path, filename)
        if os.path.isfile(filepath):
            LOG.log(MK_CODE, f'{filepath} as executable')
            if os.system(f'chmod +x {filepath}'):
                raise IOError(f'Cannot set executable flag for {filepath}')


def copy_files(path: str, files: tp.List[str]):
    """Copies files into destination directory.
    If directory not exists creates it.

    :param path: (str) destination directory
    :param files: (list) list of files
    """
    if files and not os.path.isdir(path):
        _make_dir(path)
    if not files:
        return
    space = ' ' * 10
    for item in files:
        msg = f'{item} -> {path}'
        if len(msg) > 80:
            msg = f'{item} -> \n{space}{path}'
        LOG.log(CP_CODE, msg)
        if os.system(f'cp {item} {path}'):
            raise IOError(f'Cannot copying {item} -> {path}')


class DebBuilder:
    """Represents deb package build object.
    The object implements "setup.py bdist_deb" command.
    Works after regular "setup.py build" command and
    constructs deb package using build result in build/ directory.
    """
    name: str
    package_dirs: tp.Dict[str, str]
    package_data: tp.Dict[str, tp.List[str]]
    scripts: tp.List[str]
    data_files: tp.List[tp.Tuple[str, tp.List[str]]]
    deb_scripts: tp.List[str]

    package: str
    version: str
    arch: str
    maintainer: str
    installed_size: str
    depends: str
    section: str = 'python'
    priority: str = 'optional'
    homepage: str
    description: str
    long_description: str

    package_name: str
    py_version: str
    machine: str
    build_dir: str = 'build/deb-root'
    deb_dir: str = 'build/deb-root/DEBIAN'
    src: str
    dst: str
    bin_dir: str

    def __init__(
            self,
            name: str = '',
            version: str = '',
            arch: str = '',
            maintainer: str = '',
            depends: str = '',
            section: str = '',
            priority: str = '',
            homepage: str = '',
            description: str = '',
            long_description: str = '',
            package_dirs: tp.Optional[tp.Dict[str, str]] = None,
            package_data: tp.Optional[tp.Dict[str, tp.List[str]]] = None,
            scripts: tp.List[str] = None,
            data_files: tp.Optional[tp.List[tp.Tuple[str, tp.List[str]]]] = None,
            deb_scripts: tp.Optional[tp.List[str]] = None,
            dst: str = '') -> None:
        """Initializes and runs DEB package build

        :param name: (str) package name
        :param version: (str) package version
        :param arch: (str) system architecture (amd64, i386, all), if not provided will be detected automatically
        :param maintainer: (str) package maintainer (John Smith <js@email.x>)
        :param depends: (str) comma separated string of dependencies
        :param section: (str) package section (default 'python')
        :param priority: (str) package priority for users (default 'optional')
        :param homepage: (str) project homepage
        :param description: (str) short package description
        :param long_description: (str) long description as defined by Debian rules
        :param package_dirs: (dict) dict of root python packages
        :param package_data: (dict) dict of non python files and appropriate destination directories
        :param scripts: (list) list of executable scripts
        :param data_files: (list) list of data files and appropriate destination directories
        :param deb_scripts: (list) list of Debian package scripts
        :param dst: (str) installation path
        """
        self.name = name
        self.version = version
        self.arch = arch
        self.maintainer = maintainer
        self.depends = depends
        self.section = section or self.section
        self.priority = priority or self.priority
        self.homepage = homepage
        self.description = description
        self.long_description = long_description

        self.package_dirs = package_dirs or {}
        self.package_data = package_data or {}
        self.scripts = scripts or []
        self.data_files = data_files or []
        self.deb_scripts = deb_scripts or []
        self.dst = dst

        self.package = f'python3-{self.name}'
        self.py_version = '.'.join(sys.version.split()[0].split('.')[:2])

        if not self.arch:
            arch = platform.architecture()[0]
            self.arch = 'amd64' if arch == '64bit' else 'i386'

        self.machine = platform.machine()

        self.src = f'build/lib.linux-{self.machine}-{self.py_version}'

        if not self.dst:
            self.dst = f'{self.build_dir}/usr/lib/python{self.py_version}/dist-packages'
        else:
            self.dst = self.build_dir + self.dst
        self.bin_dir = f'{self.build_dir}/usr/bin'

        self.package_name = f'python3-{self.name}-{self.version}_{self.arch}.deb'
        self.build()

    def clear_build(self) -> None:
        """Clears build artifacts
        """
        if os.path.lexists(self.build_dir):
            LOG.log(RM_CODE, f'{self.build_dir} directory.')
            if os.system(f'rm -rf {self.build_dir}'):
                raise IOError(f'Error while removing {self.build_dir} directory.')
        if os.path.lexists('dist'):
            LOG.log(RM_CODE, 'Cleaning dist/ directory.')
            if os.system('rm -rf dist/*.deb'):
                raise IOError('Error while cleaning dist/ directory.')
        else:
            _make_dir('dist')

    def write_control(self) -> None:
        """Writes Debian control file
        """
        _make_dir(self.deb_dir)
        control_list = [
            ['Package', self.package],
            ['Version', self.version],
            ['Architecture', self.arch],
            ['Maintainer', self.maintainer],
            ['Installed-Size', self.installed_size],
            ['Depends', self.depends],
            ['Section', self.section],
            ['Priority', self.priority],
            ['Homepage', self.homepage],
            ['Description', self.description],
            ['', self.long_description],
        ]
        path = os.path.join(self.deb_dir, 'control')
        LOG.log(MK_CODE, 'Writing Debian control file.')
        # noinspection PyBroadException
        try:
            control = open(path, 'w')
            for item in control_list:
                name, val = item
                if val:
                    if name:
                        control.write(f'{name}: {val}\n')
                    else:
                        control.write(f'{val}\n')
            control.close()
        except Exception:
            raise IOError('Error while writing Debian control file.')

    def copy_build(self) -> None:
        """Copies project build
        """
        for item in os.listdir(self.src):
            path = os.path.join(self.src, item)
            if os.path.isdir(path):
                LOG.log(CP_CODE, f'{path} -> {self.dst}')
                if os.system(f'cp -R {path} {self.dst}'):
                    raise IOError(f'Error while copying {path} -> {self.dst}')
            elif os.path.isfile(path):
                LOG.log(CP_CODE, f'{path} -> {self.dst}')
                if os.system(f'cp {path} {self.dst}'):
                    raise IOError(f'Error while copying {path} -> {self.dst}')

    def copy_data_files(self) -> None:
        """Copies extra files
        """
        for item in self.data_files:
            path, files = item
            copy_files(self.build_dir + path, files)

    def copy_package_data_files(self) -> None:
        """Copies package data files
        """
        files = []
        pkgs = self.package_data.keys()
        for pkg in pkgs:
            items = self.package_data[pkg]
            for item in items:
                path = os.path.join(self.package_dirs[pkg], item)
                if os.path.basename(path) == '*.*':
                    flist = []
                    folder = os.path.join(self.dst, os.path.dirname(item))
                    fldir = os.path.dirname(path)
                    fls = os.listdir(fldir)
                    for fl in fls:
                        flpath = os.path.join(fldir, fl)
                        if os.path.isfile(flpath):
                            flist.append(flpath)
                    files.append([folder, flist])
                else:
                    if os.path.isfile(path):
                        folder = os.path.join(self.dst, os.path.dirname(item))
                        files.append([folder, [path, ]])
        for item in files:
            path, files = item
            copy_files(path, files)

    def make_package(self) -> None:
        """Makes deb package using dpkg
        """
        os.system(f'chmod -R 755 {self.build_dir}')
        LOG.log(MK_CODE, f'{self.package_name} package.')
        if os.system(f'sudo dpkg --build {self.build_dir}/ dist/{self.package_name}'):
            raise IOError(f'Cannot create package {self.package_name}')

    def build(self) -> None:
        """Main build routine
        """
        line = '=' * 30
        LOG.info(line)
        LOG.info('DEB PACKAGE BUILD')
        LOG.info(line)
        try:
            if not os.path.isdir('build'):
                raise IOError('There is no project build! Run "setup.py build" and try again.')
            self.clear_build()
            _make_dir(self.dst)
            self.copy_build()
            copy_scripts(self.bin_dir, self.scripts)
            copy_scripts(self.deb_dir, self.deb_scripts)
            self.copy_data_files()
            self.installed_size = str(int(get_size(self.build_dir) / 1024))
            self.write_control()
            self.make_package()
        except IOError as e:
            LOG.error(e)
            LOG.warning(line)
            LOG.warning('BUILD FAILED!')
        LOG.info(line)
        LOG.info('BUILD SUCCESSFUL!')
        LOG.info(line)
