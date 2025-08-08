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
from __future__ import annotations

import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from interfaces.adapters.network.connection import ConnectionInterface
    from interfaces.adapters.network.indexer.accounts import IndexerAccountsInterface
    from interfaces.adapters.network.indexer.identities import (
        IndexerIdentitiesInterface,
    )
    from interfaces.adapters.network.indexer.transfers import IndexerTransfersInterface

    from tikka.domains.entities.indexer import Indexer


class NetworkIndexerInterface(abc.ABC):
    """
    NetworkIndexerInterface class
    """

    @property
    def connection(self) -> ConnectionInterface:
        """
        Return ConnectionsInterface instance

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self) -> Indexer:
        """
        Return the node instance with infos from connection

        :return:
        """
        raise NotImplementedError

    @property
    def identities(self) -> IndexerIdentitiesInterface:
        """
        Return IndexerIdentitiesInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def transfers(self) -> IndexerTransfersInterface:
        """
        Return IndexerTransfersInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def accounts(self) -> IndexerAccountsInterface:
        """
        Return IndexerAccountsInterface instance

        :return:
        """
        raise NotImplementedError


class NetworkIndexerException(Exception):
    """
    NetworkIndexerException class
    """
