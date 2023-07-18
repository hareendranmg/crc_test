import sys
import time
import serial
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QPushButton,
    QMessageBox,
)
from PyQt5.QtCore import Qt


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ser = None
        self.connected = False

        self.initUI()

    def initUI(self):
        # Create the main layout
        main_layout = QVBoxLayout()

        # Create the first horizontal layout for com port selection
        com_layout = QHBoxLayout()
        com_label = QLabel("COM Port:")
        com_layout.addWidget(com_label)
        com_dropdown = QComboBox()
        # Populate the dropdown with available COM ports (you may need to install pyserial library for this)
        import serial.tools.list_ports

        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            com_dropdown.addItem(port.device)
            if "USB Serial Port" in port.description:
                index = com_dropdown.findText(port.device)
                if index != -1:
                    com_dropdown.setCurrentIndex(index)

        com_layout.addWidget(com_dropdown)

        connect_button = QPushButton("Connect")
        connect_button.setObjectName("connect_btn")
        connect_button.clicked.connect(self.connect_to_com_port)
        com_layout.addWidget(connect_button)
        main_layout.addLayout(com_layout)

        # Create the second horizontal layout for step, rpm, and number_step input
        input_layout = QHBoxLayout()
        speed_label = QLabel("Spped:")
        input_layout.addWidget(speed_label)
        speed_input = QLineEdit()
        speed_input.setText("100")
        speed_input.setObjectName("speed_input")
        input_layout.addWidget(speed_input)
        direction_label = QLabel("Direction:")
        input_layout.addWidget(direction_label)
        direction_input = QLineEdit()
        direction_input.setText("06")
        direction_input.setObjectName("direction_input")
        input_layout.addWidget(direction_input)
        number_step_label = QLabel("Number of Steps")
        input_layout.addWidget(number_step_label)
        number_step_input = QLineEdit()
        number_step_input.setText("100")
        number_step_input.setObjectName("number_step_input")
        input_layout.addWidget(number_step_input)
        crc_button = QPushButton("Calculate CRC")
        crc_button.clicked.connect(self.calculate_crc)
        input_layout.addWidget(crc_button)
        main_layout.addLayout(input_layout)

        # Create the third horizontal layout for showing calculated crc and send button
        crc_layout = QHBoxLayout()
        crc_label = QLabel("CRC:")
        crc_layout.addWidget(crc_label)
        self.crc_field = QLineEdit()
        self.crc_field.setObjectName("crc_field")
        crc_layout.addWidget(self.crc_field)
        send_button = QPushButton("Send to COM Port")
        send_button.clicked.connect(self.send_to_com_port)
        crc_layout.addWidget(send_button)
        main_layout.addLayout(crc_layout)

        crc_response_layout = QHBoxLayout()
        crc_response_label = QLabel("Response:")
        crc_response_layout.addWidget(crc_response_label)
        self.crc_response_field = QLineEdit()
        self.crc_response_field.setObjectName("crc_response_field")
        crc_response_layout.addWidget(self.crc_response_field)

        main_layout.addLayout(crc_response_layout)

        # Set the main layout for the widget
        self.setLayout(main_layout)

    def connect_to_com_port(self):
        if not self.connected:
            com_port = self.sender().parent().findChild(QComboBox).currentText()
            print(f"Connecting to COM Port: {com_port}")
            self.ser = serial.Serial(com_port, 19200)
            print("Connection established")
            self.connected = True
            self.sender().setText("Disconnect")
        else:
            print("Disconnecting from COM Port")
            self.ser.close()
            self.ser = None
            self.connected = False
            self.sender().setText("Connect")
            print("Disconnected from COM Port")

    def calculate_crc(self):
        # Implement your CRC calculation logic here
        print("Calculating CRC...")
        speed = self.sender().parent().findChild(QLineEdit, "speed_input").text()
        direction = (
            self.sender().parent().findChild(QLineEdit, "direction_input").text()
        )
        number_step = (
            self.sender().parent().findChild(QLineEdit, "number_step_input").text()
        )

        # speed = str(hex(int(speed))[2:])
        # direction = str(hex(int(direction))[2:])
        # number_step = str(hex(int(number_step))[2:])
        speed = format(int(speed), "02x")
        direction = format(int(direction), "02x")
        number_step = format(int(number_step), "02x")
        print(
            f"Speed: {speed}, movemnent type: {direction}, Number of steps: {number_step}"
        )

        str_to_send_str = (
            f"02 10 00 25 00 05 0A 02 {direction} 00 00 00 {speed} 00 00 BB 80".replace(
                " ", ""
            )
        )
        str_to_send = bytes.fromhex(str(str_to_send_str))
        response = self.modbusCrc(str_to_send)
        ba = response.to_bytes(2, byteorder="little")
        # print("%02X %02X" % (ba[0], ba[1]))
        crc = "%02X %02X" % (ba[0], ba[1])
        final_crc = (str_to_send_str + crc).replace(" ", "")
        self.crc_field.setText(final_crc)

        print(final_crc)
        return
        # Perform CRC calculation and update the self.crc_field with the calculated value

    def send_to_com_port(self):
        # Implement your send to COM port logic here
        if self.ser is not None:
            crc = self.crc_field.text()
            print(f"Sending CRC: {crc} to COM Port")
            self.ser.write(crc.encode())
            time.sleep(1)
            response = self.ser.read_all()
            print(f"response=> {response}")
            self.crc_response_field.setText(response.decode())

        else:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("Alert")
            msg_box.setText("COM port not connected. ")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()

    def modbusCrc(self, msg: str) -> int:
        crc = 0xFFFF
        for n in range(len(msg)):
            crc ^= msg[n]
            for i in range(8):
                if crc & 1:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec_())
