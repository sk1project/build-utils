#
#   Localization utils
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
import typing as tp

from . import fsutils

LOG = logging.getLogger(__name__)


def build_pot(paths: tp.List[str], pot_file: str = 'messages.po', error_logs: bool = False) -> None:
    """Builds POT file collecting messages for translation across sources

    :param paths: (list) source code paths
    :param pot_file: (str) POT file path to collect messages to
    :param error_logs: (bool) flag to collect error logs
    """
    ret = 0
    files = []
    error_logs = 'warnings.log' if error_logs else '/dev/null'
    file_list = 'locale.in'
    for path in paths:
        files += fsutils.get_files_tree(path, 'py')
    with open(file_list, 'w') as fileptr:
        fileptr.write('\n'.join(files))
    ret += os.system(f'xgettext -f {file_list} -L Python -o {pot_file} 2>{error_logs}')
    ret += os.system(f'rm -f {file_list}')
    if not ret:
        LOG.info('POT file updated')


def build_locales(src_path: str, dest_path: str, textdomain: str) -> None:
    """Compile PO-files into MO-files.

    :param src_path: (str) path to PO-files directory
    :param dest_path: (str) path to LC_MESSAGES directory
    :param textdomain: (str) application text domain
    """
    LOG.info('Building locales')
    for item in fsutils.get_filenames(src_path, 'po'):
        lang = item.split('.')[0]
        po_file = os.path.join(src_path, item)
        mo_dir = os.path.join(dest_path, lang, 'LC_MESSAGES')
        mo_file = os.path.join(mo_dir, textdomain + '.mo')
        if not os.path.lexists(mo_dir):
            os.makedirs(mo_dir)
        LOG.info("%s ==> %s", po_file, mo_file)
        os.system('msgfmt -o %s %s' % (mo_file, po_file))
