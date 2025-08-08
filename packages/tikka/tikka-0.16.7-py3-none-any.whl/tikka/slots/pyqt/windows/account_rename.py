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

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QDialog, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.account import Account
from tikka.domains.entities.constants import DATA_PATH
from tikka.slots.pyqt.entities.constants import ADDRESS_MONOSPACE_FONT_NAME
from tikka.slots.pyqt.resources.gui.windows.account_rename_rc import (
    Ui_AccountRenameDialog,
)


class AccountRenameWindow(QDialog, Ui_AccountRenameDialog):
    """
    AccountRenameWindow class
    """

    def __init__(
        self,
        application: Application,
        account: Account,
        parent: Optional[QWidget] = None,
    ):
        """
        Init rename account window

        :param application: Application instance
        :param account: Account instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self.account = account
        self._ = self.application.translator.gettext

        # populate fields
        monospace_font = QFont(ADDRESS_MONOSPACE_FONT_NAME)
        monospace_font.setStyleHint(QFont.Monospace)
        self.addressValueLabel.setFont(monospace_font)
        self.addressValueLabel.setText(self.account.address)
        self.nameLineEdit.setText(self.account.name)

        # events
        self.buttonBox.accepted.connect(self.on_accepted_button)

    def on_accepted_button(self) -> None:
        """
        Triggered when user click on ok button

        :return:
        """
        self.account.name = self.nameLineEdit.text().strip()
        if self.account.name == "":
            self.account.name = None
        self.application.accounts.update(self.account)


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    application_ = Application(DATA_PATH)
    account_ = Account("CUYYUnh7N49WZhs5DULkmqw5Zu5fwsRBmE5LLrUFRpgw", name="old name")
    AccountRenameWindow(application_, account_).exec_()
