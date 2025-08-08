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

from tikka.domains.events import EventDispatcher
from tikka.interfaces.adapters.network.connection import ConnectionInterface
from tikka.interfaces.adapters.network.network import NetworkInterface


class ConnectionsInterface(abc.ABC):
    """
    ConnectionsInterface class
    """

    def __init__(
        self, network: NetworkInterface, event_dispatcher: EventDispatcher
    ) -> None:
        """
        Init Connections domain instance

        :param network: NetworkInterface instance
        :param event_dispatcher: EventDispatcher instance
        :return:
        """
        self.network = network
        self.event_dispatcher = event_dispatcher

    @abc.abstractmethod
    def disconnect_all(self):
        """
        Disconnect all connections

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def are_all_connected(self) -> bool:
        """
        Return True if connection is active, False otherwise

        :return:
        """
        raise NotImplementedError

    @property
    def node(self) -> ConnectionInterface:
        """
        Return a ConnectionInterface instance for the node

        :return:
        """
        raise NotImplementedError

    @property
    def indexer(self) -> ConnectionInterface:
        """
        Return a ConnectionInterface instance for the indexer

        :return:
        """
        raise NotImplementedError
