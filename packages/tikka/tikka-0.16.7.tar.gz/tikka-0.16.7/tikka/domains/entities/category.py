# Copyright 2021 Vincent Texier <vit@free.fr>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class Category:
    id: UUID
    name: str
    expanded: bool = True
    parent_id: Optional[UUID] = None
    _balance: int = 0

    @property
    def balance(self):
        """
        Return hidden field _balance

        :return:
        """
        return self._balance

    @balance.setter
    def balance(self, value):
        """
        Set value of hidden _balance

        :param value: Balance value
        :return:
        """
        self._balance = value

    def __eq__(self, other):
        """
        Test equality on id

        :param other: Category instance
        :return:
        """
        if not isinstance(other, self.__class__):
            return False
        return other.id == self.id

    def __hash__(self):
        return hash(self.id)
