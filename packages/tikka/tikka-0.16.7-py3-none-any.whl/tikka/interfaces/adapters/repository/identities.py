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
from typing import Dict, List, Optional

from tikka.domains.entities.identity import Identity


class IdentitiesRepositoryInterface(abc.ABC):
    """
    IdentitiesRepositoryInterface class
    """

    COLUMN_INDEX = "identity_index_"
    COLUMN_NAME = "identity_name"

    @abc.abstractmethod
    def add(self, identity: Identity) -> None:
        """
        Add a new identity in repository

        :param identity: Identity instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, index: int) -> Optional[Identity]:
        """
        Return Identity instance from repository

        :param index: Identity index
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_address(self, address: str) -> Optional[Identity]:
        """
        Return Identity instance from repository

        :param address: Identity index
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_addresses(self, addresses: List[str]) -> Dict[str, Optional[Identity]]:
        """
        Return Identity instances dict[address, Identity] from address list

        :param addresses: Address list
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_index_by_address(self, address: str) -> Optional[int]:
        """
        Return Identity index from repository

        :param address: Identity index
        :return:
        """
        raise NotImplementedError

    def update(self, identity: Identity) -> None:
        """
        Update identity in repository

        :param identity: Identity instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, index: int) -> None:
        """
        Delete identity in repository

        :param index: Identity index to delete
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_all(self) -> None:
        """
        Delete all identities in repository

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def exists(self, index: int) -> bool:
        """
        Return True if identity with index is in repository, else False

        :param index: Identity index to check
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> List[Identity]:
        """
        Return all identities from repository

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list_indice(self) -> List[int]:
        """
        Return all identity indice from repository

        :return:
        """
        raise NotImplementedError
