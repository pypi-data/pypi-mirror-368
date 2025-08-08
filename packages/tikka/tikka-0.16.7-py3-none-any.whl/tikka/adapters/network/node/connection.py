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
import logging
import socket
from pathlib import Path
from typing import Optional

from tikka.adapters.network.node.substrate_client import SubstrateClient
from tikka.domains.entities.constants import DATA_PATH
from tikka.interfaces.adapters.network.connection import ConnectionInterface
from tikka.interfaces.entities.Server import ServerInterface

# websocket timeout
RPC_CONNECTION_TIMEOUT = 30


class NodeConnection(ConnectionInterface):
    """
    NodeConnection class
    """

    def __init__(self) -> None:
        """
        Init NodeConnection instance

        RPC client is available in self.client after connect()
        """
        self.client: Optional[SubstrateClient] = None

    def connect(self, server: ServerInterface) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ConnectionInterface.connect.__doc__
        )
        logging.debug("CONNECTING TO NODE......................................")
        try:
            self.client = SubstrateClient(
                url=server.url,
                websocket_options={
                    "timeout": RPC_CONNECTION_TIMEOUT,
                    "sockopt": ((socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),),
                },
                metadata_dir=str(Path(DATA_PATH).expanduser()),
            )
        except Exception as exception:
            self.client = None
            logging.exception(exception)
            logging.debug(
                "CONNECTION TO NODE......................................FAILED !"
            )

        if self.client is not None:
            logging.debug(
                "CONNECTION TO NODE......................................SUCCESS !"
            )

    def disconnect(self) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ConnectionInterface.disconnect.__doc__
        )
        if self.client is not None:
            self.client.close()
            self.client = None

    def is_connected(self) -> bool:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ConnectionInterface.is_connected.__doc__
        )
        return self.client is not None
