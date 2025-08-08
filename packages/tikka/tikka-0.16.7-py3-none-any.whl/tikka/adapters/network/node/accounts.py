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
from typing import TYPE_CHECKING, Dict, List, Optional

from tikka.interfaces.adapters.network.connection import NetworkConnectionError
from tikka.interfaces.adapters.network.node.accounts import (
    NodeAccountsException,
    NodeAccountsInterface,
)

if TYPE_CHECKING:
    from tikka.adapters.network.node.node import NetworkNode


class NodeAccounts(NodeAccountsInterface):
    """
    NodeAccounts class
    """

    def __init__(self, node: "NetworkNode") -> None:
        """
        Use NetworkNodeInterface to request/send smiths information

        :param node: NetworkNodeInterface instance
        :return:
        """
        self.node = node

    def get_balance(self, address: str) -> Optional[int]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeAccountsInterface.get_balance.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeAccountsException(NetworkConnectionError())

        # system.account: FrameSystemAccountInfo
        # {
        #   nonce: 1
        #   consumers: 0
        #   providers: 1
        #   sufficients: 0
        #   data: {
        #     randomId: 0x18a4d...
        #     free: 9,799
        #     reserved: 0
        #     feeFrozen: 0
        #   }
        # }
        try:
            result = self.node.connection.client.query("System", "Account", [address])
        except Exception as exception:
            logging.exception(exception)
            raise NodeAccountsException(exception)

        if result is None:
            balance = None
        else:
            balance = result["data"]["free"] + result["data"]["reserved"]

        return balance

    def get_balances(self, addresses: List[str]) -> Dict[str, Optional[int]]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeAccountsInterface.get_balances.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeAccountsException(NetworkConnectionError())

        storage_functions = []
        for address in addresses:
            storage_functions.append(("System", "Account", [address]))

        try:
            multi_result = self.node.connection.client.query_multi(storage_functions)
        except Exception as exception:
            logging.exception(exception)
            raise NodeAccountsException(exception)

        balances: Dict[str, Optional[int]] = {}
        for index, value_obj in enumerate(multi_result):
            if value_obj is None:
                balances[addresses[index]] = None
            else:
                balances[addresses[index]] = (
                    value_obj["data"]["free"] + value_obj["data"]["reserved"]
                )

        return balances

    def get_unclaimed_ud_balance(self, first_eligible_ud: int) -> int:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeAccountsInterface.get_unclaimed_ud_balance.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeAccountsException(NetworkConnectionError())

        if first_eligible_ud == 0:
            return 0

        try:
            result = self.node.connection.client.query(
                "UniversalDividend", "CurrentUdIndex"
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeAccountsException(exception)

        current_index = result

        try:
            result = self.node.connection.client.query(
                "UniversalDividend", "PastReevals"
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeAccountsException(exception)

        if result is None:
            return 0

        balance = 0
        index = current_index
        for reeval_index, reeval_value in reversed(result):
            if reeval_index <= first_eligible_ud:
                count = index - first_eligible_ud
                balance += count * reeval_value
                break
            else:
                count = index - reeval_index
                balance += count * reeval_value
                index = reeval_index

        return balance
