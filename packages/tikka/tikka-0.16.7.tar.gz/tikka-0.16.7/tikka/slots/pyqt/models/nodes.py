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

from typing import List, Optional

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant

from tikka.domains.application import Application
from tikka.domains.entities.node import Node
from tikka.interfaces.adapters.repository.nodes import NodesRepositoryInterface
from tikka.slots.pyqt.entities.constants import (
    NODES_TABLE_SORT_COLUMN_PREFERENCES_KEY,
    NODES_TABLE_SORT_ORDER_PREFERENCES_KEY,
)


class NodesTableModel(QAbstractTableModel):
    """
    NodesTableModel class that drives the population of tabular display
    """

    def __init__(self, application: Application):
        super().__init__()

        self.application = application
        self._ = self.application.translator.gettext

        self.headers = [
            self._("Url"),
            self._("Software"),
            self._("Version"),
            self._("Peer ID"),
            self._("Unsafe API"),
        ]

        self.column_types = [
            NodesRepositoryInterface.COLUMN_URL,
            NodesRepositoryInterface.COLUMN_SOFTWARE,
            NodesRepositoryInterface.COLUMN_SOFTWARE_VERSION,
            NodesRepositoryInterface.COLUMN_PEER_ID,
            NodesRepositoryInterface.COLUMN_UNSAFE_API_EXPOSED,
        ]
        self.sort_order_types = [
            NodesRepositoryInterface.SORT_ORDER_ASCENDING,
            NodesRepositoryInterface.SORT_ORDER_DESCENDING,
        ]

        self.nodes: List[Node] = []
        self.init_data()

    def init_data(self):
        """
        Fill data from repository

        :return:
        """
        pref_sort_column = self.application.repository.preferences.get(
            NODES_TABLE_SORT_COLUMN_PREFERENCES_KEY
        )
        if pref_sort_column is None:
            sort_column = NodesRepositoryInterface.COLUMN_URL
        else:
            sort_column = self.column_types[int(pref_sort_column)]

        pref_sort_order = self.application.repository.preferences.get(
            NODES_TABLE_SORT_ORDER_PREFERENCES_KEY
        )
        if pref_sort_order is None:
            sort_order = NodesRepositoryInterface.SORT_ORDER_ASCENDING
        else:
            sort_order = self.sort_order_types[int(pref_sort_order)]
        self.beginResetModel()
        self.nodes = self.application.nodes.repository.list(
            sort_column=sort_column,
            sort_order=sort_order,
        )
        self.endResetModel()

    def sort(self, column: int, order: Optional[Qt.SortOrder] = None):
        """
        Triggered by Qt Signal Sort by column

        :param column: Index of sort column
        :param order: Qt.SortOrder flag
        :return:
        """
        if column > -1:
            self.application.repository.preferences.set(
                NODES_TABLE_SORT_COLUMN_PREFERENCES_KEY, str(column)
            )
            self.application.repository.preferences.set(
                NODES_TABLE_SORT_ORDER_PREFERENCES_KEY, str(order)
            )
        self.init_data()

    def rowCount(self, _: QModelIndex = QModelIndex()) -> int:
        """
        Return row count

        :param _: QModelIndex instance
        :return:
        """
        count = self.application.nodes.repository.count()
        if count == 0:
            return 0
        if count <= len(self.nodes):
            return count

        return len(self.nodes)

    def columnCount(self, _: QModelIndex = QModelIndex()) -> int:
        """
        Return column count (length of headers list)

        :param _: QModelIndex instance
        :return:
        """
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> QVariant:
        """
        Return data of cell for column index.column

        :param index: QModelIndex instance
        :param role: Item data role
        :return:
        """
        col = index.column()
        row = index.row()
        node = self.nodes[row]
        data = QVariant()
        if role == Qt.DisplayRole:
            if col == 0:
                data = QVariant(node.url)
            if col == 1:
                data = QVariant(node.software)
            if col == 2:
                data = QVariant(node.software_version)
            if col == 3:
                data = QVariant(node.peer_id)
            if col == 4:
                data = QVariant(
                    self._("Exposed") if node.unsafe_api_exposed is True else ""
                )
        return data

    def headerData(
        self, section: int, orientation: int, role: int = Qt.DisplayRole
    ) -> QVariant:
        """
        Return

        :param section: Headers column index
        :param orientation: Headers orientation
        :param role: Item role
        :return:
        """
        if role != Qt.DisplayRole:
            return QVariant()

        if orientation == Qt.Horizontal:
            return QVariant(self.headers[section])

        # return row number as vertical header
        return QVariant(int(section + 1))
