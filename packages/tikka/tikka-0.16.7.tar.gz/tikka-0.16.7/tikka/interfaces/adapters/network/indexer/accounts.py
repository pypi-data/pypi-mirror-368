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

from tikka.interfaces.adapters.network.indexer.indexer import NetworkIndexerInterface


class IndexerAccountsInterface(abc.ABC):
    """
    IndexerAccountsInterface class
    """

    def __init__(self, indexer: NetworkIndexerInterface) -> None:
        """
        Init IndexerAccountsInterface instance

        :param indexer: NetworkIndexerInterface instance
        :return:
        """
        self.indexer = indexer

    @abc.abstractmethod
    def is_legacy_v1(self, address: str) -> bool:
        """
        Return True if account is a legacy v1 account (present in genesis)

        :param address: ss58 account address
        :return:
        """
        raise NotImplementedError


class IndexerAccountsException(Exception):
    """
    IndexerAccountsException class
    """
