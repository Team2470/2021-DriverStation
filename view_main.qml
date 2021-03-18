import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import QtQuick.Controls.Material 2.12

ApplicationWindow {
    id: window
    width: 900
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

            Button {
                    id: btn_connect
                    text: connChanged, con.is_connected_text()
                    highlighted: true
                    Layout.preferredWidth: 150
                    Layout.preferredHeight: 50
                    Material.accent: connChanged, con.is_connected() ? Material.Blue : Material.Grey
                    onClicked: {
                        if (!con.is_connected()) {
                            con.connect()
                        } else {
                            con.disconnect()
                        }
                    }
            }

            Text {
                id: conLabel
                Layout.alignment: Qt.AlignLeft
                color: "black"
                font.pointSize: 10
                text: "Connection:"
            }
            Text {
                id: conType
                Layout.alignment: Qt.AlignLeft
                color: "black"
                font.pointSize: 10
                text: con.get_connection()
            }
        }

        RowLayout {
            Layout.leftMargin: 10

            Button {
                    id: btn_enable
                    text: "Enable"
                    padding: 0
                    spacing: 0
                    highlighted: con.is_enabled()
                    Layout.preferredWidth: 150
                    Layout.preferredHeight: 50
                    Material.accent: Material.Green
                    Material.theme: Material.Light
                    onClicked: {
                        con.set_enabled(true)
                        btn_enable.highlighted = con.is_enabled();
                        btn_disable.highlighted = !con.is_enabled();
                    }
            }

            Button {
                    id: btn_disable
                    text: "Disable"
                    padding: 0
                    spacing: 0
                    highlighted: !con.is_enabled()
                    Layout.preferredWidth: 150
                    Layout.preferredHeight: 50
                    Material.accent: Material.Red
                    onClicked: {
                        con.set_enabled(false)
                        btn_enable.highlighted = con.is_enabled();
                        btn_disable.highlighted = !con.is_enabled();
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

