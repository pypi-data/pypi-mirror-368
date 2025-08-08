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

from dataclasses import dataclass
from typing import ClassVar

from tikka.domains.entities.account import Account
from tikka.domains.entities.category import Category
from tikka.domains.entities.transfer import Transfer
from tikka.interfaces.entities.events import EventInterface


@dataclass
class AccountEvent(EventInterface):
    """
    AccountEvent class
    """

    type: str
    account: Account

    # type ignore required because mypy bug https://github.com/python/mypy/issues/6473
    EVENT_TYPE_ADD: ClassVar[str] = f"{__qualname__}.add"  # type: ignore
    EVENT_TYPE_UPDATE: ClassVar[str] = f"{__qualname__}.update"  # type: ignore
    EVENT_TYPE_DELETE: ClassVar[str] = f"{__qualname__}.delete"  # type: ignore


@dataclass
class CategoryEvent(EventInterface):
    """
    CategoryEvent class
    """

    type: str
    category: Category

    # type ignore required because mypy bug https://github.com/python/mypy/issues/6473
    EVENT_TYPE_ADD: ClassVar[str] = f"{__qualname__}.add"  # type: ignore
    EVENT_TYPE_UPDATE: ClassVar[str] = f"{__qualname__}.update"  # type: ignore
    EVENT_TYPE_DELETE: ClassVar[str] = f"{__qualname__}.delete"  # type: ignore


@dataclass
class CurrencyEvent(EventInterface):
    """
    ConfigEvent class
    """

    type: str
    currency: str

    # type ignore required because mypy bug https://github.com/python/mypy/issues/6473
    EVENT_TYPE_PRE_CHANGE: ClassVar[str] = f"{__qualname__}.pre_change"  # type: ignore
    EVENT_TYPE_CHANGED: ClassVar[str] = f"{__qualname__}.changed"  # type: ignore


@dataclass
class NodesEvent(EventInterface):
    """
    NodesEvent class
    """

    type: str

    # type ignore required because mypy bug https://github.com/python/mypy/issues/6473
    EVENT_TYPE_LIST_CHANGED: ClassVar[str] = f"{__qualname__}.list_changed"  # type: ignore


@dataclass
class IndexersEvent(EventInterface):
    """
    IndexersEvent class
    """

    type: str

    # type ignore required because mypy bug https://github.com/python/mypy/issues/6473
    EVENT_TYPE_LIST_CHANGED: ClassVar[str] = f"{__qualname__}.list_changed"  # type: ignore


@dataclass
class ConnectionsEvent(EventInterface):
    """
    ConnectionsEvent class
    """

    type: str

    # type ignore required because mypy bug https://github.com/python/mypy/issues/6473
    EVENT_TYPE_NODE_CONNECTED: ClassVar[str] = f"{__qualname__}.node_connected"  # type: ignore
    EVENT_TYPE_NODE_DISCONNECTED: ClassVar[str] = f"{__qualname__}.node_disconnected"  # type: ignore
    EVENT_TYPE_INDEXER_CONNECTED: ClassVar[str] = f"{__qualname__}.indexer_connected"  # type: ignore
    EVENT_TYPE_INDEXER_DISCONNECTED: ClassVar[str] = f"{__qualname__}.indexer_disconnected"  # type: ignore


@dataclass
class UnitEvent(EventInterface):
    """
    UnitEvent class
    """

    type: str

    # type ignore required because mypy bug https://github.com/python/mypy/issues/6473
    EVENT_TYPE_CHANGED: ClassVar[str] = f"{__qualname__}.changed"  # type: ignore


# todo: enhance this event with from and to addresses
@dataclass
class TransferEvent(EventInterface):
    """
    TransferEvent class
    """

    type: str

    # type ignore required because mypy bug https://github.com/python/mypy/issues/6473
    EVENT_TYPE_SENT: ClassVar[str] = f"{__qualname__}.sent"  # type: ignore


@dataclass
class LastTransferEvent(EventInterface):
    """
    LastTransferEvent class
    """

    type: str
    address: str
    transfer: Transfer

    # type ignore required because mypy bug https://github.com/python/mypy/issues/6473
    EVENT_TYPE_LAST_TRANSFER_CHANGED: ClassVar[str] = f"{__qualname__}.sent"  # type: ignore
