import logging
import sys
from os import device_encoding
from pathlib import Path

from PyQt5.QtCore import QDateTime
from PyQt5.QtCore import QMessageLogContext
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QtCriticalMsg
from PyQt5.QtCore import QtDebugMsg
from PyQt5.QtCore import QtFatalMsg
from PyQt5.QtCore import QtInfoMsg
from PyQt5.QtCore import QtMsgType
from PyQt5.QtCore import QtWarningMsg
from PyQt5.QtCore import qInstallMessageHandler
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QDateTimeEdit
from PyQt5.QtWidgets import QDial
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QRadioButton
from PyQt5.QtWidgets import QScrollBar
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QSlider
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtWidgets import QStyleFactory
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from ..input import InputDevices
from ..input import panasonic_keyboard_device
from ..util import logger


def qt_log_handler(msg_type: QtMsgType, msg_context: QMessageLogContext, msg: str | None) -> None:
    level = logging.DEBUG
    abort = False
    context = False
    if msg_type == QtFatalMsg:
        level = logging.CRITICAL
        abort = True
        context = True
    elif msg_type == QtCriticalMsg:
        level = logging.CRITICAL
        context = True
    elif msg_type == QtWarningMsg:
        level = logging.WARNING
    elif msg_type == QtInfoMsg:
        level = logging.INFO
    elif msg_type == QtDebugMsg:
        pass  # this is the default case
    else:
        level = logging.ERROR
        abort = True
        context = True
    if context:
        context_attributes = {k: getattr(msg_context, k, None) for k in ("category", "file", "function", "line")}
        msg = f"{context_attributes}: {msg}"
    logger.log(level, msg)
    if abort:
        sys.exit(1)


qInstallMessageHandler(qt_log_handler)


class PanasonicKeyboardWindow(QDialog):
    def __init__(self, parent=None, proc_input_file: Path | None = None):
        super(PanasonicKeyboardWindow, self).__init__(parent)

        self.devices = InputDevices.load(proc_input_file)
        device_combo_box = QComboBox()
        device_combo_box.addItems(map(lambda d: d.name, self.devices.devices))
        self.panasonic_device = panasonic_keyboard_device(self.devices)
        if self.panasonic_device is not None:
            device_combo_box.setCurrentText(self.panasonic_device.name)
        device_label = QLabel("&Device:")
        device_label.setBuddy(device_combo_box)

        self.create_top_left_group_box()
        self.create_top_right_group_box()
        self.create_bottom_left_tab_widget()
        self.create_bottom_right_group_box()

        top_layout = QHBoxLayout()
        top_layout.addWidget(device_label)
        top_layout.addWidget(device_combo_box)
        top_layout.addStretch(1)

        main_layout = QGridLayout()
        main_layout.addLayout(top_layout, 0, 0, 1, 2)
        main_layout.addWidget(self.top_left_group_box, 1, 0)
        main_layout.addWidget(self.top_right_group_box, 1, 1)
        main_layout.addWidget(self.bottom_left_tab_widget, 2, 0)
        main_layout.addWidget(self.bottom_right_group_box, 2, 1)
        main_layout.setRowStretch(1, 1)
        main_layout.setRowStretch(2, 1)
        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 1)
        self.setLayout(main_layout)

        self.change_style("Fusion")

        self.setWindowTitle("Panasonic Keyboard Selector")

    def change_style(self, style_name):
        QApplication.setStyle(QStyleFactory.create(style_name))

    def create_top_left_group_box(self):
        self.top_left_group_box = QGroupBox("Group 1")

        radio_button1 = QRadioButton("Radio button 1")
        radio_button2 = QRadioButton("Radio button 2")
        radio_button3 = QRadioButton("Radio button 3")
        radio_button1.setChecked(True)

        check_box = QCheckBox("Tri-state check box")
        check_box.setTristate(True)
        check_box.setCheckState(Qt.CheckState.PartiallyChecked)

        layout = QVBoxLayout()
        layout.addWidget(radio_button1)
        layout.addWidget(radio_button2)
        layout.addWidget(radio_button3)
        layout.addWidget(check_box)
        layout.addStretch(1)
        self.top_left_group_box.setLayout(layout)

    def create_top_right_group_box(self):
        self.top_right_group_box = QGroupBox("Group 2")

        default_push_button = QPushButton("Default Push Button")
        default_push_button.setDefault(True)

        toggle_push_button = QPushButton("Toggle Push Button")
        toggle_push_button.setCheckable(True)
        toggle_push_button.setChecked(True)

        flat_push_button = QPushButton("Flat Push Button")
        flat_push_button.setFlat(True)

        layout = QVBoxLayout()
        layout.addWidget(default_push_button)
        layout.addWidget(toggle_push_button)
        layout.addWidget(flat_push_button)
        layout.addStretch(1)
        self.top_right_group_box.setLayout(layout)

    def create_bottom_left_tab_widget(self):
        self.bottom_left_tab_widget = QTabWidget()
        self.bottom_left_tab_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Ignored)

        tab1 = QWidget()
        table_widget = QTableWidget(10, 10)

        tab1hbox = QHBoxLayout()
        tab1hbox.setContentsMargins(5, 5, 5, 5)
        tab1hbox.addWidget(table_widget)
        tab1.setLayout(tab1hbox)

        tab2 = QWidget()
        text_edit = QTextEdit()

        text_edit.setPlainText(
            "Twinkle, twinkle, little star,\n"
            "How I wonder what you are.\n"
            "Up above the world so high,\n"
            "Like a diamond in the sky.\n"
            "Twinkle, twinkle, little star,\n"
            "How I wonder what you are!\n"
        )

        tab2hbox = QHBoxLayout()
        tab2hbox.setContentsMargins(5, 5, 5, 5)
        tab2hbox.addWidget(text_edit)
        tab2.setLayout(tab2hbox)

        self.bottom_left_tab_widget.addTab(tab1, "&Table")
        self.bottom_left_tab_widget.addTab(tab2, "Text &Edit")

    def create_bottom_right_group_box(self):
        self.bottom_right_group_box = QGroupBox("Group 3")
        self.bottom_right_group_box.setCheckable(True)
        self.bottom_right_group_box.setChecked(True)

        line_edit = QLineEdit("s3cRe7")
        line_edit.setEchoMode(QLineEdit.EchoMode.Password)

        spin_box = QSpinBox(self.bottom_right_group_box)
        spin_box.setValue(50)

        date_time_edit = QDateTimeEdit(self.bottom_right_group_box)
        date_time_edit.setDateTime(QDateTime.currentDateTime())

        slider = QSlider(Qt.Orientation.Horizontal, self.bottom_right_group_box)
        slider.setValue(40)

        scroll_bar = QScrollBar(Qt.Orientation.Horizontal, self.bottom_right_group_box)
        scroll_bar.setValue(60)

        dial = QDial(self.bottom_right_group_box)
        dial.setValue(30)
        dial.setNotchesVisible(True)

        layout = QGridLayout()
        layout.addWidget(line_edit, 0, 0, 1, 2)
        layout.addWidget(spin_box, 1, 0, 1, 2)
        layout.addWidget(date_time_edit, 2, 0, 1, 2)
        layout.addWidget(slider, 3, 0)
        layout.addWidget(scroll_bar, 4, 0)
        layout.addWidget(dial, 3, 1, 2, 1)
        layout.setRowStretch(5, 1)
        self.bottom_right_group_box.setLayout(layout)


def gui(proc_input_file: Path | None):
    app = QApplication([])
    window = PanasonicKeyboardWindow(proc_input_file=proc_input_file)
    window.show()
    sys.exit(app.exec())
