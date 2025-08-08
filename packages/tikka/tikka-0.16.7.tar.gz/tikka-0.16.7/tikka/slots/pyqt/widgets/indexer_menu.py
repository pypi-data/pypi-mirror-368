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

from PyQt5.QtWidgets import QApplication, QMenu, QMessageBox, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.constants import DATA_PATH
from tikka.domains.entities.events import IndexersEvent
from tikka.domains.entities.indexer import Indexer


class IndexerPopupMenu(QMenu):
    """
    IndexerPopupMenu class
    """

    def __init__(
        self,
        application: Application,
        indexer: Indexer,
        parent: Optional[QWidget] = None,
    ):
        """
        Init IndexerPopupMenu instance

        :param application: Application instance
        :param indexer: Indexer instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)

        self.application = application
        self.indexer = indexer
        self._ = self.application.translator.gettext

        # menu actions
        copy_url_to_clipboard_action = self.addAction(self._("Copy URL to clipboard"))
        copy_url_to_clipboard_action.triggered.connect(self.copy_url_to_clipboard)
        if (
            not self.indexer.url == self.application.indexers.get_current_url()
            and self.indexer.url
            not in self.application.currencies.get_entry_point_urls()["squid"]
        ):
            forget_indexer_action = self.addAction(self._("Forget server"))
            forget_indexer_action.triggered.connect(self.delete_indexer)

    def copy_url_to_clipboard(self):
        """
        Copy URL to clipboard

        :return:
        """
        clipboard = QApplication.clipboard()
        clipboard.setText(self.indexer.url)

    def delete_indexer(self):
        """
        Forget selected indexer and its entry point

        :return:
        """
        response_button = self.confirm_delete_indexer(self.indexer)
        if response_button == QMessageBox.Yes:
            self.application.indexers.delete(self.indexer.url)
            self.application.event_dispatcher.dispatch_event(
                IndexersEvent(IndexersEvent.EVENT_TYPE_LIST_CHANGED)
            )

    def confirm_delete_indexer(self, indexer: Indexer) -> QMessageBox.StandardButton:
        """
        Display confirm dialog and return response

        :param indexer: Indexer instance
        :return:
        """
        # display confirm dialog and get response
        custom_question = self._("Forget server {}?")
        return QMessageBox.question(
            self,
            self._("Forget server"),
            custom_question.format(indexer.url),
        )


if __name__ == "__main__":
    qapp = QApplication(sys.argv)

    application_ = Application(DATA_PATH)
    indexer_ = Indexer(
        "ws://indexer.url.com",
        999,
    )

    menu = IndexerPopupMenu(application_, indexer_)
    menu.exec_()

    sys.exit(qapp.exec_())
