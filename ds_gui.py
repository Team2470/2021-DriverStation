import sys
from os.path import abspath, dirname, join

from PySide6.QtQuick import QQuickView
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from driver_station import DriverStation


class ViewModelMain(QObject):
    connectionChanged = Signal(bool, arguments=['connected'])

    def __init__(self, ds):
        self.ds = ds
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
        ds.connect()
        self.connectionChanged.emit(self.is_connected())

    @Slot()
    def disconnect(self):
        ds.disconnect()
        self.connectionChanged.emit(self.is_connected())


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

    sys.exit(app.exec_())
