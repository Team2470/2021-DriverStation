import sys
from os.path import abspath, dirname, join
import pygame

from PySide2.QtQuick import QQuickView
from PySide2.QtCore import QObject, Signal, Slot, QThread, QTimer
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine

from driver_station import DriverStation
from communication import CommunicationState
from communication import serial_sources
from communication import bluetooth_sources

import structlog
import time
import asyncio
from threading import Thread


class ViewModelMain(QObject):
    connectionChanged = Signal(bool, arguments=['connected'])
    connectionDetailsChanged = Signal(str, int, int, arguments=['comm_state', 'sent', 'recieved'])
    connectionJoysticksChanged = Signal(str, str, str, arguments=['joystick_count_summary', 'joystick_1_summary', 'joystick_2_summary'])
    availableSourceChanged = Signal(str, arguments=['sources_str'])

    def __init__(self, ds):
        self.logger = structlog.get_logger()
        self.ds = ds

        # Joystick manager task
        self.timer = QTimer()
        self.timer.timeout.connect(self.joystick_manager_tick)
        self.timer.start(20)  # Poll at 50 HZ

        # Available sources tasks
        self.avialable_source_thread = Thread(target=self.available_source_run)
        self.avialable_source_thread.start()

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
    def get_connection(self) -> str:
        connection_str = "unknown"
        if ds.config["communication_backend"] == "serial":
            connection_str = ds.config["serial"]["port"] + " @ " + str(ds.config["serial"]["baudrate"])
        elif ds.config["communication_backend"] == "bluetooth":
            connection_str = "MAC Address " + ds.config["bluetooth"]["mac_address"]

        return ds.config["communication_backend"] + "  [ " + connection_str + " ]"

    @Slot(result=bool)
    def is_connected(self) -> bool:
        return ds.get_comm_state() == CommunicationState.CONNECTED

    @Slot(result=bool)
    def is_connecting(self) -> bool:
        return ds.get_comm_state() == CommunicationState.CONNECTING

    @Slot(result=str)
    def is_connected_text(self) -> str:
        if self.is_connected():
            return "Disconnect"
        elif self.is_connecting():
            return "Connecting"
        else:
            return "Connect"

    @Slot(result=bool)
    def is_enabled(self) -> bool:
        return ds.is_enabled()

    @Slot(bool)
    def set_enabled(self, enable: bool):
        ds.set_enabled(enable)

    @Slot()
    def connect(self):
        # Connect then start sending packets on success
        if ds.connect_port():
            if not self.thread.isRunning():
                self.thread.start()
                pass
            else:
                self.logger.fatal("Cannot start connection thread, thread already started!")

    @Slot()
    def disconnect(self):
        ds.stop()
        ds.disconnect_port()
        self.connectionChanged.emit(self.is_connected())

    def updateBytes(self, comm_state: str, sent: int, received: int):
        self.connectionDetailsChanged.emit(comm_state, sent, received)

    def joystick_manager_tick(self):
        # self.logger.info("Joystick manager tick!", comm_state=self.ds.get_comm_state_str())
        self.connectionChanged.emit(self.is_connected() or self.is_connecting())
        self.ds.joystick_manager.loop()

        # Generate strings for GUI
        j1_summary = "Not Connected"
        if 1 in self.ds.joystick_manager.joysticks:
            j1_summary = self.ds.joystick_manager.joysticks[1].get_summary()

        j2_summary = "Not Connected"
        if 2 in self.ds.joystick_manager.joysticks:
            j2_summary = self.ds.joystick_manager.joysticks[2].get_summary()

        ids = []
        for joystick in [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]:
            ids.append(joystick.get_guid())

        j_summary = "{} - Available UUIDs: [{}]".format(
            pygame.joystick.get_count(),
            " ,".join(ids)
        )

        self.connectionJoysticksChanged.emit(j_summary, j1_summary, j2_summary)

        self.timer.start(20) # 50 Hz

    def available_source_run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        while True: # TODO this needs to exit
            # self.logger.info("Updating available source")

            available_sources_str = "unknown"

            if ds.config["communication_backend"] == "serial":
                ports = serial_sources.available_ports()
                if len(ports) == 0:
                    available_sources_str = "none"
                else:
                    available_sources_str = "\n".join(ports)
            elif ds.config["communication_backend"] == "bluetooth":
                devices = bluetooth_sources.avaiable_devices()
                if len(devices) == 0:
                    available_sources_str = "none"
                else:
                    device_strs = []
                    for device in devices:
                        device_str = "Address: "+ device.address + "\tName:" + device.name
                        device_strs.append(device_str)
                    available_sources_str = "\n".join(device_strs)


            self.availableSourceChanged.emit(available_sources_str)

            time.sleep(1)


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
