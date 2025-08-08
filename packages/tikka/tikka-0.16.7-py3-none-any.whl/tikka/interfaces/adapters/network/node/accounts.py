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
from typing import Dict, List, Optional

from tikka.interfaces.adapters.network.node.node import NetworkNodeInterface


class NodeAccountsInterface(abc.ABC):
    """
    NodeAccountsInterface class
    """

    @abc.abstractmethod
    def __init__(self, node: NetworkNodeInterface) -> None:
        """
        Use node connection to request accounts information

        :param node: NetworkNodeInterface instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_balance(self, address: str) -> Optional[int]:
        """
        Return the balance amount or none if account not exists

        :param address: Account address
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_balances(self, addresses: List[str]) -> Dict[str, Optional[int]]:
        """
        Return a dict with balance for each address

        {
            address: balance
        }

        :param addresses: Account address list
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_unclaimed_ud_balance(self, first_eligible_ud: int) -> int:
        """
        Return the balance amount of the unclaimed UDs

        :param first_eligible_ud: First eligible UD index of identity
        :return:
        """
        raise NotImplementedError


class NodeAccountsException(Exception):
    """
    NodeAccountsException class
    """
