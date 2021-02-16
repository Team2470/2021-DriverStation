import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import QtQuick.Controls.Material 2.12

ApplicationWindow {
    id: window
    width: 600
    height: 200
    visible: true
    title: "2021 TP Driver Station"

    property int connChanged: 0

    Connections {
        target: con

        // Signal Handlers
        function onConnectionChanged(connected) {
            // Odd hack to force our properties below to update
            // There should be a better way to do this
            connChanged++
            lblConnDetails.text = "Bytes -- Sent: " + 0 + " Received: " + 0
        }

        function onConnectionDetailsChanged(sent, received) {
            lblConnDetails.text = "Bytes -- Sent: " + sent + " Received: " + received
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
                font.pointSize: 12
                text: "Connection:"
            }
            Text {
                id: conType
                Layout.alignment: Qt.AlignLeft
                color: "black"
                font.pointSize: 12
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
                    Layout.preferredWidth: 150
                    Layout.preferredHeight: 50
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
        height: 25
        RowLayout {
            Label {
                id: lblConnDetails
                text: "Disconnected"
                elide: Label.ElideRight
                horizontalAlignment: Qt.AlignHCenter
                verticalAlignment: Qt.AlignVCenter
                Layout.fillWidth: true
            }
        }
    }
}

