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

from typing import Dict, List

from gql import gql

from tikka.interfaces.adapters.network.connection import NetworkConnectionError
from tikka.interfaces.adapters.network.indexer.identities import (
    IndexerIdentitiesException,
    IndexerIdentitiesInterface,
)


class IndexerIdentities(IndexerIdentitiesInterface):
    """
    IndexerIdentities class
    """

    def get_identity_name(self, identity_index: int) -> str:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IndexerIdentitiesInterface.get_identity_name.__doc__
        )
        if (
            not self.indexer.connection.is_connected()
            or self.indexer.connection.client is None
        ):
            raise IndexerIdentitiesException(NetworkConnectionError())

        query = gql(
            """
                query {
                    identity(
                        where: {
                            index: {_eq: """
            + str(identity_index)
            + """ } 
                        } 
                        ) {
                            name
                    }
                }
                """
        )
        try:
            result = self.indexer.connection.client.execute(query)
        except Exception as exception:
            raise IndexerIdentitiesException(exception)

        #
        #    {
        #         "identity": [
        #             {
        #                 "name": "vit"
        #             }
        #         ]
        #     }
        #
        return result["identity"][0]["name"]

    def get_identity_names(self, index_list: List[int]) -> Dict[int, str]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IndexerIdentitiesInterface.get_identity_names.__doc__
        )
        if (
            not self.indexer.connection.is_connected()
            or self.indexer.connection.client is None
        ):
            raise IndexerIdentitiesException(NetworkConnectionError())

        query = gql(
            """
                query GetNamesByIndex($indices: [Int!]!) {
                    identity(where: { index: { _in: $indices } }) {
                        index
                        name
                    }
                }
                """
        )
        variables = {"indices": index_list}
        try:
            result = self.indexer.connection.client.execute(
                query, variable_values=variables
            )
        except Exception as exception:
            raise IndexerIdentitiesException(exception)

        #
        #    {
        #         "identity": [
        #             {
        #                 "index": 65,
        #                 "name": "jean"
        #             },
        #             {
        #                 "index": 112,
        #                 "name": "marc"
        #             },
        #         ]
        #     }
        #
        names = {}
        for row in result["identity"]:
            names[row["index"]] = row["name"]
        return names
