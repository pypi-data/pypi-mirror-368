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
from typing import Dict, List

from tikka.interfaces.adapters.network.indexer.indexer import NetworkIndexerInterface


class IndexerIdentitiesInterface(abc.ABC):
    """
    IndexerIdentitiesInterface class
    """

    def __init__(self, indexer: NetworkIndexerInterface) -> None:
        """
        Init IndexerIdentitiesInterface instance

        :param indexer: NetworkIndexerInterface instance
        :return:
        """
        self.indexer = indexer

    @abc.abstractmethod
    def get_identity_name(self, identity_index: int) -> str:
        """
        Return the Identity name from index

        :param identity_index: Identity index
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_identity_names(self, index_list: List[int]) -> Dict[int, str]:
        """
        Return the account Identity index from addresses if exists

        :param index_list: List of identity indice
        :return:
        """
        raise NotImplementedError


class IndexerIdentitiesException(Exception):
    """
    IndexerIdentitiesException class
    """
