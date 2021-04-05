import sys
from os.path import abspath, dirname, join

from PySide2.QtQuick import QQuickView
from PySide2.QtCore import QObject, Signal, Slot, QThread, QTimer
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine

from driver_station import DriverStation

import structlog


class ViewModelMain(QObject):
    connectionChanged = Signal(bool, arguments=['connected'])
    connectionDetailsChanged = Signal(int, int, arguments=['sent', 'recieved'])

    def __init__(self, ds):
        self.logger = structlog.get_logger()
        self.ds = ds

        # Joystick manager task
        self.timer = QTimer()
        self.timer.timeout.connect(self.joystick_manager_tick)
        self.timer.start(20)  # Poll at 50 HZ

        # Communications Thread
        self.thread = QThread()

        # Connect Signals / Slots
        # When the thread starts, run the run command
        self.thread.started.connect(self.ds.run)

        # If the worker ever finished, quit the thread and clean it up
        self.ds.moveToThread(self.thread)
        self.ds.finished.connect(self.thread.quit)
        self.ds.comms_stats.connect(self.updateBytes)

        super().__init__()

    @Slot(result=str)
    def get_connection(self):
        return ds.config["communication_backend"] + "  [ " + ds.config["serial"]["port"] + " @ " + str(ds.config["serial"]["baudrate"]) + " ]"

    @Slot(result=bool)
    def is_connected(self):
        return ds.is_connected()

    @Slot(result=str)
    def is_connected_text(self):
        if self.is_connected():
            return "Disconnect"
        else:
            return "Connect"

    @Slot(result=bool)
    def is_enabled(self):
        return ds.is_enabled()

    @Slot(bool)
    def set_enabled(self, enable):
        ds.set_enabled(enable)

    @Slot()
    def connect(self):
        # Connect then start sending packets on success
        if (ds.connect_port()):
            if (not self.thread.isRunning()):
                self.thread.start()
                pass
            else:
                self.logger.fatal("Cannot start connection thread, thread already started!")
        self.connectionChanged.emit(self.is_connected())

    @Slot()
    def disconnect(self):
        ds.stop()
        ds.disconnect_port()
        self.connectionChanged.emit(self.is_connected())

    def updateBytes(self, sent, received):
        self.connectionDetailsChanged.emit(sent, received)

    def joystick_manager_tick(self):
        # self.logger.info("Joystick manager tick!")
        self.ds.joystick_manager.loop()
        self.timer.start(20) # 50 Hz


if __name__ == "__main__":
    # Force Material Style for now, as it is easier to change button colors
    # If there are objections to this, feel free to update it as fit
    sys.argv += ['--style', 'material']
    app = QGuiApplication(sys.argv)

    ds = DriverStation()
    ds.load_settings("config.yaml")
    vm_main = ViewModelMain(ds)

    engine = QQmlApplicationEngine()

    # Expose the Python object to QML
    engine.rootContext().setContextProperty("con", vm_main)

    # Get the path of the current directory, and then add the name
    # of the QML file, to load it.
    qmlFile = join(dirname(__file__), 'view_main.qml')
    engine.load(abspath(qmlFile))

    if not engine.rootObjects():
        sys.exit(-1)

    # Store the return and disconnect
    ret = app.exec_()
    ds.stop()
    ds.disconnect_port()

    sys.exit(ret)
