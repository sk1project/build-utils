#
#   RPM builder
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

import os
import typing as tp


class RpmBuilder:
    """Represents rpm package build object. The object implements "setup.py bdist_rpm" command.
    Works after regular "setup.py build" command and constructs rpm package using build result of "setup.py sdist".
    """

    def __init__(
            self,
            name: str = '',
            version: str = '',
            release: str = '',
            arch: str = '',
            maintainer: str = '',
            summary: str = '',
            description: str = '',
            license_: str = '',
            url: str = '',
            depends: str = '',

            build_script: str = '',
            scripts: tp.Union[tp.List[str], None] = None,
            install_path: str = '',
            data_files: tp.Union[tp.List[str], None] = None,
    ) -> None:
        """Initialize and runs rpm package build

        :param name: (str) package names
        :param version: (str) package version
        :param release: (str) release marker
        :param arch: (str) system architecture (i686, x86_64), if not provided will be detected automatically
        :param maintainer: (str) package maintainer (John Smith <js@email.x>)
        :param summary: (str) short package description
        :param description: (str) long description as defined by Debian rules
        :param license_: (str) application license
        :param url: (str) project homepage
        :param depends: (str) list of dependencies

        :param build_script: (str) build script name (usually setup.py)
        :param scripts: (list|None) list of installed executable
        :param install_path: (str) installation path
        :param data_files: (list|None) list of data files and appropriate destination directories
        """

        data_files = data_files or []
        release = release or '0'

        self.name = name
        self.version = version
        self.release = release
        self.arch = arch
        self.maintainer = maintainer
        self.summary = summary
        self.description = description
        self.license = license_
        self.url = url
        self.depends = depends
        self.build_script = build_script
        self.scripts = ['%{_bindir}/' + os.path.basename(f) for f in scripts] \
            if scripts else ['%{_bindir}/' + self.name]
        self.install_path = install_path
        self.data_files = data_files

        self.current_path = os.path.abspath('.')
        self.rpmbuild_path = os.path.expanduser('~/rpmbuild')
        self.spec_path = os.path.join(self.rpmbuild_path, 'SPECS', 'python3-%s.spec' % self.name)
        self.dist_dir = os.path.join(self.current_path, 'dist')
        self.tarball = ''

        self._build()

    def _build(self):
        """Build pipeline"""
        self._clear_rpmbuild()
        self._create_rpmbuild()
        self._copy_sources(*self._find_tarball())
        self._write_spec()
        os.chdir(self.rpmbuild_path + '/SPECS')
        self._build_rpm()
        self._clear_rpmbuild()

    def _create_rpmbuild(self) -> None:
        """Creates rpm build directory structure"""
        for item in ('', 'BUILD', 'BUILDROOT', 'SOURCES', 'SPECS', 'RPMS', 'SRPMS'):
            os.mkdir(f'{self.rpmbuild_path}/{item}')

    def _find_tarball(self) -> tp.Tuple[str, str]:
        """Searches source code tarball in ./dist directory

        :return: (tuple) tarball path and tarball name
        """
        if not os.path.exists(self.dist_dir):
            raise IOError('There is no ./dist source folder!')
        file_items = os.listdir(self.dist_dir)
        for item in file_items:
            file_path = os.path.join(self.dist_dir, item)
            if os.path.isfile(file_path) and file_path.endswith('.tar.gz'):
                return file_path, item
        raise IOError('There is no source tarball in ./dist folder!')

    def _copy_sources(self, file_path, file_name) -> None:
        """Copies source code tarball"""
        self.tarball = self.rpmbuild_path + '/SOURCES/' + file_name
        os.system(f'cp {file_path} {self.tarball}')

    def _write_spec(self) -> None:
        """Creates RPM spec-file"""
        content = [
            f'Name: python3-{self.name}',
            f'Version: {self.version}',
            f'Release: {self.release}',
            f'Summary: {self.summary}',
            '',
            f'License: {self.license}',
            f'URL: {self.url}',
            f'Source: {self.tarball}',
            ''] + [f'Requires: {item}' for item in self.depends]
        content += [
            '',
            '%global __python %{__python3}',
            '',
            '%description', self.description,
            '',
            '%prep', f'%autosetup -n {self.name}-{self.version}',
            '',
            '%build', f'/usr/bin/python3 {self.build_script} build',
            '',
            '%install',
            'rm -rf $RPM_BUILD_ROOT', f'/usr/bin/python3 {self.build_script} install --root=$RPM_BUILD_ROOT',
            '',
            '%files', '\n'.join(self.scripts),
            self.install_path.replace('/usr/', '%{_usr}/'),
        ]
        for item in self.data_files:
            if item[0].startswith('/usr/share/'):
                path = item[0].replace('/usr/share/', '%{_datadir}/')
                for filename in item[1]:
                    filename = filename.split('/')[-1]
                    content.append(f'{path}/{filename}')
        content += ['', ]

        open(self.spec_path, 'w').write('\n'.join(content))

    def _build_rpm(self) -> None:
        """Runs 'rpmbuild -bb' command"""
        os.system(f'rpmbuild -bb {self.spec_path} --define "_topdir {self.rpmbuild_path}"')
        os.system(f'cp `find {self.rpmbuild_path} -name "*.rpm"` {self.dist_dir}/')

    def _clear_rpmbuild(self) -> None:
        """Clears build artifacts"""
        if os.path.exists(self.rpmbuild_path):
            os.system(f'rm -rf {self.rpmbuild_path}')
