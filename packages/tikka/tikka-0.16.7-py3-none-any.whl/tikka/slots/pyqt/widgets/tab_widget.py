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

from PyQt5 import QtGui
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtWidgets import QAction, QMenu, QTabWidget

from tikka.domains.application import Application


class TabWidget(QTabWidget):
    def __init__(self, application: Application):
        """
        Init TabWidget instance

        :param application: Application instance
        """
        super().__init__()
        self.__context_menu_p = 0
        self.__init_last_removed_tab_info()
        self.__init_ui()
        self.application = application
        self._ = self.application.translator.gettext

    def __init_last_removed_tab_info(self):
        self.__last_removed_tab_idx = []
        self.__last_removed_tab_widget = []
        self.__last_removed_tab_title = []

    def __init_ui(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.__prepare_menu)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.remove_tab)

    def __prepare_menu(self, p):
        tab_idx = self.tabBar().tabAt(p)
        if tab_idx != -1:
            self.__context_menu_p = p
            close_tab_action = QAction(self._("Close Tab"))
            close_tab_action.triggered.connect(self.close_tab)

            close_all_tab_action = QAction(self._("Close All Tabs"))
            close_all_tab_action.triggered.connect(self.close_all_tab)

            close_other_tab_action = QAction(self._("Close Other Tabs"))
            close_other_tab_action.triggered.connect(self._(self.close_other_tab))

            close_tab_to_the_left_action = QAction(self._("Close Tabs to the Left"))
            close_tab_to_the_left_action.triggered.connect(self.close_tab_to_left)

            close_tab_to_the_right_action = QAction(self._("Close Tabs to the Right"))
            close_tab_to_the_right_action.triggered.connect(self.close_tab_to_right)

            reopen_closed_tab_action = QAction(self._("Reopen Closed Tab"))
            reopen_closed_tab_action.triggered.connect(self.reopen_closed_tab)

            menu = QMenu(self)
            menu.addAction(close_tab_action)
            menu.addAction(close_all_tab_action)
            menu.addAction(close_other_tab_action)
            menu.addAction(close_tab_to_the_left_action)
            menu.addAction(close_tab_to_the_right_action)
            menu.addAction(reopen_closed_tab_action)
            menu.exec(self.mapToGlobal(p))

    def remove_tab(self, idx):
        self.__save_last_removed_tab_info(idx)
        # return super().removeTab(idx)

    # def removeTab(self, idx):
    #     return super().removeTab(idx)

    def __save_last_removed_tab_info(self, idx):
        self.__last_removed_tab_idx.append(idx)
        self.__last_removed_tab_widget.append(self.widget(idx))
        self.__last_removed_tab_title.append(self.tabText(idx))

    def keyPressEvent(self, e):
        if e.modifiers() & Qt.AltModifier and e.key() == Qt.Key_Left:
            self.setCurrentIndex(self.currentIndex() - 1)
        elif e.modifiers() & Qt.AltModifier and e.key() == Qt.Key_Right:
            self.setCurrentIndex(self.currentIndex() + 1)
        elif e.modifiers() & Qt.ControlModifier and e.key() == Qt.Key_F4:
            self.close_tab()
        return super().keyPressEvent(e)

    def mouseReleaseEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == Qt.MiddleButton:
            self.close_tab()
        return super().mouseReleaseEvent(e)

    def close_tab(self):
        if isinstance(self.__context_menu_p, QPoint):
            tab_idx = self.tabBar().tabAt(self.__context_menu_p)
            self.remove_tab(tab_idx)
            self.__context_menu_p = 0
        else:
            self.remove_tab(self.currentIndex())

    def close_all_tab(self):
        self.clear()

    def close_other_tab(self):
        if isinstance(self.__context_menu_p, QPoint):
            tab_idx = self.tabBar().tabAt(self.__context_menu_p)
            self.__remove_tab_from_left_to(tab_idx)
            tab_idx = 0
            self.setCurrentIndex(tab_idx)
            self.__remove_tab_from_right_to(tab_idx)

    def close_tab_to_left(self):
        if isinstance(self.__context_menu_p, QPoint):
            tab_idx = self.tabBar().tabAt(self.__context_menu_p)
            self.__remove_tab_from_left_to(tab_idx)

    def __remove_tab_from_left_to(self, idx):
        for i in range(idx - 1, -1, -1):
            self.remove_tab(i)

    def __remove_tab_from_right_to(self, idx):
        for i in range(self.count() - 1, idx, -1):
            self.remove_tab(i)

    def close_tab_to_right(self):
        if isinstance(self.__context_menu_p, QPoint):
            tab_idx = self.tabBar().tabAt(self.__context_menu_p)
            self.__remove_tab_from_right_to(tab_idx)

    def reopen_closed_tab(self):
        # todo enable/disable action dynamically by existence of closed tab
        if len(self.__last_removed_tab_idx) > 0:
            for i in range(len(self.__last_removed_tab_idx) - 1, -1, -1):
                self.insertTab(
                    self.__last_removed_tab_idx[i],
                    self.__last_removed_tab_widget[i],
                    self.__last_removed_tab_title[i],
                )
            self.setCurrentIndex(self.__last_removed_tab_idx[-1])
            self.__init_last_removed_tab_info()
