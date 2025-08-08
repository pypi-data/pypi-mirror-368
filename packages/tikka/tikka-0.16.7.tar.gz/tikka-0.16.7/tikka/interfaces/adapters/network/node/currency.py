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

from tikka.domains.entities.currency import Currency
from tikka.interfaces.adapters.network.node.node import NetworkNodeInterface


class NodeCurrencyInterface(abc.ABC):
    """
    NodeCurrencyInterface class
    """

    @abc.abstractmethod
    def __init__(self, node: NetworkNodeInterface) -> None:
        """
        Use node connection to request currency information

        :param node: NetworkNodeInterface instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_instance(self) -> Currency:
        """
        Return Currency instance

        :return:
        """
        raise NotImplementedError


class NodeCurrencyException(Exception):
    """
    NodeCurrencyException class
    """
