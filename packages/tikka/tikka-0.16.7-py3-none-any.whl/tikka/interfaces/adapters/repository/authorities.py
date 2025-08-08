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

from tikka.domains.entities.authorities import Authority


class AuthoritiesRepositoryInterface(abc.ABC):
    """
    AuthoritiesRepositoryInterface class
    """

    @abc.abstractmethod
    def add(self, authority: Authority) -> None:
        """
        Add a new authority in repository

        :param authority: Authority instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, identity_index: int) -> Optional[Authority]:
        """
        Return Authority instance from repository

        :param identity_index: Identity index
        :return:
        """
        raise NotImplementedError

    def update(self, authority: Authority) -> None:
        """
        Update authority in repository

        :param authority: Authority instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, identity_index: int) -> None:
        """
        Delete authority in repository

        :param identity_index: Identity index of authority to delete
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_all(self) -> None:
        """
        Delete all authorities

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def exists(self, identity_index: int) -> bool:
        """
        Return True if authority with identity index is in repository, else False

        :param identity_index: Identity index of authority to check
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> List[Authority]:
        """
        Return list of all Authority in repository

        :return:
        """
        raise NotImplementedError
