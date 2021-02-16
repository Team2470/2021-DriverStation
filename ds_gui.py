import sys
from os.path import abspath, dirname, join

from PySide6.QtQuick import QQuickView
from PySide6.QtCore import QObject, Signal, Slot, QThread
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from driver_station import DriverStation


class ViewModelMain(QObject):
    connectionChanged = Signal(bool, arguments=['connected'])
    connectionDetailsChanged = Signal(int, int, arguments=['sent', 'recieved'])

    def __init__(self, ds):
        self.ds = ds

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
        return ds.config["communication_backend"]

    @Slot(result=bool)
    def is_connected(self):
        return ds.is_connected()

    @Slot(result=str)
    def is_connected_text(self):
        if self.is_connected():
            return "Disconnect"
        else:
            return "Connect"

    @Slot()
    def connect(self):
        # Connect then start sending packets on success
        if (ds.connect_port()):
            if (not self.thread.isRunning()):
                self.thread.start()
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


if __name__ == "__main__":
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
