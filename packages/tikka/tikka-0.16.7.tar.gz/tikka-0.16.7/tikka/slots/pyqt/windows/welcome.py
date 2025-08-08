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

from PyQt5.QtCore import QMutex
from PyQt5.QtWidgets import QApplication, QDialog, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.constants import DATA_PATH
from tikka.slots.pyqt.resources.gui.windows.welcome_rc import Ui_WelcomeDialog
from tikka.slots.pyqt.windows.account_create import AccountCreateWindow
from tikka.slots.pyqt.windows.account_import import AccountImportWindow
from tikka.slots.pyqt.windows.v1_account_import import V1AccountImportWindow


class WelcomeWindow(QDialog, Ui_WelcomeDialog):
    """
    WelcomenWindow class
    """

    def __init__(self, application: Application, parent: Optional[QWidget] = None):
        """
        Init welcome window

        :param application: Application instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self._ = self.application.translator.gettext

        # events
        self.importV2Button.clicked.connect(self.on_import_v2_button_clicked)
        self.importV1Button.clicked.connect(self.on_import_v1_button_clicked)
        self.createButton.clicked.connect(self.on_create_button_clicked)
        self.continueButton.clicked.connect(self.on_continue_button_clicked)

    def on_import_v2_button_clicked(self):
        """
        Triggered when user click on import V2 account button

        :return:
        """
        window = AccountImportWindow(self.application, QMutex(), self.parentWidget())
        window.destroyed.connect(self.close)
        window.exec()

    def on_import_v1_button_clicked(self):
        """
        Triggered when user click on import V1 account button

        :return:
        """
        window = V1AccountImportWindow(self.application, QMutex(), self.parentWidget())
        window.destroyed.connect(self.close)
        window.exec()

    def on_create_button_clicked(self):
        """
        Triggered when user click on create account button

        :return:
        """
        window = AccountCreateWindow(self.application, self.parentWidget())
        window.destroyed.connect(self.close)
        window.exec()

    def on_continue_button_clicked(self):
        """
        Triggered when user click on continue button

        :return:
        """
        self.close()


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    application_ = Application(DATA_PATH)
    WelcomeWindow(application_).exec_()
