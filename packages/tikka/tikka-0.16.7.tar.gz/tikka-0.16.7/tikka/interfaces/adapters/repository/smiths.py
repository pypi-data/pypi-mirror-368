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
from typing import List, Optional

from tikka.domains.entities.smith import Smith


class SmithsRepositoryInterface(abc.ABC):
    """
    SmithsRepositoryInterface class
    """

    @abc.abstractmethod
    def add(self, smith: Smith) -> None:
        """
        Add a new smith in repository

        :param smith: Smith instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, index: int) -> Optional[Smith]:
        """
        Return Smith instance from repository

        :param index: Identity index
        :return:
        """
        raise NotImplementedError

    def update(self, smith: Smith) -> None:
        """
        Update smith in repository

        :param smith: Smith instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, index: int) -> None:
        """
        Delete smith in repository

        :param index: Identity index of smith to delete
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_all(self) -> None:
        """
        Delete all smiths in repository

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def exists(self, index: int) -> bool:
        """
        Return True if smith with identity index is in repository, else False

        :param index: Identity index of smith to check
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> List[Smith]:
        """
        Return list of all smiths in repository

        :return:
        """
        raise NotImplementedError
