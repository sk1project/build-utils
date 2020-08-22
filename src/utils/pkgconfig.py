#
#   pkgconfig utils
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

import typing as tp
import subprocess


def get_pkg_version(pkg_name: str) -> str:
    """Returns version of requested package

    :param pkg_name: (str) name of requested package
    :return: (str) version of requested package
    """
    process = subprocess.Popen(["pkg-config", "--modversion", pkg_name], stdout=subprocess.PIPE)
    output, err = process.communicate()
    return output.decode().strip()


def get_pkg_includes(pkg_names: tp.List[str]) -> tp.List[str]:
    """Returns includes for requested package

    :param pkg_names: (list) package names
    :return: (list) include list
    """
    includes = []
    for item in pkg_names:
        process = subprocess.Popen(["pkg-config", "--cflags-only-I", item], stdout=subprocess.PIPE)
        output, err = process.communicate()
        names = output.decode().replace('-I', '').strip().split(' ')
        for name in names:
            if name not in includes:
                includes.append(name)
    return includes


def get_pkg_libs(pkg_names: tp.List[str]) -> tp.List[str]:
    """Returns libraries for requested package

    :param pkg_names: (list) package names
    :return: (list) libs list
    """
    libs = []
    for item in pkg_names:
        process = subprocess.Popen(["pkg-config", "--libs-only-l", item], stdout=subprocess.PIPE)
        output, err = process.communicate()
        names = output.decode().replace('-l', '').strip().split(' ')
        for name in names:
            if name not in libs:
                libs.append(name)
    return libs


def get_pkg_cflags(pkg_names: tp.List[str]) -> tp.List[str]:
    """Returns compiler flags for requested package

    :param pkg_names: (list) package names
    :return: (list) cflags list
    """
    flags = []
    for item in pkg_names:
        process = subprocess.Popen(["pkg-config", "--cflags-only-other", item], stdout=subprocess.PIPE)
        output, err = process.communicate()
        names = output.decode().strip().split(' ')
        for name in names:
            if name not in flags:
                flags.append(name)
    return flags
