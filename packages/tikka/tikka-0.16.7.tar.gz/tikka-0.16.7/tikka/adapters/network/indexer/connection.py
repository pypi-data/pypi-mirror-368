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
from typing import Optional

from gql import Client, gql
from gql.client import SyncClientSession
from gql.transport.requests import RequestsHTTPTransport

from tikka.interfaces.adapters.network.connection import ConnectionInterface
from tikka.interfaces.entities.Server import ServerInterface

# graphQL timeout
GRAPHQL_CONNECTION_TIMEOUT = 30


class IndexerConnection(ConnectionInterface):
    """
    IndexerConnection class
    """

    def __init__(self) -> None:
        """
        Init IndexerConnection instance

        gql session is available in self.client after connect()
        """
        self.client: Optional[SyncClientSession] = None

    def connect(self, server: ServerInterface) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ConnectionInterface.connect.__doc__
        )
        self.url = server.url
        logging.debug("CONNECTING TO INDEXER......................................")
        # Create a GraphQL client using the defined transport
        gql_client = Client(
            transport=RequestsHTTPTransport(url=server.url),
        )

        try:
            self.client = gql_client.connect_sync()
            # check connection...
            query = gql(
                """
            query {
                block(
                    limit: 1
                    offset: 0
                    orderBy: [{timestamp: DESC_NULLS_LAST }]
                    where: {}
                  ) {
                    height
                  }
            }
            """
            )
            result = self.client.execute(query)  # type: ignore
        except Exception as exception:
            logging.exception(exception)
            self.client = None
            logging.debug(
                "CONNECTION TO INDEXER......................................FAILED !"
            )
        else:
            if len(result["block"]) < 1:
                self.client = None
                logging.debug(
                    "CONNECTION TO INDEXER......................................FAILED !"
                )
            else:
                logging.debug(
                    "CONNECTION TO INDEXER......................................SUCCESS !"
                )

    def disconnect(self) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ConnectionInterface.disconnect.__doc__
        )
        if self.client is not None:
            self.client.close()
            self.client = None
            logging.debug("GraphQL connection closed.")

    def is_connected(self) -> bool:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            ConnectionInterface.is_connected.__doc__
        )
        return self.client is not None
