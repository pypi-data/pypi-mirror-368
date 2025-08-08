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
from datetime import datetime
from typing import List, Optional

from dateutil import parser
from gql import gql

from tikka.domains.entities.transfer import Transfer
from tikka.interfaces.adapters.network.connection import NetworkConnectionError
from tikka.interfaces.adapters.network.indexer.transfers import (
    IndexerTransfersException,
    IndexerTransfersInterface,
)


class IndexerTransfers(IndexerTransfersInterface):
    """
    IndexerTransfers class
    """

    def list(
        self,
        address: str,
        limit: int,
        offset: int = 0,
        sort_column: str = IndexerTransfersInterface.COLUMN_TIMESTAMP,
        sort_order: str = IndexerTransfersInterface.SORT_ORDER_DESCENDING,
        from_datetime: Optional[datetime] = None,
        to_datetime: Optional[datetime] = None,
    ) -> List[Transfer]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IndexerTransfersInterface.list.__doc__
        )

        if (
            not self.indexer.connection.is_connected()
            or self.indexer.connection.client is None
        ):
            raise IndexerTransfersException(NetworkConnectionError())

        # Construire la condition de filtrage pour la date
        date_filter = []
        if from_datetime:
            date_filter.append(
                f'{{ timestamp: {{ _gte: "{from_datetime.isoformat()}" }} }}'
            )
        if to_datetime:
            date_filter.append(
                f'{{ timestamp: {{ _lte: "{to_datetime.isoformat()}" }} }}'
            )

        date_filter_str = (
            "_and: [" + ", ".join(date_filter) + "]" if date_filter else ""
        )

        # Construire la requête GraphQL
        query = gql(
            f"""
            query {{
              transfer(
                limit: {limit}
                offset: {offset}
                orderBy: {{
                    {sort_column}: {sort_order}
                }}
                where: {{
                    _or: [
                        {{ fromId: {{ _eq: \"{address}\" }} }}
                        {{ toId: {{ _eq: \"{address}\" }} }}
                    ]
                    {date_filter_str}
                }}
              ) {{
                    id
                    fromId
                    from {{
                      identity {{
                        index
                        name
                      }}
                    }}
                    toId
                    to {{
                      identity {{
                        index
                        name
                      }}
                    }}
                    amount
                    timestamp
                    comment {{
                      type
                      remark
                      remarkBytes
                    }}
                }}
            }}
        """
        )

        try:
            result = self.indexer.connection.client.execute(query)
        except Exception as exception:
            raise IndexerTransfersException(exception)

        transfers = []
        for transfer in result["transfer"]:
            issuer_identity_index = (
                transfer["from"]["identity"]["index"]
                if transfer["from"]["identity"]
                else None
            )
            issuer_identity_name = (
                transfer["from"]["identity"]["name"]
                if transfer["from"]["identity"]
                else None
            )
            receiver_identity_index = (
                transfer["to"]["identity"]["index"]
                if transfer["to"]["identity"]
                else None
            )
            receiver_identity_name = (
                transfer["to"]["identity"]["name"]
                if transfer["to"]["identity"]
                else None
            )

            comment = None
            comment_type = None
            if transfer["comment"]:
                comment = (
                    transfer["comment"]["remarkBytes"]
                    if transfer["comment"]["type"] == "RAW"
                    else transfer["comment"]["remark"]
                )
                comment_type = transfer["comment"]["type"]

            transfers.append(
                Transfer(
                    id=transfer["id"],
                    issuer_address=transfer["fromId"],
                    issuer_identity_index=issuer_identity_index,
                    issuer_identity_name=issuer_identity_name,
                    receiver_address=transfer["toId"],
                    receiver_identity_index=receiver_identity_index,
                    receiver_identity_name=receiver_identity_name,
                    amount=transfer["amount"],
                    timestamp=parser.parse(transfer["timestamp"]),
                    comment=comment,
                    comment_type=comment_type,
                )
            )

        return transfers

    def count(self, address) -> int:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IndexerTransfersInterface.count.__doc__
        )
        if (
            not self.indexer.connection.is_connected()
            or self.indexer.connection.client is None
        ):
            raise IndexerTransfersException(NetworkConnectionError())

        query = gql(
            """
            query {
                transferAggregate (
                    where: {
                        _or: [
                        {fromId: {_eq: \""""
            + address
            + """\"}}
                        {toId: {_eq: \""""
            + address
            + """\"}}
                        ]
                    }
                ) {
                    aggregate {
                        count
                    }
                }
            }
            """
        )
        try:
            result = self.indexer.connection.client.execute(query)
        except Exception as exception:
            raise IndexerTransfersException(exception)

        # {
        #     "transferAggregate": {
        #       "aggregate": {
        #         "count": 3
        #       }
        #     }
        # }
        return result["transferAggregate"]["aggregate"]["count"]
