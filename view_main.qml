import QtQuick 2.0
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import QtQuick.Window 2.12
import QtQuick.Controls.Material 2.12

ApplicationWindow {
    id: window
    width: 500
    height: 200
    visible: true

    Connections {
        target: con

        // Signal Handlers
        function onConnectionChanged(connected) {
            btn_connect.text = con.is_connected_text()
            if (con.is_connected()) {
                btn_connect.Material.accent=Material.Red
            } else {
                btn_connect.Material.accent=Material.Green
            }
        }
    }

   menuBar: MenuBar {
        Menu {
            title: qsTr("&File")
            Action { text: qsTr("&Quit") }
        }
        Menu {
            title: qsTr("&Help")
            Action { text: qsTr("&About") }
        }
    }


    GridLayout {
        id: grid
        columns: 1
        rows: 2

        RowLayout {
            spacing: 20
            Layout.preferredWidth: 400

            Text {
                id: conLabel
                Layout.alignment: Qt.AlignHLeft
                color: "black"
                font.pointSize: 14
                text: "Connection:"
            }
            Text {
                id: conType
                Layout.alignment: Qt.AlignHLeft
                color: "black"
                font.pointSize: 14
                text: con.get_connection()
            }
        }

        RowLayout {
            spacing: 20
            Layout.preferredWidth: 400

            Button {
                    id: btn_connect
                    text: con.is_connected_text()
                    highlighted: true
                    Material.accent: Material.Green
                    onClicked: {
                        if (!con.is_connected()) {
                            con.connect()
                        } else {
                            con.disconnect()
                        }
                    }
            }
        }
    }

    footer: ToolBar {

    }
}

