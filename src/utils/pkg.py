# -*- coding: utf-8 -*-
#
#   macOS pkg build
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

#   Requires xar and bomutils:
# sudo apt-get install libxml2-dev libssl-dev
# tar -zxvf ./bomutils-0.2.tar.gz && cd bomutils-0.2&& make && make install
# tar -zxvf ./xar-1.5.2.tar.gz && cd ./xar-1.5.2 && \
# ./configure && make && make install

import os
import shutil

from . import fsutils
from .xmlutils import XmlElement


# KW_SAMPLE = {
#     'src_dir': '',  # path to distribution folder
#     'build_dir': './build_dir',  # path for build
#     'install_dir': '/opt/appName',  # where to install app
#     'identifier': 'com.ProFarms.SimCow',  # domain.Publisher.AppName
#     'preinstall': None, # path to preinstall script
#     'postinstall': None, # path to postinstall script
# }


class PkgBuilder:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.payload_sz = (0, 0)
        build_dir = fsutils.normalize_path(self.kwargs['build_dir'])
        flat_dir = os.path.join(build_dir, 'flat')
        self.scripts_dir = os.path.join(build_dir, 'scripts')
        proj_dir = os.path.join(flat_dir, 'Resources', 'en.lproj')
        self.pkg_dir = os.path.join(flat_dir, 'base.pkg')
        self.root_dir = os.path.join(build_dir, 'root')

        for item in (proj_dir, self.pkg_dir):
            os.makedirs(item)
        self.create_payload()

    def create_payload(self):
        src = fsutils.normalize_path(self.kwargs['src_dir'])
        shutil.copytree(src, self.root_dir)
        os.system('( cd %s && find . | '
                  'cpio -o --format odc --owner 0:80 | '
                  'gzip -c ) > %s/Payload' % (self.root_dir, self.pkg_dir))
        self.payload_sz = fsutils.getsize(self.root_dir, True)
        os.system('rm -rf %s' % self.root_dir)

    def add_scripts(self):
        scripts = None
        os.makedirs(self.scripts_dir)
        if 'preinstall' in self.kwargs:
            scripts = XmlElement('scripts')

            scr = self.kwargs['preinstall']
            name = os.path.basename(scr)
            path = os.path.join(self.scripts_dir, name)
            shutil.copy(fsutils.normalize_path(scr), path)
            os.system('chmod +x %s' % path)
            scripts.add(XmlElement('preinstall', {'file': './%s' % name}))

        if 'postinstall' in self.kwargs:
            scripts = XmlElement('scripts') if not scripts else scripts

            scr = self.kwargs['postinstall']
            name = os.path.basename(scr)
            path = os.path.join(self.scripts_dir, name)
            shutil.copy(fsutils.normalize_path(scr), path)
            os.system('chmod +x %s' % path)
            scripts.add(XmlElement('postinstall', {'file': './%s' % name}))

        if scripts:
            os.system('( cd %s && find . | '
                      'cpio -o --format odc --owner 0:80 | gzip -c ) > '
                      '%s/Scripts' % (self.scripts_dir, self.pkg_dir))

        os.system('rm -rf %s' % self.scripts_dir)
        return scripts

    def add_bundle(self):
        bundle = XmlElement('bundle-version')
        bundle.add(XmlElement('bundle', {
            'id': self.kwargs['identifier'],
            'CFBundleIdentifier': self.kwargs['identifier'],
            'path': self.kwargs['install_dir'],
            'CFBundleVersion': '1.3.0',
        }))

        return bundle

    def create_pkg_info(self):
        pkg_info = XmlElement('pkg-info', {
            'format-version': '2',
            'identifier': '%s.base.pkg' % self.kwargs['identifier'],
            'version': '1.3.0',
            'install-location': '/',
            'auth': 'root',
        })
        pkg_info.add(XmlElement('payload', {
            'installKBytes': '%d' % (self.payload_sz[0] // 1024),
            'numberOfFiles': '%d' % self.payload_sz[1],
        }))
        pkg_info.add(self.add_scripts())
        pkg_info.add(self.add_bundle())

        pkg_info_file = os.path.join(self.pkg_dir, 'PackageInfo')
        with open(pkg_info_file, 'wb') as fileptr:
            pkg_info.write_xml(fileptr)
