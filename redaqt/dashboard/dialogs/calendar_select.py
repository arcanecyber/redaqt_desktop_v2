# redaqt/dashboard/dialogs/calendar_select.py

from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QHBoxLayout,
    QComboBox, QSizePolicy, QCalendarWidget, QMessageBox
)
from PySide6.QtCore import QDateTime, Qt
from PySide6.QtGui import QTextCharFormat, QColor

from redaqt.ui.button import RedaQtButton


class CalendarSelectDialog(QDialog):
    def __init__(self, smart_policy: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Secure Document with Date Policy")
        self.setMinimumWidth(400)

        self.smart_policy = smart_policy  # Save policy for validation
        self.selected_datetime = None

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        self.title_label = QLabel(smart_policy)
        self.title_label.setStyleSheet("font-size: 14px; font-weight: normal;")
        layout.addWidget(self.title_label)

        # Calendar widget
        self.calendar = QCalendarWidget()
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)

        # Style weekdays and weekends
        weekend_fmt = QTextCharFormat()
        weekend_fmt.setForeground(QColor("#4f8dff"))

        weekday_fmt = QTextCharFormat()
        weekday_fmt.setForeground(QColor("#ffffff"))

        for day in [Qt.Monday, Qt.Tuesday, Qt.Wednesday, Qt.Thursday, Qt.Friday]:
            self.calendar.setWeekdayTextFormat(day, weekday_fmt)

        self.calendar.setWeekdayTextFormat(Qt.Saturday, weekend_fmt)
        self.calendar.setWeekdayTextFormat(Qt.Sunday, weekend_fmt)

        layout.addWidget(self.calendar)

        # Time selection layout
        time_layout = QHBoxLayout()

        h_label = QLabel("Hour")
        h_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        time_layout.addWidget(h_label)

        self.hour_selector = QComboBox()
        self.hour_selector.setMinimumWidth(70)
        self.hour_selector.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        for h in range(1, 13):
            self.hour_selector.addItem(f"{h:02d}")
        time_layout.addWidget(self.hour_selector, 0, Qt.AlignLeft)

        m_label = QLabel("Minute")
        m_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        time_layout.addWidget(m_label)

        self.minute_selector = QComboBox()
        self.minute_selector.setMinimumWidth(80)
        self.minute_selector.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        for m in range(0, 60, 5):
            self.minute_selector.addItem(f"{m:02d}")
        time_layout.addWidget(self.minute_selector, 0, Qt.AlignLeft)

        self.ampm_selector = QComboBox()
        self.ampm_selector.setMinimumWidth(80)
        self.ampm_selector.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.ampm_selector.addItems(["AM", "PM"])
        time_layout.addWidget(self.ampm_selector, 0, Qt.AlignRight)

        layout.addLayout(time_layout)

        # Buttons
        button_layout = QHBoxLayout()
        cancel_button = RedaQtButton("Cancel", parent=self)
        accept_button = RedaQtButton("Accept", parent=self)

        cancel_button.clicked.connect(self._on_cancel)
        accept_button.clicked.connect(self._on_accept)

        button_layout.addWidget(cancel_button, alignment=Qt.AlignLeft)
        button_layout.addWidget(accept_button, alignment=Qt.AlignRight)
        layout.addLayout(button_layout)

        # Apply fixed dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                font-size: 14px;
                color: #ffffff;
            }
            QComboBox {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px;
            }
        """)

    def _on_accept(self):
        selected_date = self.calendar.selectedDate()
        hour = int(self.hour_selector.currentText())
        minute = int(self.minute_selector.currentText())
        ampm = self.ampm_selector.currentText()

        if ampm == "PM" and hour != 12:
            hour += 12
        elif ampm == "AM" and hour == 12:
            hour = 0

        try:
            dt = datetime(
                selected_date.year(),
                selected_date.month(),
                selected_date.day(),
                hour,
                minute
            )
            now = datetime.now()

            # Validation for "do_not_open_after"
            if "do_not_open_after" in self.smart_policy.lower() and dt <= now:
                QMessageBox.warning(self, "Invalid Time", "Please select a future date and time.")
                return

            self.selected_datetime = dt.isoformat()
            self.accept()
        except ValueError:
            self.selected_datetime = None
            self.reject()

    def _on_cancel(self):
        self.selected_datetime = None
        self.reject()

    def get_selected_datetime(self) -> str | None:
        return self.selected_datetime