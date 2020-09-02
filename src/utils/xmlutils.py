#
# 	Copyright (C) 2019-2020 by Ihor E. Novikov
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

INDENT = 4
WRAP = 3

XmlElementType = tp.TypeVar('XmlElementType')


class XmlElement:
    parent: tp.Optional[XmlElementType] = None
    childs: tp.Optional[tp.List[XmlElementType]] = None
    tag: str
    attrs: tp.Dict[str, str]
    comment: str = ''
    content: str = ''
    nl: bool = False

    def __init__(self, tag: str, kwargs: tp.Optional[tp.Dict[str, str]] = None, content: str = '') -> None:
        """Initializes XML element object

        :param tag: (str) element tag name
        :param kwargs: (dict) element attributes
        :param content: element tag content
        """
        self.tag = tag
        self.childs = []
        self.content = content
        self.attrs = {key: value for key, value in kwargs.items()} if kwargs else {}

    def destroy(self) -> None:
        """Destroys the object and it's children"""
        for child in self.childs:
            child.destroy()
        for item in self.__dict__.keys():
            self.__dict__[item] = None

    def add(self, child: tp.Optional[XmlElementType]) -> None:
        """Adds child object

        :param child: (XmlElement) element object
        """
        if child:
            self.childs.append(child)
            child.parent = self

    def set(self, kwargs: tp.Dict[str, str]) -> None:
        """Updates element attributes

        :param kwargs: (dict) element attributes
        """
        self.attrs.update(kwargs)

    def get(self, key: str) -> str:
        """Returns attribute value

        :param key: (str) attribute name
        :return: (str) attribute value
        """
        return self.attrs.get(key)

    def pop(self, key: str) -> None:
        """Removes attribute

        :param key: (str) attribute name
        """
        if key in self.attrs:
            self.attrs.pop(key)

    def write_xml(self, fp: tp.IO, indent: int = 0) -> None:
        """Writes element into file-like object

        :param fp: (tp.IO) file-like object
        :param indent: (int) indent size
        """
        if self.nl:
            fp.write('\n')
        tab = indent * ' '
        if self.comment:
            fp.write(f'{tab}<!-- {self.comment} -->\n')
        fp.write(f'{tab}<{self.tag}')
        prefix = f'\n{tab}  ' if len(self.attrs) > WRAP else ' '
        for key, value in self.attrs.items():
            fp.write(f'{prefix}{key}="{value}"')
        if self.childs:
            fp.write('>\n')
            for child in self.childs:
                child.write_xml(fp, indent + INDENT)
            fp.write(f'{tab}</{self.tag}>\n')
        elif self.content:
            fp.write('>')
            fp.write(self.content)
            fp.write(f'</{self.tag}>\n')
        else:
            fp.write(' />\n')
