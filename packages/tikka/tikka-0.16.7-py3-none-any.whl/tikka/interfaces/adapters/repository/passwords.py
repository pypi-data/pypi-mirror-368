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

from tikka.domains.entities.password import Password


class PasswordsRepositoryInterface(abc.ABC):
    """
    PasswordsRepositoryInterface class
    """

    @abc.abstractmethod
    def list(self) -> List[Password]:
        """
        List passwords from repository

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add(self, password: Password) -> None:
        """
        Add a new password in repository

        :param password: Password instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, root: str) -> Optional[Password]:
        """
        Return Password instance from repository

        :param root: Root address
        :return:
        """
        raise NotImplementedError

    def update(self, password: Password) -> None:
        """
        Update password in repository

        :param password: Password instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, root: str) -> None:
        """
        Delete password in repository

        :param root: Password root address to delete
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_all(self) -> None:
        """
        Delete all passwords in repository

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def exists(self, root: str) -> bool:
        """
        Return True if password with root address is in repository, else False

        :param root: Password root address to check
        :return:
        """
        raise NotImplementedError
