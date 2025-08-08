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
import logging
import sys
from typing import Optional

from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.constants import DATA_PATH
from tikka.slots.pyqt.entities.constants import (
    NUMERIC_DISPLAY_COLOR_GREEN,
    NUMERIC_DISPLAY_COLOR_RED,
)
from tikka.slots.pyqt.resources.gui.widgets.account_transfer_row_rc import (
    Ui_AccountTransferRowWidget,
)


class AccountTransferRowWidget(QWidget, Ui_AccountTransferRowWidget):
    """
    AccountTransferRowWidget class
    """

    def __init__(
        self,
        account_address: str,
        account_name: str,
        identity_name: str,
        account_has_identity: bool,
        datetime: str,
        amount: str,
        comment: Optional[str] = None,
        comment_type: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Init AccountTransferRowWidget instance

        :param account_address: Account address label text
        :param account_name: Account name
        :param identity_name: Identity name label text
        :param account_has_identity: True if account name is identity name
        :param datetime: Datetime label text
        :param amount: Amount label text
        :param comment: Optional comment label text, default to None
        :param comment_type: Optional comment type, default to None
        :param parent: MainWindow instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        account_identity_name_color = "blue"
        amount_received_background_color = NUMERIC_DISPLAY_COLOR_GREEN
        amount_paid_background_color = NUMERIC_DISPLAY_COLOR_RED
        amount_color = "white"

        self.accountAddressValuelabel.setText(account_address)

        if account_has_identity:
            self.identityNameValueLabel.setStyleSheet(
                f'color: "{account_identity_name_color}"'
            )
            self.accountNameValueLabel.setText(
                f" - {account_name}" if account_name is not None else ""
            )
            self.identityNameValueLabel.setText(identity_name)
        else:
            self.identityNameValueLabel.setText(account_name)
            self.accountNameValueLabel.setText("")

        self.datetimeValueLabel.setText(datetime)

        # set amount style
        if amount[0] == "-":
            amount_background = amount_paid_background_color
        else:
            amount_background = amount_received_background_color

        self.amountValueLabel.setText(amount)
        self.amountValueLabel.setStyleSheet(
            f""" 
            color: {amount_color};
            border: 3px solid {amount_background};
            border-radius: 10%;
            background: {amount_background};
            """
        )

        if comment is None:
            self.commentValueLabel.setText("")
        else:
            if comment_type == "UNICODE":
                fonts = QFontDatabase()
                names = fonts.families()
                if "Symbola" in names:
                    self.commentValueLabel.setFont(QFont("Symbola"))
                elif "Emoji One" in names:
                    self.commentValueLabel.setFont(QFont("Emoji One"))

            # comment = "0 " * 73
            self.commentValueLabel.setText(comment)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    qapp = QApplication(sys.argv)

    application = Application(DATA_PATH)

    main_window = QMainWindow()
    main_window.show()
    account_address = "5D3r...8uI9"
    account_name = "Vince"
    identity_name = "vic#67"
    datetime = "01/02/2025 - 21:50:06"
    amount = "-257 G1"
    comment = "Merci pour les crêpes"
    widget = AccountTransferRowWidget(
        account_address,
        account_name,
        identity_name,
        True,
        datetime,
        amount,
        comment,
        "UNICODE",
        main_window,
    )
    main_window.setCentralWidget(widget)

    sys.exit(qapp.exec_())
