# redaqt/dashboard/dialogs/cert_image_select.py

from pathlib import Path
import shutil

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog
)
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QPixmap, QDragEnterEvent, QDropEvent

from redaqt.ui.button import RedaQtButton


class CertImageSelectDialog(QDialog):
    """
    Modal dialog to preview and select a certificate image.
    - Accepts JPG image via drag-drop or file picker
    - Shows preview
    - Copies selected image to `data/`
    - Emits imagePathSelected(str) with the saved path in `data/`
    """
    imagePathSelected = Signal(str)

    def __init__(self, cert_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Certificate Image")
        self.setFixedSize(400, 400)
        self.setAcceptDrops(True)
        self.setStyleSheet("background-color: #2e2e2e;")

        self.selected_image_path: Path | None = None

        # ─── Main layout ─────────────────────────────────────────────
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(10)

        # Title
        title_lbl = QLabel("Current Certificate Image", self)
        title_lbl.setStyleSheet("color: #d3d3d3; font-size: 14px;")
        title_lbl.setAlignment(Qt.AlignHCenter)
        self.main_layout.addWidget(title_lbl)

        # Drop zone / image preview
        self.img_lbl = QLabel(self)
        self.img_lbl.setFixedSize(200, 200)
        self.img_lbl.setStyleSheet("border: 2px dashed #aaa; background-color: #444;")
        self.img_lbl.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.img_lbl, alignment=Qt.AlignHCenter)

        # Load initial image
        if cert_path and Path(cert_path).exists():
            self._load_image(Path(cert_path))

        self.main_layout.addStretch(1)

        # ─── Button Row ──────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.setSpacing(10)

        cancel_btn = RedaQtButton("Cancel")
        save_btn = RedaQtButton("Accept")

        cancel_btn.clicked.connect(self.reject)
        save_btn.clicked.connect(self._on_save)

        btn_row.addWidget(cancel_btn, alignment=Qt.AlignLeft)
        btn_row.addStretch(1)
        btn_row.addWidget(save_btn, alignment=Qt.AlignRight)

        self.main_layout.addLayout(btn_row)

        # Optional fallback click to select image
        self.img_lbl.mousePressEvent = self._on_img_click

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            if url.toLocalFile().lower().endswith(".jpg"):
                event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            path = Path(urls[0].toLocalFile())
            if path.suffix.lower() == ".jpg":
                self._load_image(path)

    def _on_img_click(self, _event):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select JPG Image", "", "Images (*.jpg)")
        if file_path:
            self._load_image(Path(file_path))

    def _load_image(self, path: Path):
        if path.exists() and path.suffix.lower() == ".jpg":
            pix = QPixmap(str(path))
            if not pix.isNull():
                scaled = pix.scaled(200, 200, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                self.img_lbl.setPixmap(scaled)
                self.selected_image_path = path

    def _on_save(self):
        if self.selected_image_path and self.selected_image_path.exists():
            destination_dir = Path("data")
            destination_dir.mkdir(exist_ok=True)
            dest_path = destination_dir / self.selected_image_path.name

            try:
                # Only copy if source and destination are different
                if self.selected_image_path.resolve() != dest_path.resolve():
                    shutil.copy2(self.selected_image_path, dest_path)
                # Emit signal with the correct path
                self.imagePathSelected.emit(str(dest_path))
            except Exception as e:
                print(f"[ERROR] Failed to copy image: {e}")
        self.accept()
