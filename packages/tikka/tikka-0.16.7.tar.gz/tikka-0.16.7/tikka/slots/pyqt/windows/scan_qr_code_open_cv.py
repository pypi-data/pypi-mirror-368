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
from typing import List, Optional

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QCloseEvent, QFont, QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout, QWidget
from scalecodec.utils.ss58 import is_valid_ss58_address

from tikka.domains.application import Application
from tikka.domains.entities.account import Account, AccountCryptoType
from tikka.domains.entities.constants import DATA_PATH
from tikka.domains.entities.events import AccountEvent
from tikka.libs import crypto_type
from tikka.libs.keypair import Keypair
from tikka.slots.pyqt.entities.constants import ADDRESS_MONOSPACE_FONT_NAME
from tikka.slots.pyqt.resources.gui.windows.scan_qrcode_rc import Ui_ScanQRCodeDialog


class QrScannerWidget(QWidget):
    """QrScannerWidget class"""

    def __init__(self, camera_index: int = 0, parent: Optional[QWidget] = None):
        """
        Init QrScannerWidget instance

        :param camera_index: Index of camera from OpenCV detector
        :param parent: Parent QWidget
        """
        super().__init__(parent)

        self.setLayout(QVBoxLayout(self))
        self.image_label = QLabel(self)
        self.setup_ui()

        self.camera_index = camera_index
        self.detected_data = None
        self.cap = None
        self.timer = QTimer(self)

        self.setup_camera()

    def setup_ui(self):
        """
        Setup GUI

        :return:
        """
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(self.image_label)

    def setup_camera(self):
        """
        Setup camera with OpenCV

        :return:
        """
        import cv2

        self.cap = cv2.VideoCapture(self.camera_index)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # ~30 FPS

    def update_frame(self):
        """
        Update Qt frame from OpenCV camera images

        :return:
        """
        import cv2

        ret, frame = self.cap.read()
        if not ret:
            return

        # Detect QR code
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(frame)

        if data and is_valid_ss58_address(data):
            self.detected_data = data
            self.timer.stop()
            self.parent().accept()  # Close parent QDialog

        # Display image
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(qt_image))

    def closeEvent(self, event: QCloseEvent):
        """
        Oberload CloseEvent

        :param event: QCloseEvent instance
        :return:
        """
        if self.cap is not None:
            self.cap.release()
        super().closeEvent(event)


class ScanQRCodeOpenCVWindow(QDialog, Ui_ScanQRCodeDialog):
    """
    ScanQRCodeOpenCVWindow class
    """

    display_crypto_type = {
        AccountCryptoType.ED25519: "ED25519",
        AccountCryptoType.SR25519: "SR25519",
    }

    def __init__(self, application: Application, parent: Optional[QWidget] = None):
        """
        Init scan qrcode OpenCV window

        :param application: Application instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self._ = self.application.translator.gettext

        self.scanner: Optional[QrScannerWidget] = None
        self.address: Optional[str] = None
        self.crypto_type = AccountCryptoType.ED25519

        # set monospace font to address field
        monospace_font = QFont(ADDRESS_MONOSPACE_FONT_NAME)
        monospace_font.setStyleHint(QFont.Monospace)
        self.addressValueLabel.setFont(monospace_font)

        # buttons
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)

        # events
        self.buttonBox.accepted.connect(self.on_accepted_button)
        self.buttonBox.rejected.connect(self.close)

        camera_index = self.get_available_camera_opencv_index()
        if camera_index is not None:
            self.start_qt_qr_scanner(camera_index)
        else:
            self.errorLabel.setText(self._("No camera available"))

    def start_qt_qr_scanner(self, camera_index: int):
        """
        Start OpenCV camera integrated in Qt

        :param camera_index: Index of camera
        :return:
        """
        self.scanner = QrScannerWidget(camera_index, self)
        self.layout().insertWidget(0, self.scanner)  # type: ignore

        # Hide useless elements during scan
        self.addressValueLabel.hide()
        self.keyTypeValueLabel.hide()
        # self.buttonBox.hide()

        if self.exec_() == QDialog.Accepted:
            self.address = self.scanner.detected_data
            if self.address is not None:
                self._show_result()
            else:
                self.errorLabel.setText(self._("QRCode Scanner canceled"))
        else:
            self.errorLabel.setText(self._("Scan canceled"))

    def _show_result(self):
        """
        Show scan result

        :return:
        """
        # self.scanner.hide()
        self.addressValueLabel.show()
        self.keyTypeValueLabel.show()
        # self.buttonBox.show()

        self.addressValueLabel.setText(self.address)
        self.errorLabel.setText("")
        self._detect_crypto_type(self.address)
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(True)

    def _detect_crypto_type(self, address: str):
        """
        :param address: Address scanned

        :return:
        """
        keypair = Keypair(address)
        try:
            result = crypto_type.is_valid_ed25519(keypair.public_key)
        except (AttributeError, AssertionError):
            result = False

        if result is True:
            self.crypto_type = AccountCryptoType.ED25519
            self.keyTypeValueLabel.setText(
                self.display_crypto_type[AccountCryptoType.ED25519]
            )
        else:
            try:
                result = crypto_type.is_valid_sr25519(keypair.public_key)
            except (AttributeError, AssertionError):
                result = False
            if result is True:
                self.crypto_type = AccountCryptoType.SR25519
                self.keyTypeValueLabel.setText(
                    self.display_crypto_type[AccountCryptoType.SR25519]
                )

    @staticmethod
    def get_available_camera_opencv_index() -> Optional[int]:
        """
        Return first available working camera index or None

        :return:
        """
        import cv2

        non_working_ports: List[int] = []
        dev_port = 0
        working_ports: List[int] = []
        available_ports: List[int] = []
        while len(non_working_ports) < 5:  # Stop after 5 non-working ports
            camera = cv2.VideoCapture(dev_port)
            if not camera.isOpened():
                non_working_ports.append(dev_port)
                logging.debug("Port %s is not working." % dev_port)
            else:
                is_reading, img = camera.read()
                width = camera.get(3)
                height = camera.get(4)
                if is_reading:
                    logging.debug(
                        "Camera %s is working and reads images (%s x %s)"
                        % (dev_port, width, height)
                    )
                    working_ports.append(dev_port)
                else:
                    logging.debug(
                        "Port %s for camera ( %s x %s) is present but does not reads."
                        % (dev_port, width, height)
                    )
                    available_ports.append(dev_port)
            dev_port += 1
            camera.release()

        return working_ports[0] if working_ports else None

    def on_accepted_button(self) -> None:
        """
        Triggered when user click on ok button

        :return:
        """
        if self.address is not None:
            account = self.application.accounts.get_by_address(self.address)
            if account is None:
                # create account instance
                account = Account(
                    self.address,
                    name=self._("Added from a QRCode"),
                    crypto_type=self.crypto_type,
                )
                # add instance in application
                self.application.accounts.add(account)
            else:
                # dispatch event
                event = AccountEvent(
                    AccountEvent.EVENT_TYPE_ADD,
                    account,
                )
                self.application.event_dispatcher.dispatch_event(event)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    qapp = QApplication(sys.argv)
    application_ = Application(DATA_PATH)
    window = ScanQRCodeOpenCVWindow(application_)
    if window.address is not None:
        # display window
        window.exec_()
