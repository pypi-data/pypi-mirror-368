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

from tikka.interfaces.adapters.network.connection import ConnectionInterface

if TYPE_CHECKING:
    from tikka.domains.entities.node import Node
    from tikka.interfaces.adapters.network.node.accounts import NodeAccountsInterface
    from tikka.interfaces.adapters.network.node.authorities import (
        NodeAuthoritiesInterface,
    )
    from tikka.interfaces.adapters.network.node.currency import NodeCurrencyInterface
    from tikka.interfaces.adapters.network.node.identities import (
        NodeIdentitiesInterface,
    )
    from tikka.interfaces.adapters.network.node.smiths import NodeSmithsInterface
    from tikka.interfaces.adapters.network.node.technical_committee import (
        NodeTechnicalCommitteeInterface,
    )
    from tikka.interfaces.adapters.network.node.transfers import NodeTransfersInterface


class NetworkNodeInterface(abc.ABC):
    """
    NetworkNodeInterface class
    """

    @abc.abstractmethod
    def get(self) -> Node:
        """
        Return the node instance with infos from connection

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_ss58_prefix(self) -> int:
        """
        Return the node ss58 prefix from connection

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_genesis_block_hash(self) -> str:
        """
        Return the node genesis block hash from connection

        :return:
        """
        raise NotImplementedError

    @property
    def connection(self) -> ConnectionInterface:
        """
        Return ConnectionsInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def accounts(self) -> NodeAccountsInterface:
        """
        Return NodeAccountsInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def authorities(self) -> NodeAuthoritiesInterface:
        """
        Return NodeAuthoritiesInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def currency(self) -> NodeCurrencyInterface:
        """
        Return NodeCurrencyInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def identities(self) -> NodeIdentitiesInterface:
        """
        Return NodeIdentitiesInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def smiths(self) -> NodeSmithsInterface:
        """
        Return NodeSmithsInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def technical_committee(self) -> NodeTechnicalCommitteeInterface:
        """
        Return NodeTechnicalCommitteeInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def transfers(self) -> NodeTransfersInterface:
        """
        Return NodeTransfersInterface instance

        :return:
        """
        raise NotImplementedError


class NetworkNodeException(Exception):
    """
    NetworkNodeException class
    """
