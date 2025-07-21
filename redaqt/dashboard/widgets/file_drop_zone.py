# redaqt/dashboard/widgets/file_drop_zone.py

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QDragEnterEvent, QDragLeaveEvent, QDropEvent

from redaqt.theme.context import ThemeContext


class FileDropZone(QWidget):
    fileDropped = Signal(str)

    def __init__(self, theme_context: ThemeContext, parent=None):
        super().__init__(parent)
        self.theme_context = theme_context
        self.theme         = theme_context.theme
        self.colors        = theme_context.colors

        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._setup_ui()
        self._update_style(hover=False)

        if parent:
            parent.setAcceptDrops(True)
            parent.installEventFilter(self)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel("Drop file or folder here", alignment=Qt.AlignCenter)
        self.title_label.setAttribute(Qt.WA_StyledBackground, True)
        layout.addWidget(self.title_label)

    def _update_style(self, *, hover: bool):
        if hover:
            border_color = self.colors.get("accent", "#9B51E0")
            border_width = 4
        else:
            if self.theme == "light":
                base = self.colors.get("secondary", "#6083C5")
                border_color = f"rgba({int(base[1:3],16)}, {int(base[3:5],16)}, {int(base[5:7],16)}, 0.5)"
            else:
                fg = self.colors.get("foreground", "#DEE5E7")
                border_color = f"rgba({int(fg[1:3],16)}, {int(fg[3:5],16)}, {int(fg[5:7],16)}, 0.5)"
            border_width = 2

        text_color = self.colors.get("file_foreground",
                                     self.colors.get("foreground", "#000000"))
        self.title_label.setStyleSheet(f"color: {text_color}; background: transparent;")

        self.setStyleSheet(f"""
            QWidget {{
                background: transparent;
                border: {border_width}px solid {border_color};
                border-radius: 7px;
            }}
        """)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._update_style(hover=True)
        else:
            event.ignore()

    def dragLeaveEvent(self, event: QDragLeaveEvent):
        self._update_style(hover=False)
        event.accept()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            path_str = urls[0].toLocalFile()
            p = Path(path_str)

            if p.is_dir():
                files = [str(child) for child in p.iterdir() if child.is_file()]
            else:
                files = [str(p)]

            if files:
                self.fileDropped.emit(files[0])

                if p.is_file() and p.suffix.lower() == ".epf":
                    if self.parent() and hasattr(self.parent(), "window"):
                        main_window = self.window()
                        if hasattr(main_window, "on_item_selected") and hasattr(main_window, "access_page"):
                            main_window.on_item_selected("Access Flow")
                            main_window.access_page.process_protected_document(str(p))
                else:
                    if self.parent() and hasattr(self.parent(), "window"):
                        main_window = self.window()
                        if hasattr(main_window, "on_item_selected") and hasattr(main_window, "protection_page"):
                            main_window.on_item_selected("Protection Flow")
                            main_window.protection_page.show_for_paths(files)

        event.acceptProposedAction()
        self._update_style(hover=False)

    def eventFilter(self, source, event):
        if event.type() == QEvent.DragEnter:
            return self.dragEnterEvent(event) or True
        elif event.type() == QEvent.DragLeave:
            return self.dragLeaveEvent(event) or True
        elif event.type() == QEvent.Drop:
            return self.dropEvent(event) or True
        return super().eventFilter(source, event)