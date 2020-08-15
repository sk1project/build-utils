# -*- coding: utf-8 -*-
#
#   Native modules build
#
# 	Copyright (C) 2015-2020 by Ihor E. Novikov
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

import os
import platform
from distutils.core import Extension

from . import build
from . import pkgconfig


def make_modules(src_path, include_path, lib_path=None):
    if lib_path is None:
        lib_path = []
    modules = []

    # --- Cairo module

    cairo_src = os.path.join(src_path, 'uc2', 'libcairo')
    files = build.make_source_list(cairo_src, ['_libcairo.c', ])

    include_dirs = []
    cairo_libs = ['cairo']

    if os.name == 'nt':
        include_dirs = build.make_source_list(
            include_path,
            ['cairo', 'pycairo'])
    elif platform.system() == 'Darwin':
        include_dirs = pkgconfig.get_pkg_includes(['pycairo', 'cairo'])
        cairo_libs = pkgconfig.get_pkg_libs(['pycairo', 'cairo'])
    elif os.name == 'posix':
        include_dirs = pkgconfig.get_pkg_includes(['pycairo', ])
        cairo_libs = pkgconfig.get_pkg_libs(['pycairo', ])

    cairo_module = Extension(
        'uc2.libcairo._libcairo',
        define_macros=[('MAJOR_VERSION', '2'), ('MINOR_VERSION', '0')],
        sources=files, include_dirs=include_dirs,
        library_dirs=lib_path,
        libraries=cairo_libs)
    modules.append(cairo_module)

    # --- LCMS2 module

    lcms2_files = ['_lcms2.c', ]
    lcms2_libraries = []
    extra_compile_args = []

    if os.name == 'nt':
        if platform.architecture()[0] == '32bit':
            lcms2_libraries = ['lcms2_static']
        else:
            lcms2_libraries = ['liblcms2-2']
    elif os.name == 'posix':
        lcms2_libraries = pkgconfig.get_pkg_libs(['lcms2', ])
        extra_compile_args = ["-Wall"]

    lcms2_src = os.path.join(src_path, 'uc2', 'cms', 'lcms2')
    files = build.make_source_list(lcms2_src, lcms2_files)
    include_dirs = [include_path, ]
    lcms2_module = Extension(
        'uc2.cms._lcms2',
        define_macros=[('MAJOR_VERSION', '2'), ('MINOR_VERSION', '0')],
        sources=files, include_dirs=include_dirs,
        library_dirs=lib_path,
        libraries=lcms2_libraries,
        extra_compile_args=extra_compile_args)
    modules.append(lcms2_module)

    # --- Pango module

    # pango_src = os.path.join(src_path, 'uc2', 'libpango')
    # files = build.make_source_list(pango_src, ['_libpango.c', ])
    # pango_libs = [
    #     'pango-1.0', 'pangocairo-1.0', 'cairo', 'glib-2.0', 'gobject-2.0']
    #
    # if os.name == 'nt':
    #     include_dirs = build.make_source_list(
    #         include_path, ['cairo', 'pycairo', 'pango-1.0', 'glib-2.0'])
    # elif platform.system() == 'Darwin':
    #     include_dirs = pkgconfig.get_pkg_includes(['pangocairo', 'pango',
    #                                                'pycairo', 'cairo'])
    #     pango_libs = pkgconfig.get_pkg_libs(['pangocairo', 'pango', 'pycairo',
    #                                          'cairo'])
    # elif os.name == 'posix':
    #     include_dirs = pkgconfig.get_pkg_includes(['pangocairo', 'pycairo'])
    #     pango_libs = pkgconfig.get_pkg_libs(['pangocairo', ])
    #
    # pango_module = Extension(
    #     'uc2.libpango._libpango',
    #     define_macros=[('MAJOR_VERSION', '1'), ('MINOR_VERSION', '0')],
    #     sources=files, include_dirs=include_dirs,
    #     library_dirs=lib_path,
    #     libraries=pango_libs)
    # modules.append(pango_module)

    # --- ImageMagick module

    compile_args = []
    libimg_libraries = ['CORE_RL_wand_', 'CORE_RL_magick_']
    im_ver = '6'

    if os.name == 'nt':
        include_dirs = [include_path, include_path + '/ImageMagick']
    elif os.name == 'posix':
        im_ver = pkgconfig.get_pkg_version('MagickWand')[0]
        libimg_libraries = pkgconfig.get_pkg_libs(['MagickWand', ])
        include_dirs = pkgconfig.get_pkg_includes(['MagickWand', ])
        compile_args = pkgconfig.get_pkg_cflags(['MagickWand', ])

    libimg_src = os.path.join(src_path, 'uc2', 'libimg')
    files = build.make_source_list(libimg_src, ['_libimg%s.c' % im_ver, ])
    libimg_module = Extension(
        'uc2.libimg._libimg',
        define_macros=[('MAJOR_VERSION', '1'), ('MINOR_VERSION', '0')],
        sources=files, include_dirs=include_dirs,
        library_dirs=lib_path,
        libraries=libimg_libraries,
        extra_compile_args=compile_args)
    modules.append(libimg_module)

    return modules


def make_cp2_modules(src_path, include_path, lib_path=None):
    if lib_path is None:
        lib_path = []
    modules = []

    # --- LCMS2 module

    lcms2_files = ['_lcms2.c', ]
    lcms2_libraries = []
    extra_compile_args = []

    if os.name == 'nt':
        if platform.architecture()[0] == '32bit':
            lcms2_libraries = ['lcms2_static']
        else:
            lcms2_libraries = ['liblcms2-2']
    elif os.name == 'posix':
        lcms2_libraries = pkgconfig.get_pkg_libs(['lcms2', ])
        extra_compile_args = ["-Wall"]

    lcms2_src = os.path.join(src_path, 'uc2', 'cms', 'lcms2')
    files = build.make_source_list(lcms2_src, lcms2_files)
    include_dirs = [include_path, ]
    lcms2_module = Extension(
        'uc2.cms._lcms2',
        define_macros=[('MAJOR_VERSION', '1'), ('MINOR_VERSION', '0')],
        sources=files, include_dirs=include_dirs,
        library_dirs=lib_path,
        libraries=lcms2_libraries,
        extra_compile_args=extra_compile_args)
    modules.append(lcms2_module)

    return modules
