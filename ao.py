import sys
import serial
import serial.tools.list_ports
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QRadioButton, QTextEdit, QLineEdit, QGridLayout, QGroupBox, QCheckBox,QFileDialog
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer


class SerialThread(QThread):
    received = pyqtSignal(str)

    def __init__(self, port, baudrate, databits, stopbits, parity):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.databits = databits
        self.stopbits = stopbits
        self.parity = parity
        self.serial = None
        self.running = True

    def run(self):
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.databits,
                stopbits=self.stopbits,
                parity=self.parity
            )
        except Exception as e:
            self.received.emit(f"Error opening serial port: {str(e)}")
            return
        while self.running:
            if self.serial.in_waiting:
                data = self.serial.read(self.serial.in_waiting).decode('utf-8', errors='ignore')
                self.received.emit(data)

    def stop(self):
        self.running = False
        if self.serial and self.serial.is_open:
            self.serial.close()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("串口通信助手")
        self.setGeometry(100, 100, 800 ,600)
        self.serial_thread = None

        # 创建串口配置部分
        serial_config_group = QGroupBox("串口配置")
        serial_config_group.setStyleSheet("background-color: #E3E3E3;")
        serial_config_group.setFixedSize(200,200)
        serial_config_layout = QGridLayout()

        serial_config_layout.addWidget(self.create_label("端口"), 0, 0)
        self.port_combobox = self.create_Qcombox()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ports)
        self.timer.start(100)
        serial_config_layout.addWidget(self.port_combobox, 0, 1)

        serial_config_layout.addWidget(self.create_label("波特率"), 1, 0)
        self.baudrate_combobox = self.create_Qcombox()
        self.baudrate_combobox.addItems(['9600', '14400', '19200', '38400', '57600', '115200'])
        serial_config_layout.addWidget(self.baudrate_combobox, 1, 1)

        serial_config_layout.addWidget(self.create_label("数据位"), 2, 0)
        self.data_bits_combobox =self.create_Qcombox()
        self.data_bits_combobox.addItems(['5', '6', '7', '8'])
        serial_config_layout.addWidget(self.data_bits_combobox, 2, 1)

        serial_config_layout.addWidget(self.create_label("停止位"), 3, 0)
        self.stop_bits_combobox = self.create_Qcombox()
        self.stop_bits_combobox.addItems(['1', '1.5', '2'])
        serial_config_layout.addWidget(self.stop_bits_combobox, 3, 1)

        serial_config_layout.addWidget(self.create_label("校验位"), 4, 0)
        self.parity_combobox = self.create_Qcombox()
        self.parity_combobox.addItems(['N', 'E', 'O', 'M', 'S'])
        serial_config_layout.addWidget(self.parity_combobox, 4, 1)

        self.open_serial_button = self.create_button("打开串口", 100, 30)
        self.open_serial_button.clicked.connect(self.open_serial)
        serial_config_layout.addWidget(self.open_serial_button, 5, 1)

        serial_config_group.setLayout(serial_config_layout)

        # 创建接收区
        receive_group = QGroupBox("接收区设置")
        receive_group.setFixedSize(200,200)
        receive_group.setStyleSheet("background-color: #E3E3E3;")
        receive_layout = QGridLayout()
        self.ascii_radio = QRadioButton("ASCII")
        self.hex_radio = QRadioButton("HEX")
        self.ascii_radio.setChecked(True)
        receive_layout.addWidget(self.ascii_radio, 0, 0)
        receive_layout.addWidget(self.hex_radio, 0, 1)
        self.stop_display_checkbox = self.create_checkbox("停止显示")
        receive_layout.addWidget(self.stop_display_checkbox, 1, 0)
        self.log_mode_checkbox = self.create_checkbox("日志模式")
        receive_layout.addWidget(self.log_mode_checkbox, 1, 1)
        self.clear_receive_button = self.create_button("清空接收区", 80, 30)
        self.clear_receive_button.clicked.connect(self.clear_receive_area)
        receive_layout.addWidget(self.clear_receive_button)
        self.save_to_file_button = self.create_button("保存到文件", 80, 30)
        receive_layout.addWidget(self.save_to_file_button)
        receive_group.setLayout(receive_layout)

        # 创建发送区
        send_group = QGroupBox("发送区设置")
        send_group.setFixedSize(200,200)
        send_group.setStyleSheet("background-color: #E3E3E3;")
        send_layout = QGridLayout()
        self.send_options_combobox = self.create_Qcombox()
        self.send_options_combobox.addItems(["单项发送", "循环发送"])
        send_layout.addWidget(self.send_options_combobox, 2, 0, 1, 2)
        self.auto_send_period_input = QLineEdit()
        self.auto_send_period_input.setPlaceholderText("自动发送周期(ms)")
        send_layout.addWidget(self.auto_send_period_input, 3, 0, 1, 2)
        self.ascii_send_radio = QRadioButton("ASCII")
        self.hex_send_radio = QRadioButton("HEX")
        self.ascii_send_radio.setChecked(True)
        send_layout.addWidget(self.ascii_send_radio, 0, 0)
        send_layout.addWidget(self.hex_send_radio, 0, 1)
        self.send_newline_checkbox = self.create_checkbox("发送新行")
        send_layout.addWidget(self.send_newline_checkbox, 1, 0)
        self.auto_send_checkbox = self.create_checkbox("自动发送")
        send_layout.addWidget(self.auto_send_checkbox, 1, 1)
        send_group.setLayout(send_layout)

        # 创建接收显示区和发送输入区
        self.receive_text_edit = QTextEdit()
        self.receive_text_edit.setReadOnly(True)
        self.send_text_edit = QTextEdit()

        # 创建发送按钮
        self.send_button = self.create_button("发送数据", 100, 30)
        self.send_button.clicked.connect(self.send_data)
        self.load_file_button = self.create_button("加载文件", 100, 30)
        self.load_file_button.clicked.connect(self.load_file)

        # 消息提示区
        self.msg = self.create_label('')
        self.msg.setStyleSheet('color:red')

        # 布局
        main_layout = QGridLayout()
        main_layout.addWidget(serial_config_group, 0, 0, 2, 1)
        main_layout.addWidget(receive_group, 2, 0)
        main_layout.addWidget(send_group, 3, 0)
        main_layout.addWidget(self.msg, 4, 0)
        main_layout.addWidget(self.receive_text_edit, 0, 1, 2, 1)
        main_layout.addWidget(self.send_text_edit, 2, 1, 2, 1)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.load_file_button)
        button_layout.addWidget(self.send_button)
        main_layout.addLayout(button_layout, 4, 1)
        self.setLayout(main_layout)

    def create_label(self, text):
        label = QLabel(text)
        label.setFont(QFont("Segoe UI", 10))
        label.setStyleSheet("color: #000000;")
        return label

    def create_button(self, text, width, height):
        button = QPushButton(text)
        button.setFixedSize(width, height)
        button.setStyleSheet("""
               QPushButton {
                   background-color: #F0F8FF;  /* 淡蓝色背景 */
                   color: black;               /* 文字颜色 */
                   border-radius: 5px;         /* 圆角 */
                   padding: 5px;               /* 内边距 */
                   border: 1px solid #A9A9A9;  /* 边框 */
               }
               QPushButton:hover {
                   background-color: #ADD8E6;  /* 悬浮时背景颜色变化 */
               }
               QPushButton:pressed {
                   background-color: #87CEEB;  /* 按下时背景颜色变化 */
               }
           """)
        return button

    def create_checkbox(self, text):
        checkbox = QCheckBox(text)
        checkbox.setFont(QFont("Segoe UI", 10))
        return checkbox
    def create_Qcombox(self):
        com = QComboBox()
        com.setStyleSheet("""
            QComboBox {
                background-color: #F0F8FF;  /* 淡蓝色背景 */
                color: #2e2e2e;             /* 深灰色字体 */
                border: 1px solid #A9A9A9;  /* 边框 */
                border-radius: 4px;         /* 圆角边框 */
                padding: 2px 5px;           /* 内边距 */
            }
            QComboBox:hover {
                border-color: #87CEEB;     /* 悬浮时边框颜色变化 */
            }
            QComboBox::drop-down {
                border: none;              /* 下拉箭头的边框 */
            }
            QComboBox QAbstractItemView {
                selection-background-color: #ADD8E6; /* 选中项的背景颜色 */
            }
        """)
        return com


    def update_ports(self):
        ports = serial.tools.list_ports.comports()
        self.port_combobox.clear()
        self.port_combobox.addItems([port.device for port in ports])

    def open_serial(self):
        if not self.port_combobox:
            self.msg.setText('Error opening serial')
            return
        if self.serial_thread and self.serial_thread.isRunning():
            self.serial_thread.stop()
            self.serial_thread.wait()
            self.serial_thread = None
            self.receive_text_edit.clear()
            self.open_serial_button.setText("打开串口")
            return

        port = self.port_combobox.currentText()
        baudrate = int(self.baudrate_combobox.currentText())
        databits = int(self.data_bits_combobox.currentText())
        stopbits = float(self.stop_bits_combobox.currentText())
        parity = self.parity_combobox.currentText()
        parity_map = {'N': serial.PARITY_NONE, 'E': serial.PARITY_EVEN, 'O': serial.PARITY_ODD, 'M': serial.PARITY_MARK, 'S': serial.PARITY_SPACE}

        self.serial_thread = SerialThread(port, baudrate, databits, stopbits, parity_map[parity])
        self.serial_thread.received.connect(self.update_receive_area)
        self.serial_thread.start()
        self.open_serial_button.setText("关闭串口")
        self.msg.setText(f'connect to {port} ')

    def update_receive_area(self, data):
        if not self.stop_display_checkbox.isChecked():
            self.receive_text_edit.append(data)

    def clear_receive_area(self):
        self.receive_text_edit.clear()

    def send_data(self):
        if self.serial_thread and self.serial_thread.isRunning():
            data = self.send_text_edit.toPlainText()
            if self.send_newline_checkbox.isChecked():
                data += '\n'
            if self.ascii_send_radio.isChecked():
                self.serial_thread.serial.write(data.encode('utf-8'))
            elif self.hex_send_radio.isChecked():
                self.serial_thread.serial.write(bytes.fromhex(data))

    def load_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "选择文件", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.send_text_edit.setPlainText(content)
            except Exception as e:
                self.msg.setText(f"Error loading file: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
