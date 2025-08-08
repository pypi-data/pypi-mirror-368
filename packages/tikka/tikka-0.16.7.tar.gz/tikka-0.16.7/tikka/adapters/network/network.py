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
from __future__ import annotations

from tikka.adapters.network.indexer.indexer import NetworkIndexer
from tikka.adapters.network.node.node import NetworkNode
from tikka.interfaces.adapters.network.network import NetworkInterface


class Network(NetworkInterface):
    """
    Network class
    """

    def __init__(self) -> None:
        """
        Init Network instance

        """
        self._node = NetworkNode()
        self._indexer = NetworkIndexer()

    @property
    def node(self) -> NetworkNode:
        """
        Return NetworkNode instance

        :return:
        """
        return self._node

    @property
    def indexer(self) -> NetworkIndexer:
        """
        Return NetworkIndexer instance

        :return:
        """
        return self._indexer


class NetworkException(Exception):
    """
    NetworkException class
    """
