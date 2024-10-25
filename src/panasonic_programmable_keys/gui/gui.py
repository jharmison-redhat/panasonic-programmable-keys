import logging
import sys
from pathlib import Path

from PyQt5.QtCore import QMessageLogContext
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QtCriticalMsg
from PyQt5.QtCore import QtDebugMsg
from PyQt5.QtCore import QtFatalMsg
from PyQt5.QtCore import QThread
from PyQt5.QtCore import QtInfoMsg
from PyQt5.QtCore import QtMsgType
from PyQt5.QtCore import QtWarningMsg
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import qInstallMessageHandler
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QStyleFactory
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from ..input import panasonic_keyboard_device
from ..input import yield_from
from ..input.models import InputDevices
from ..input.models import KeyPressEventType
from ..util import logger
from ..util import settings


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


class UpdateThread(QThread):
    received = pyqtSignal([str])

    def __init__(self, *args, proc_input_file: Path | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.proc_input_file = proc_input_file

    def run(self):
        for event in yield_from(self.proc_input_file):
            if event.type == KeyPressEventType.press:
                self.received.emit(event.descriptor.name)


class PanasonicKeyboardWindow(QDialog):
    def __init__(self, parent=None, proc_input_file: Path | None = None):
        super(PanasonicKeyboardWindow, self).__init__(parent)

        QApplication.setStyle(QStyleFactory.create("Fusion"))

        self.devices = InputDevices.load(proc_input_file)
        device_combo_box = QComboBox()
        device_combo_box.addItems(map(lambda d: d.name, self.devices.devices))
        self.panasonic_device = panasonic_keyboard_device(self.devices)
        if self.panasonic_device is not None:
            device_combo_box.setCurrentText(self.panasonic_device.name)
        device_label = QLabel(self.tr("&Device:"))
        device_label.setBuddy(device_combo_box)

        rescan_buttons = QPushButton("Re-scan Device Buttons")
        rescan_buttons.clicked.connect(self.popup_rescan_buttons)

        top_layout = QHBoxLayout()
        top_layout.addWidget(device_label)
        top_layout.addWidget(device_combo_box)
        top_layout.addWidget(rescan_buttons)
        top_layout.addStretch(1)

        main_layout = QGridLayout()
        main_layout.addLayout(top_layout, 0, 0, 1, Qt.AlignRight)

        self.setLayout(main_layout)

        self.create_macro_functions_box()

        self.setWindowTitle(self.tr("Panasonic Keyboard Selector"))

    def create_macro_functions_box(self):
        window_layout: QGridLayout = self.layout()  # type: ignore
        if getattr(self, "macro_functions_box", None) is not None:
            window_layout.removeWidget(self.macro_functions_box)
        self.macro_functions_box: QGroupBox = QGroupBox(self.tr("Macro Functions"))

        layout = QFormLayout()

        for row, enabled_key in enumerate(settings.keyboard.get("enabled_keys", [])):
            label = f"P{row + 1}"
            configured_function = settings.keyboard.get(enabled_key, False) or ""
            function_definition = QLineEdit(configured_function)
            function_definition.setProperty("key_name", enabled_key)
            function_definition.setClearButtonEnabled(True)
            logger.debug(
                f"Adding button for {label} targeting {enabled_key} preselected to '{function_definition.text()}'"
            )
            layout.addRow(label, function_definition)

        buttons = QHBoxLayout()

        reload = QPushButton(self.tr("&Reload"))
        reload.clicked.connect(settings.reload)
        reload.clicked.connect(self.create_macro_functions_box)
        buttons.addWidget(reload)

        save = QPushButton(self.tr("&Save"))
        save_menu = QMenu()
        save_pwd = QAction(self.tr("Save to &Working Directory"), self)
        save_pwd.triggered.connect(self.save)
        save_pwd.setShortcuts(QKeySequence.Save)
        save_menu.addAction(save_pwd)
        save_as = QAction(self.tr("Save &As"), self)
        save_as.triggered.connect(self.save_as)
        save_as.setShortcuts(QKeySequence.SaveAs)
        save_menu.addAction(save_as)
        save.setMenu(save_menu)
        buttons.addWidget(save)

        layout.addRow("", buttons)

        self.macro_functions_box.setLayout(layout)
        window_layout.addWidget(self.macro_functions_box, 1, 0)

    def popup_rescan_buttons(self):
        logger.debug("Rescan buttons")
        popup = QDialog(parent=self)
        popup.setWindowTitle("Re-scan Device Buttons")

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(popup.accept)
        button_box.rejected.connect(popup.reject)

        button_reading = QTextEdit()
        button_reading.setReadOnly(True)

        popup_layout = QVBoxLayout()
        popup_layout.addWidget(QLabel(self.tr("Press and release your programmable keys, one at a time, in order")))
        popup_layout.addWidget(button_reading)
        popup_layout.addWidget(button_box)
        popup.setLayout(popup_layout)

        update_button_reading = UpdateThread()
        update_button_reading.received.connect(button_reading.append)
        update_button_reading.start()

        popup.show()
        QApplication.processEvents()

        if not popup.exec():
            logger.warning("Not updating scanned buttons due to user choice")
            return None

        mapped_buttons = [b.strip() for b in button_reading.toPlainText().splitlines()]
        logger.debug(mapped_buttons)
        settings.keyboard["enabled_keys"] = mapped_buttons
        self.create_macro_functions_box()

    def save_as(self, _: bool) -> None:
        save_as = QFileDialog(parent=self)
        save_as.setNameFilter("Configuration Settings (*.toml)")
        save_as.setFileMode(QFileDialog.AnyFile)
        save_as.setOption(QFileDialog.ReadOnly, True)
        save_as.setOption(QFileDialog.HideNameFilterDetails, True)
        save_as.setOption(QFileDialog.DontConfirmOverwrite, True)
        selection = save_as.exec()
        logger.debug(f"User selected: {selection}")
        if selection:
            self.save(True, Path(save_as.selectedFiles()[0]))

    def save(self, _: bool, file: Path | None = None) -> None:
        if file is None:
            file = Path("config.toml")
        if file.exists():
            logger.warning(f"Path exists: {file}")
            warning = QDialog(parent=self)
            warning.setWindowTitle(f"Warning! Path exists: {file}")
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(warning.accept)
            button_box.rejected.connect(warning.reject)
            warning_layout = QVBoxLayout()
            warning_layout.addWidget(QLabel(self.tr("File exists, overwrite?")))
            warning_layout.addWidget(button_box)
            warning.setLayout(warning_layout)
            if not warning.exec():
                logger.warning("Not saving due to user choice")
                return None

        prev = {"keyboard": settings.keyboard.to_dict()}
        layout: QFormLayout = self.macro_functions_box.layout()  # type: ignore
        row_count = layout.rowCount() - 1  # One less to account for buttons
        _label: QWidget
        function_definition: QWidget
        for _label, function_definition in (
            (
                layout.itemAt(i * 2).widget(),
                layout.itemAt(i * 2 + 1).widget(),
            )
            for i in range(row_count)
        ):
            enabled_key = function_definition.property("key_name") or "KEY_UNDEFINED"
            if (
                enabled_key in settings.keyboard.get("enabled_keys", [])
                and callable(getattr(function_definition, "text", None))
            ):
                new_function = function_definition.text()  # type: ignore
                if new_function == "":
                    logger.debug(f"Unsetting the defined function for {enabled_key}")
                else:
                    logger.debug(f"Updating {enabled_key} to use {new_function}")
                prev["keyboard"][enabled_key] = new_function

        from dynaconf import loaders

        loaders.write(str(file), prev)
        # Load our new settings, in case they changed
        settings.reload()


def gui(proc_input_file: Path | None):
    app = QApplication([])
    window = PanasonicKeyboardWindow(proc_input_file=proc_input_file)
    window.show()
    sys.exit(app.exec())
