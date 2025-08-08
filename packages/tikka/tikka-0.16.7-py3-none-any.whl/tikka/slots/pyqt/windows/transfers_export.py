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
from pathlib import Path
from typing import Optional

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QDialog, QFileDialog, QWidget

from tikka.domains.application import Application
from tikka.slots.pyqt.entities.constants import (
    TRANSFERS_EXPORT_DEFAULT_DIRECTORY_PREFERENCES_KEY,
)
from tikka.slots.pyqt.resources.gui.windows.transfers_export_rc import (
    Ui_transfersExportDialog,
)


class TransfersExportWindow(QDialog, Ui_transfersExportDialog):
    """
    TransfersExportWindow class
    """

    MIN_PERIOD_IN_WEEKS = 4
    MAX_PERIOD_IN_WEEKS = 104

    def __init__(
        self, application: Application, address: str, parent: Optional[QWidget] = None
    ):
        """
        Init transfers export window instance

        :param application: Application instance
        :param address: Account address
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self._ = self.application.translator.gettext
        self.address = address

        # buttons
        self.buttonBox.accepted.connect(self.on_accepted_button)
        self.buttonBox.rejected.connect(self.close)
        self.fromCalendarWidget.selectionChanged.connect(self.update_date_constraints)
        self.toCalendarWidget.selectionChanged.connect(self.update_date_constraints)
        self.todayButton.clicked.connect(self.init_calendar_limits)
        self.init_calendar_limits()

    def init_calendar_limits(self):
        """
        Définit les dates minimales et maximales autorisées pour les calendriers,
        en se basant sur la période maximale définie.
        """
        today = QDate.currentDate()
        default_min_date = today.addDays(-self.MIN_PERIOD_IN_WEEKS * 7)

        # Définir la plage de dates pour le calendrier "from"
        # self.fromCalendarWidget.setDateRange(max_min_date, today)
        self.fromCalendarWidget.setSelectedDate(default_min_date)

        # Définir la plage de dates pour le calendrier "to"
        # self.toCalendarWidget.setDateRange(min_date, max_date)
        self.toCalendarWidget.setSelectedDate(today)

    def update_date_constraints(self):
        """
        Update calendars with date constraints
        """
        from_date = self.fromCalendarWidget.selectedDate()
        to_date = self.toCalendarWidget.selectedDate()
        min_to_date = from_date.addDays(self.MIN_PERIOD_IN_WEEKS * 7)
        max_from_date = to_date.addDays(-self.MAX_PERIOD_IN_WEEKS * 7)

        if from_date > to_date:
            self.fromCalendarWidget.setSelectedDate(to_date)
        elif to_date < min_to_date:
            self.toCalendarWidget.setSelectedDate(min_to_date)

        max_to_date = from_date.addDays(self.MAX_PERIOD_IN_WEEKS * 7)

        if to_date > max_to_date:
            self.toCalendarWidget.setSelectedDate(max_to_date)
        if from_date < max_from_date:
            self.fromCalendarWidget.setSelectedDate(max_from_date)
        # self.toCalendarWidget.setMinimumDate(from_date)
        # self.toCalendarWidget.setMaximumDate(max_to_date)
        # self.fromCalendarWidget.setMaximumDate(to_date)

    def open_file_dialog(self) -> Optional[str]:
        """
        Open file dialog and return the selected filepath or None

        :return:
        """
        default_dir = self.application.repository.preferences.get(
            TRANSFERS_EXPORT_DEFAULT_DIRECTORY_PREFERENCES_KEY
        )
        if default_dir is not None:
            default_dir = str(Path(default_dir).expanduser().absolute())
        else:
            default_dir = ""

        result = QFileDialog.getSaveFileName(
            self, self._("Export file"), default_dir, "OFX Files (*.ofx)"
        )
        if result[0] == "":
            return None

        self.application.repository.preferences.set(
            TRANSFERS_EXPORT_DEFAULT_DIRECTORY_PREFERENCES_KEY,
            str(Path(result[0]).parent),
        )

        return result[0]

    def on_accepted_button(self) -> None:
        """
        Triggered when user click on ok button

        :return:
        """
        # open file dialog
        filepath = self.open_file_dialog()
        if filepath is not None:
            self.application.transfers.export_as_ofx(
                filepath,
                self.address,
                self.fromCalendarWidget.selectedDate().toPyDate(),
                self.toCalendarWidget.selectedDate().toPyDate(),
            )
        self.close()
