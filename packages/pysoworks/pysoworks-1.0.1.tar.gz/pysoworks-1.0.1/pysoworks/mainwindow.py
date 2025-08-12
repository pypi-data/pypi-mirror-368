# This Python file uses the following encoding: utf-8
import sys
import logging
from typing import List, Dict
import json
import pkgutil
import os


from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import (
    Qt,
    QtMsgType,
    qInstallMessageHandler,
    QStandardPaths,
    QLocale
)
from PySide6.QtGui import QIcon, QGuiApplication, QAction

import qtinter
from pathlib import Path
import PySide6QtAds as QtAds
import qtass
from rich.traceback import install as install_rich_traceback
from rich.logging import RichHandler

from pysoworks.nv200widget import NV200Widget
from pysoworks.spiboxwidget import SpiBoxWidget
from pysoworks.action_manager import ActionManager, MenuID, action_manager
from pysoworks.style_manager import StyleManager, style_manager
from pysoworks.settings_manager import SettingsContext


def qt_message_handler(mode, context, message):
    if mode == QtMsgType.QtDebugMsg:
        print(f"[QtDebug] {message}")
    elif mode == QtMsgType.QtInfoMsg:
        print(f"[QtInfo] {message}")
    elif mode == QtMsgType.QtWarningMsg:
        print(f"[QtWarning] {message}")
    elif mode == QtMsgType.QtCriticalMsg:
        print(f"[QtCritical] {message}")
    elif mode == QtMsgType.QtFatalMsg:
        print(f"[QtFatal] {message}")

qInstallMessageHandler(qt_message_handler)


# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from pysoworks.ui_mainwindow import Ui_MainWindow



class MainWindow(QMainWindow):
    """
    Main application window for the PySoWorks UI, providing asynchronous device discovery, connection, and control features.
    Attributes:
        _device (DeviceClient): The currently connected device client, or None if not connected.
        _recorder (DataRecorder): The data recorder associated with the connected device, or None if not initialized
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        ui = self.ui
        ui.setupUi(self)

        self.init_action_manager() 

        # Create the dock manager. Because the parent parameter is a QMainWindow
        # the dock manager registers itself as the central widget.
        self.dock_manager = QtAds.CDockManager(self)
        self.dock_manager.setStyleSheet("")
        ui.actionNv200View.triggered.connect(self.add_nv200_view)
        ui.actionSpiBoxView.triggered.connect(self.add_spibox_view)
        self.add_nv200_view()
        self.resize(1600, 900)  # Set initial size to 800x600

        self.init_style_controls()


    def init_action_manager(self):
        """
        Initializes the ActionManager and registers the main window.
        This method should be called after the main window is set up.
        """
        action_manager.register_main_window(self)

        # Register menus
        action_manager.register_menu(MenuID.FILE, self.ui.menuFile)
        action_manager.register_menu(MenuID.VIEW, self.ui.menuView)
        action_manager.register_menu(MenuID.HELP, self.ui.menuHelp)
        action_manager.add_action_to_menu(MenuID.FILE, QAction("Exit"))


    def init_style_controls(self):
        """
        Initializes the style controls for the main window.
        This method sets up the UI elements related to styling and appearance.
        """
        menu = self.ui.menuView
        menu.addSeparator()
        a = self.light_theme_action = QAction("Light Theme", self)
        a.setCheckable(True)
        a.setChecked(not style_manager.style.is_current_theme_dark())
        menu.addAction(a)
        a.triggered.connect(style_manager.set_light_theme)
        

    def add_view(self, widget_class, title):
        """
        Adds a new view to the main window.
        :param widget_class: The class of the widget to be added.
        :param title: The title of the dock widget.
        """
        widget = widget_class(self)
        dock_widget = QtAds.CDockWidget(title)
        dock_widget.setWidget(widget)
        self.dock_manager.addDockWidget(QtAds.RightDockWidgetArea, dock_widget)
        widget.status_message.connect(self.show_status_message)


    def add_nv200_view(self):
        """
        Adds a new NV200 view to the main window.
        """
        self.add_view(NV200Widget, "NV200")

    def add_spibox_view(self):
        """
        Adds a new SpiBox view to the main window.
        """
        self.add_view(SpiBoxWidget, "SpiBox")


    def show_status_message(self, message: str, timeout: int | None = 4000):
        """
        Displays a status message in the status bar.
        :param message: The message to display.
        """
        if message.startswith("Error"):
            self.statusBar().setStyleSheet("QStatusBar { color: red; }")
        else:
            self.statusBar().setStyleSheet("")
        self.statusBar().showMessage(message, timeout)

   
def setup_logging():
    """
    Configures the logging settings for the application.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s.%(msecs)03d | %(name)-25s | %(message)s',
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, )]
    )
    install_rich_traceback(show_locals=True)  

    logging.getLogger("nv200.device_discovery").setLevel(logging.DEBUG)
    logging.getLogger("nv200.transport_protocols").setLevel(logging.DEBUG)         
    logging.getLogger("nv200.serial_protocol").setLevel(logging.DEBUG)    
    logging.getLogger("nv200.device_base").setLevel(logging.DEBUG)     


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = ''
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = Path(__file__).resolve().parent.parent
    print(f"base_path: {base_path}")
    return os.path.join(base_path, relative_path)


def main():
    """
    Initializes and runs the main application window.
    """
    QLocale.setDefault(QLocale(QLocale.English, QLocale.UnitedStates))
    setup_logging()
    QGuiApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    QGuiApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    QApplication.setDesktopSettingsAware(True)

    QApplication.setEffectEnabled(Qt.UIEffect.UI_AnimateMenu, False)
    QApplication.setEffectEnabled(Qt.UIEffect.UI_AnimateCombo, False)

    app = QApplication(sys.argv)
    app.setApplicationName('PySoWorks')
    app.setApplicationDisplayName('PySoWorks')
    app.setOrganizationName('piezosystem jena')
    app.setOrganizationDomain('piezosystem.com')
    app_path = Path(__file__).resolve().parent
    print(f"Application Path: {app_path}")
    app.setWindowIcon(QIcon(resource_path('pysoworks/assets/app_icon.ico')))
    style_manager.load_theme_from_settings()

    widget = MainWindow()
    widget.show()
    widget.setWindowTitle('PySoWorks')

    style_manager.notify_application()

    with qtinter.using_asyncio_from_qt():
        app.exec()
