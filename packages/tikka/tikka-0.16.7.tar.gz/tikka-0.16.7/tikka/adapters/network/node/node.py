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

import logging

from tikka.adapters.network.node.accounts import NodeAccounts
from tikka.adapters.network.node.authorities import NodeAuthorities
from tikka.adapters.network.node.connection import NodeConnection
from tikka.adapters.network.node.currency import NodeCurrency
from tikka.adapters.network.node.identities import NodeIdentities
from tikka.adapters.network.node.smiths import NodeSmiths
from tikka.adapters.network.node.technical_committee import NodeTechnicalCommittee
from tikka.adapters.network.node.transfers import NodeTransfers
from tikka.domains.entities.node import Node
from tikka.interfaces.adapters.network.connection import NetworkConnectionError
from tikka.interfaces.adapters.network.node.node import (
    NetworkNodeException,
    NetworkNodeInterface,
)


class NetworkNode(NetworkNodeInterface):
    """
    NetworkNode class
    """

    def __init__(self):
        """
        Init NetworkNode instance
        """
        self._connection = NodeConnection()
        self._accounts = NodeAccounts(self)
        self._authorities = NodeAuthorities(self)
        self._currency = NodeCurrency(self)
        self._identities = NodeIdentities(self)
        self._smiths = NodeSmiths(self)
        self._technical_committee = NodeTechnicalCommittee(self)
        self._transfers = NodeTransfers(self)

    @property
    def connection(self) -> NodeConnection:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NetworkNodeInterface.connection.__doc__
        )
        return self._connection

    def get(self) -> Node:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NetworkNodeInterface.get.__doc__
        )
        if not self.connection.is_connected() or self.connection.client is None:
            raise NetworkNodeException(NetworkConnectionError())

        try:
            response = self.connection.client.rpc_request("system_localPeerId", [])
        except Exception as exception:
            logging.exception(exception)
            raise NetworkNodeException(exception)

        if response is None:
            message = "node.get system_localPeerId returns None"
            logging.error(message)
            raise NetworkNodeException(message)

        peer_id = response.get("result")

        try:
            response = self.connection.client.rpc_request(  # type: ignore
                "system_syncState", []
            )
        except Exception as exception:
            logging.exception(exception)
            raise NetworkNodeException(exception)

        if response is None:
            message = "node.get system_syncState returns None"
            logging.error(message)
            raise NetworkNodeException(message)

        sync_state = response.get("result")
        current_block = sync_state["currentBlock"] if sync_state is not None else None

        try:
            current_epoch_result = self.connection.client.query("Babe", "EpochIndex")
        except Exception as exception:
            logging.exception(exception)
            raise NetworkNodeException(exception)

        try:
            response = self.connection.client.rpc_request("system_name", [])
        except Exception as exception:
            logging.exception(exception)
            raise NetworkNodeException(exception)

        if response is None:
            message = "node.get system_name returns None"
            logging.error(message)
            raise NetworkNodeException(message)

        chain_name = response.get("result")

        try:
            response = self.connection.client.rpc_request("system_version", [])
        except Exception as exception:
            logging.exception(exception)
            raise NetworkNodeException(exception)

        if response is None:
            message = "node.get system_version returns None"
            logging.error(message)
            raise NetworkNodeException(message)

        chain_version = response.get("result")

        unsafe_api_exposed = True
        try:
            self.connection.client.rpc_request("babe_epochAuthorship", [])
        except Exception as exception:
            error_message = str(exception)
            if "'code': -32601" not in error_message:
                logging.exception(exception)
            unsafe_api_exposed = False

        return Node(
            self.connection.client.url,
            peer_id=peer_id,
            block=current_block,
            software=chain_name,
            software_version=chain_version,
            epoch_index=current_epoch_result,
            unsafe_api_exposed=unsafe_api_exposed,
        )

    def get_ss58_prefix(self) -> int:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NetworkNodeInterface.get.__doc__
        )
        if not self.connection.is_connected() or self.connection.client is None:
            raise NetworkNodeException(NetworkConnectionError())

        return self.connection.client.runtime_config.ss58_format

    def get_genesis_block_hash(self) -> str:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NetworkNodeInterface.get.__doc__
        )
        if not self.connection.is_connected() or self.connection.client is None:
            raise NetworkNodeException(NetworkConnectionError())

        return self.connection.client.get_block_hash(0)

    @property
    def accounts(self) -> NodeAccounts:
        """
        Return NodeAccountsInterface instance

        :return:
        """
        return self._accounts

    @property
    def authorities(self) -> NodeAuthorities:
        """
        Return NodeAuthoritiesInterface instance

        :return:
        """
        return self._authorities

    @property
    def currency(self) -> NodeCurrency:
        """
        Return NodeCurrencyInterface instance

        :return:
        """
        return self._currency

    @property
    def identities(self) -> NodeIdentities:
        """
        Return NodeIdentitiesInterface instance

        :return:
        """
        return self._identities

    @property
    def smiths(self) -> NodeSmiths:
        """
        Return NodeSmithsInterface instance

        :return:
        """
        return self._smiths

    @property
    def technical_committee(self) -> NodeTechnicalCommittee:
        """
        Return NodeTechnicalCommitteeInterface instance

        :return:
        """
        return self._technical_committee

    @property
    def transfers(self) -> NodeTransfers:
        """
        Return NodeTransfersInterface instance

        :return:
        """
        return self._transfers
