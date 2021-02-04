import QtQuick 2.0
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import QtQuick.Window 2.12
import QtQuick.Controls.Material 2.12

ApplicationWindow {
    id: window
    width: 300
    height: 150
    visible: true

    property int connChanged: 0

    Connections {
        target: con

        // Signal Handlers
        function onConnectionChanged(connected) {
            // Odd hack to force our properties below to update
            // There should be a better way to do this
            connChanged++
        }
    }

    menuBar: MenuBar {
        Menu {
            title: qsTr("&File")

            Action {
                text: qsTr("&Quit")
                onTriggered: {
                    Qt.quit()
                }
            }
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
            Layout.leftMargin: 10

            Text {
                id: conLabel
                Layout.alignment: Qt.AlignLeft
                color: "black"
                font.pointSize: 14
                text: "Connection:"
            }
            Text {
                id: conType
                Layout.alignment: Qt.AlignLeft
                color: "black"
                font.pointSize: 14
                text: con.get_connection()
            }
        }

        RowLayout {
            spacing: 20
            Layout.preferredWidth: 400
            Layout.leftMargin: 10

            Button {
                    id: btn_connect
                    text: connChanged, con.is_connected_text()
                    highlighted: true
                    Material.accent: connChanged, con.is_connected() ? Material.Green : Material.Red
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
        height: 20
        RowLayout {
            Label {
                text: "Sent: 0 Received: 0"
                elide: Label.ElideRight
                horizontalAlignment: Qt.AlignHCenter
                verticalAlignment: Qt.AlignVCenter
                Layout.fillWidth: true
            }
        }
    }
}

