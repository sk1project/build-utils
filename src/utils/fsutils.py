#
#   Filesystem utils
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

import glob
import os
import shutil
import typing as tp


def get_filenames(path: str = '.', ext: str = '*') -> tp.List[str]:
    """Returns filename list for provided path filtering by extension

    :param path: (str) working directory, default - current directory
    :param ext: (str) select by the extension (e.g. 'svg', 'ai' etc.), default - any extension
    :return: (list) found file names list
    """
    result = []
    if os.path.isdir(path):
        try:
            for name in sorted(os.listdir(path)):
                if os.path.isfile(os.path.join(path, name)):
                    if ext == '*' or name.endswith(f'.{ext}'):
                        result.append(name)
        except os.error:
            pass
    return result


def get_filepaths(path: str = '.', ext: str = '*') -> tp.List[str]:
    """Returns file paths list for provided path filtering by extension

    :param path: (str) working directory, default - current directory
    :param ext: (str) select by the extension (e.g. 'svg', 'ai' etc.), default - any extension
    :return: (list) found file paths list
    """
    file_items = sorted(glob.glob(os.path.join(path, f'*.{ext}')))
    return [file_item for file_item in file_items if os.path.isfile(file_item)]


def get_dirpaths(path: str = '.', skip_hidden: bool = True) -> tp.List[str]:
    """Returns directory paths list for provided path

    :param path: (str) working directory, default - current directory
    :param skip_hidden: (bool) skip hidden directories, e.g. '.svn'
    :return: (list) found directory paths list
    """
    result = []
    if os.path.isdir(path):
        try:
            for name in sorted(os.listdir(path)):
                dirpath = os.path.join(path, name)
                skip = name.startswith('.') and skip_hidden
                if not skip and os.path.isdir(dirpath):
                    result.append(dirpath)
        except os.error:
            pass
    return result


def get_dirs_tree(path: str = '.') -> tp.List[str]:
    """Returns recursive directory paths list for provided path

    :param path: (str) working directory, default - current directory
    :return: (list) found directory paths list
    """
    tree = get_dirpaths(path)
    res = [] + tree
    for node in tree:
        res += get_dirs_tree(node)
    return sorted(res)


def get_files_tree(path: str = '.', ext: str = '*') -> tp.List[str]:
    """Returns recursive file path list for provided path

    :param path: (str) working directory, default - current directory
    :param ext: (str) select by the extension (e.g. 'svg', 'ai' etc.), default - any extension
    :return: (list) found file paths list
    """
    tree = []
    for dir_item in [path, ] + get_dirs_tree(path):
        tree += get_filepaths(dir_item, ext)
    return sorted(tree)


def normalize_path(path: str = '.') -> str:
    """Returns absolute path

    :param path: (str) path representation
    :return: (str) normalized absolute path
    """
    return os.path.abspath(os.path.expanduser(path))


def getsize(path='.', count=False) -> tp.Union[int, tp.Tuple[int, int]]:
    """Returns size of file or recursive size of directory

    :param path: (str) working directory, default - current directory
    :param count: (bool) return number of files
    :return: (int|tuple) total files size or tuple of files size and number of files
    """
    sizes = [os.path.getsize(path)] if os.path.isfile(path) \
        else [os.path.getsize(f) for f in get_files_tree(path)]
    return (sum(sizes), len(sizes)) if count else sum(sizes)


def rmtree(path: str) -> None:
    """Recursively delete a directory tree

    :param path: (str) target path
    """
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.islink(path):
        os.unlink(path)
