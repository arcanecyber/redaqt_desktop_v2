# redaqt/dashboard/widgets/spinner.py

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QMovie
from PySide6.QtCore import Qt, QSize


class Spinner(QWidget):
    """
    A reusable spinner widget using an animated GIF and a label.
    Usage:
        spinner = Spinner("assets/animations/spinner.gif")
        layout.addWidget(spinner)
        spinner.start()
        ...
        spinner.stop()
    """

    def __init__(self, gif_path: str, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)

        self.label = QLabel("Processing Your Request", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: white; background: transparent; padding-bottom: 10px;")
        layout.addWidget(self.label)

        self.movie_label = QLabel(self)
        self.movie_label.setAlignment(Qt.AlignCenter)
        self.movie_label.setStyleSheet("background: transparent; border: none;")

        self.movie = QMovie(gif_path)
        self.movie.setScaledSize(QSize(150, 150))
        self.movie_label.setMovie(self.movie)

        layout.addWidget(self.movie_label)

    def start(self):
        self.show()
        self.movie.start()

    def stop(self):
        self.movie.stop()
        self.hide()