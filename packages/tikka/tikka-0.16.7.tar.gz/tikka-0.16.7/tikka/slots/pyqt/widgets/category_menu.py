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

import sys

from PyQt5.QtCore import QMutex
from PyQt5.QtWidgets import QApplication, QMenu, QMessageBox

from tikka.domains.application import Application
from tikka.domains.entities.category import Category
from tikka.domains.entities.constants import DATA_PATH

# if TYPE_CHECKING:
#     from tikka.slots.pyqt.widgets.account_tree import AccountTreeWidget


class CategoryPopupMenu(QMenu):
    """
    CategoryPopupMenu class
    """

    def __init__(
        self,
        application: Application,
        category: Category,
        mutex: QMutex,
        parent: AccountTreeWidget,
    ):
        """
        Init AccountPopupMenu instance

        :param application: Application instance
        :param category: Category instance
        :param mutex: QMutex instance
        :param parent: AccountTreeWidget instance
        """
        super().__init__(parent=parent)

        self._parent = parent
        self.application = application
        self.category = category
        self.mutex = mutex
        self._ = self.application.translator.gettext

        # menu actions
        rename_action = self.addAction(self._("Rename"))
        rename_action.triggered.connect(self.rename)
        add_sub_category_action = self.addAction(self._("Add sub-category"))
        add_sub_category_action.triggered.connect(self.add_sub_category)
        delete_category_action = self.addAction(self._("Delete category"))
        delete_category_action.triggered.connect(self.delete_category)

    def rename(self):
        """
        Set the current category in edit mode in tree view

        :return:
        """
        self._parent.rename_category()

    def add_sub_category(self):
        """
        Add new category in self.category

        :return:
        """
        self._parent.add_sub_category()

    def delete_category(self):
        """
        Add new category in self.category

        :return:
        """
        # display confirm dialog and get response
        button = QMessageBox.question(
            self,
            self._("Delete category"),
            self._(
                'Category content will be deleted locally. Do you really want to delete "{name}"?'
            ).format(name=self.category.name),
        )
        if button == QMessageBox.Yes:
            self.application.categories.delete(self.category.id)


if __name__ == "__main__":
    qapp = QApplication(sys.argv)

    application_ = Application(DATA_PATH)
    from tikka.slots.pyqt.widgets.account_tree import AccountTreeWidget

    categories = application_.categories.list(None)
    if len(categories) == 0:
        category_ = application_.categories.create("test category", None)
        application_.categories.add(category_)

    menu = CategoryPopupMenu(
        application_,
        application_.categories.list(None)[0],
        QMutex(),
        AccountTreeWidget(application_, QMutex()),
    )
    menu.exec_()

    sys.exit(qapp.exec_())
