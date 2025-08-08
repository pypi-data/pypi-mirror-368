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

import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tikka.interfaces.adapters.network.indexer.indexer import (
        NetworkIndexerInterface,
    )
    from tikka.interfaces.adapters.network.node.node import NetworkNodeInterface


class NetworkInterface(abc.ABC):
    """
    NetworkInterface class
    """

    @property
    def node(self) -> NetworkNodeInterface:
        """
        Return NetworkNodeInterface instance

        :return:
        """
        raise NotImplementedError

    @property
    def indexer(self) -> NetworkIndexerInterface:
        """
        Return NetworkIndexerInterface instance

        :return:
        """
        raise NotImplementedError


class NetworkException(Exception):
    """
    NetworkException class
    """
