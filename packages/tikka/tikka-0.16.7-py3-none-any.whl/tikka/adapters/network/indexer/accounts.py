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

from gql import gql

from tikka.interfaces.adapters.network.connection import NetworkConnectionError
from tikka.interfaces.adapters.network.indexer.accounts import (
    IndexerAccountsException,
    IndexerAccountsInterface,
)


class IndexerAccounts(IndexerAccountsInterface):
    """
    IndexerAccounts class
    """

    def is_legacy_v1(self, address: str) -> bool:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IndexerAccountsInterface.is_legacy_v1.__doc__
        )
        if (
            not self.indexer.connection.is_connected()
            or self.indexer.connection.client is None
        ):
            raise IndexerAccountsException(NetworkConnectionError())

        query = gql(
            f"""
            query {{
                account (where: {{
                            createdOn: {{_eq: 0  }},
                            id: {{_eq: "{address}"}}
                        }}) {{
                            id
                        }}

            }}
            """
        )
        try:
            result = self.indexer.connection.client.execute(query)
        except Exception as exception:
            raise IndexerAccountsException(exception)

        #
        #    {
        #     "account": [
        #       {
        #         "id": "xxxxxxxx"
        #       }
        #     ]
        #    }
        #
        return len(result["account"]) > 0
