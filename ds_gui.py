import sys
from os.path import abspath, dirname, join

from PySide6.QtQuick import QQuickView
from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine


class Bridge(QObject):

    @Slot(str, result=str)
    def getColor(self, color_name):
        if color_name.lower() == "red":
            return "#ef9a9a"
        elif color_name.lower() == "green":
            return "#a5d6a7"
        elif color_name.lower() == "blue":
            return "#90caf9"
        else:
            return "white"

    @Slot(float, result=int)
    def getSize(self, s):
        size = int(s * 42) # Maximum font size
        if size <= 0:
            return 1
        else:
            return size

    @Slot(str, result=bool)
    def getItalic(self, s):
        if s.lower() == "italic":
            return True
        else:
            return False

    @Slot(str, result=bool)
    def getBold(self, s):
        if s.lower() == "bold":
            return True
        else:
            return False

    @Slot(str, result=bool)
    def getUnderline(self, s):
        if s.lower() == "underline":
            return True
        else:
            return False


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    view.setSource("view.qml")
    bridge = Bridge()
    view.engine().rootContext().setContextProperty("con", bridge)

    if view.status() == QQuickView.Error:
        sys.exit(-1)
    view.show()

    # execute and cleanup
    app.exec_()
    del view

    # engine = QQmlApplicationEngine()
    #
    # # Instance of the Python object
    # bridge = Bridge()
    #
    # # Expose the Python object to QML
    # context = engine.rootContext()
    # context.setContextProperty("con", bridge)
    #
    # # Get the path of the current directory, and then add the name
    # # of the QML file, to load it.
    # qmlFile = join(dirname(__file__), 'view.qml')
    # engine.load(abspath(qmlFile))
    #
    # if not engine.rootObjects():
    #     sys.exit(-1)
    #
    # sys.exit(app.exec_())
