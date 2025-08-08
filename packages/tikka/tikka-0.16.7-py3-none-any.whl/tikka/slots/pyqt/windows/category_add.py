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
import sys
from typing import Optional

from PyQt5.QtWidgets import QApplication, QDialog, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.constants import DATA_PATH
from tikka.slots.pyqt.resources.gui.windows.category_add_rc import Ui_addCategoryDialog


class CategoryAddWindow(QDialog, Ui_addCategoryDialog):
    """
    CategoryAddWindow class
    """

    def __init__(self, application: Application, parent: Optional[QWidget] = None):
        """
        Init add category window

        :param application: Application instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self._ = self.application.translator.gettext

        # init combo box
        self.parentComboBox.addItem(self._("None"), userData=None)
        for category in self.application.categories.list_all():
            self.parentComboBox.addItem(category.name, userData=category.id)

        # buttons
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)

        # events
        self.buttonBox.accepted.connect(self.on_accepted_button)
        self.nameValueLineEdit.textChanged.connect(self.on_name_line_edit_changed)
        self.buttonBox.rejected.connect(self.close)

    def on_name_line_edit_changed(self) -> None:
        """
        Triggered when the name line edit is changed

        :return:
        """
        name = self.nameValueLineEdit.text().strip()

        if name != "":
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(True)
        else:
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)

    def on_accepted_button(self) -> None:
        """
        Triggered when user click on ok button

        :return:
        """
        name = self.nameValueLineEdit.text().strip()
        if name == "":
            return None

        parent_id = self.parentComboBox.currentData()

        category = self.application.categories.create(name, parent_id)
        self.application.categories.add(category)

        return None


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    application_ = Application(DATA_PATH)
    CategoryAddWindow(application_).exec_()
