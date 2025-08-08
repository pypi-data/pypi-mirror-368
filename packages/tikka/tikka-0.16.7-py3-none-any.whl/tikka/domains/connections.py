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
from tikka.adapters.network.node.connection import NodeConnection
from tikka.domains.entities.events import ConnectionsEvent
from tikka.domains.events import EventDispatcher
from tikka.interfaces.adapters.network.connection import ConnectionInterface
from tikka.interfaces.adapters.network.network import NetworkInterface
from tikka.interfaces.domains.connections import ConnectionsInterface
from tikka.interfaces.entities.Server import ServerInterface


class ConnectionWithEventDispatcher(ConnectionInterface):
    def __init__(
        self, connection: ConnectionInterface, event_dispatcher: EventDispatcher
    ) -> None:
        """
        Init ConnectionWithEventDispatcher instance

        :param connection: EventDispatcher instance
        :param event_dispatcher: EventDispatcher instance
        :return:
        """
        self.connection = connection
        self.event_dispatcher = event_dispatcher

    def connect(self, server: ServerInterface) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ConnectionInterface.connect.__doc__
        )
        self.connection.connect(server)
        if self.connection.is_connected():
            if isinstance(self.connection, NodeConnection):
                self.event_dispatcher.dispatch_event(
                    ConnectionsEvent(ConnectionsEvent.EVENT_TYPE_NODE_CONNECTED)
                )
            else:
                self.event_dispatcher.dispatch_event(
                    ConnectionsEvent(ConnectionsEvent.EVENT_TYPE_INDEXER_CONNECTED)
                )

    def disconnect(self) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ConnectionInterface.disconnect.__doc__
        )
        self.connection.disconnect()
        if not self.connection.is_connected():
            if isinstance(self.connection, NodeConnection):
                self.event_dispatcher.dispatch_event(
                    ConnectionsEvent(ConnectionsEvent.EVENT_TYPE_NODE_DISCONNECTED)
                )
            else:
                self.event_dispatcher.dispatch_event(
                    ConnectionsEvent(ConnectionsEvent.EVENT_TYPE_INDEXER_DISCONNECTED)
                )

    def is_connected(self) -> bool:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ConnectionInterface.is_connected.__doc__
        )
        return self.connection.is_connected()


class Connections(ConnectionsInterface):
    """
    Connections domain class
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
        super().__init__(network, event_dispatcher)

        self._node = self.network.node.connection
        self._indexer = self.network.indexer.connection

    @property
    def node(self) -> ConnectionInterface:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ConnectionsInterface.node.__doc__
        )
        return self._node

    @property
    def indexer(self) -> ConnectionInterface:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ConnectionsInterface.indexer.__doc__
        )
        return self._indexer

    def disconnect_all(self):
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ConnectionsInterface.disconnect_all.__doc__
        )
        self.node.disconnect()
        self.indexer.disconnect()

    def are_all_connected(self) -> bool:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ConnectionsInterface.are_all_connected.__doc__
        )
        return self.node.is_connected() and self.indexer.is_connected()
