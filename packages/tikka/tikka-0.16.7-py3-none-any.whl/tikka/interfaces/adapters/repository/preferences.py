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

import abc
from typing import Dict, Optional


class PreferencesRepositoryInterface(abc.ABC):
    """
    PreferencesRepositoryInterface class
    """

    @abc.abstractmethod
    def get(self, key: str) -> Optional[str]:
        """
        Return the key value

        :param key: Key name
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def set(self, key: str, value: Optional[str]) -> None:
        """
        Set the key value

        :param key: Key name
        :param value: Value to store
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_all(self) -> None:
        """
        Delete all preferences entries

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> Dict[str, str]:
        """
        Return a dict {key: value} of all preferences

        :return:
        """
        raise NotImplementedError
