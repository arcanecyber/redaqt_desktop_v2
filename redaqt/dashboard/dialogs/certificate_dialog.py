# redaqt/dashboard/dialogs/certificate_dialog.py

import os
import sys
import subprocess
from pathlib import Path

import numpy as np
from PySide6.QtWidgets import (
    QDialog, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout
)
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, Signal

from redaqt.ui.button import RedaQtButton

ICON_PATHS = {
    "Gold": "assets/icon_cert_gold.png",
    "Blue": "assets/icon_cert_blue.png",
}


class CertificateDialog(QDialog):
    returnToFileSelection = Signal()

    def __init__(self, davinci_certificate: dict, davinci_certificate_image: np.ndarray, file_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Document Certificate")
        self.setFixedSize(500, 300)
        self.setStyleSheet("background-color: #2c2c2c; color: lightgray;")

        self.file_path = file_path
        cert_type = davinci_certificate.get("certificate_type", "Gold")
        cert_icon_path = ICON_PATHS.get(cert_type, ICON_PATHS["Gold"])
        cert_image_qpixmap = self.convert_ndarray_to_pixmap(davinci_certificate_image)

        # --- Certificate Icon + Description ---
        cert_icon = QLabel()
        cert_icon.setPixmap(QPixmap(cert_icon_path).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        cert_label = QLabel(f"This document has been certified with a {cert_type} label")
        cert_label.setStyleSheet("font-size: 14px; color: white;")

        top_row = QHBoxLayout()
        top_row.addWidget(cert_icon)
        top_row.addSpacing(10)
        top_row.addWidget(cert_label)
        top_row.addStretch()

        # --- Certificate Image + Data Grid ---
        cert_image_label = QLabel()
        cert_image_label.setPixmap(cert_image_qpixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        data_grid = QGridLayout()
        data_grid.setVerticalSpacing(10)
        data_grid.setHorizontalSpacing(10)

        labels = [
            "certificate id",
            "signing time",
            "expires after",
            "name",
            "organization",
        ]

        values = [
            davinci_certificate.get("child_certificate_id", ""),
            davinci_certificate.get("issuer", {}).get("signing_time", ""),
            davinci_certificate.get("issuer", {}).get("expires_after", ""),
            davinci_certificate.get("issuer", {}).get("name", ""),
            davinci_certificate.get("issuer", {}).get("organization", ""),
        ]

        for i, (label_text, value_text) in enumerate(zip(labels, values)):
            label = QLabel(label_text)
            label.setStyleSheet("color: #4FADEA;")
            value = QLabel(value_text)
            value.setStyleSheet("color: lightgray;")
            data_grid.addWidget(label, i, 0, alignment=Qt.AlignRight)
            data_grid.addWidget(value, i, 1, alignment=Qt.AlignLeft)

        middle_row = QHBoxLayout()
        middle_row.addWidget(cert_image_label)
        middle_row.addLayout(data_grid)

        # --- Buttons ---
        btn_close = RedaQtButton("Close", parent=self)
        btn_close.clicked.connect(self.handle_close)

        btn_open = RedaQtButton("Open File", parent=self)
        btn_open.clicked.connect(self.handle_open_file)

        button_row = QHBoxLayout()
        button_row.addWidget(btn_close)
        button_row.addStretch()
        button_row.addWidget(btn_open)

        # --- Final Layout ---
        layout = QVBoxLayout()
        layout.addLayout(top_row)
        layout.addSpacing(20)
        layout.addLayout(middle_row)
        layout.addStretch()
        layout.addLayout(button_row)
        self.setLayout(layout)

    def convert_ndarray_to_pixmap(self, image_array: np.ndarray) -> QPixmap:
        """Convert a numpy image array to QPixmap"""
        height, width, channels = image_array.shape
        bytes_per_line = channels * width
        image = QImage(image_array.data, width, height, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(image)

    def open_file(self):
        """Open the file in the system's default application (cross-platform)."""
        print(f"[INFO] Open file: {self.file_path}")

        try:
            if sys.platform.startswith("darwin"):  # macOS
                subprocess.run(["open", self.file_path], check=False)
            elif os.name == "nt":  # Windows
                os.startfile(self.file_path)
            elif os.name == "posix":  # Linux/Unix
                subprocess.run(["xdg-open", self.file_path], check=False)
            else:
                print("[ERROR] Unsupported OS platform for file opening.")
        except Exception as e:
            print(f"[ERROR] Failed to open file: {e}")

    def handle_close(self):
        """Close the dialog and return to file selection page."""
        self.returnToFileSelection.emit()
        self.reject()

    def handle_open_file(self):
        """Open file and return to file selection page."""
        self.open_file()
        self.returnToFileSelection.emit()
        self.accept()