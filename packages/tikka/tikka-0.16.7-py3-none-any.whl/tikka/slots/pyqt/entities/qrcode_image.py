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

# Image class for QR code
from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPainter, QPixmap
from qrcode import QRCode
from qrcode.image.base import BaseImage


class QRCodeImage(BaseImage):

    # constructor
    def __init__(self, border, width, box_size, *args, **kwargs):

        # assigning border
        super().__init__(border, width, box_size, *args, **kwargs)
        self.border = border

        # assigning width
        self.width = width

        # assigning box size
        self.box_size = box_size

        # creating size
        size = (width + border * 2) * box_size

        # image
        self._image = QImage(size, size, QImage.Format_RGB16)

        # initial image as white
        self._image.fill(Qt.white)

    # pixmap method
    def pixmap(self):

        # returns image
        return QPixmap.fromImage(self._image)

    def drawrect_context(self, row: int, col: int, qr: QRCode):
        pass

    # drawrect method for drawing rectangle
    def drawrect(self, row, col):
        # creating painter object
        painter = QPainter(self._image)

        # drawing rectangle
        painter.fillRect(
            (col + self.border) * self.box_size,
            (row + self.border) * self.box_size,
            self.box_size,
            self.box_size,
            Qt.black,
        )

    def save(self, stream, kind=None):
        pass

    def new_image(self, **kwargs) -> Any:
        pass

    def process(self):
        pass
