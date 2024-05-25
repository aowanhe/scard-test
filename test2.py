import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QLineEdit, QTextEdit, \
    QRadioButton, QHBoxLayout, QCheckBox, QFileDialog, QMessageBox, QGridLayout, QGroupBox, QComboBox, QFileDialog
from PyQt6.QtCore import QTimer
import socket
import threading


class NetworkDebuggingAssistant(QWidget):
    def __init__(self):
        super().__init__()
        self.button = None
        self.setWindowTitle("串口通信助手")
        self.setGeometry(100, 100, 800, 600)
        port_config_group = QGroupBox("端口配置")
        port_config_group.setStyleSheet("background-color: #E3E3E3;")
        port_config_group.setFixedSize(200, 250)
        port_config_layout = QGridLayout()

        port_config_layout.addWidget(self.create_label("协议类型"), 0, 0, 1, 2)
        self.protocol_combobox = self.create_Qcombox()
        self.protocol_combobox.addItems(['TCP Server', 'TCP Client', 'UDP'])
        self.protocol_combobox.currentTextChanged.connect(self.button_change)
        port_config_layout.addWidget(self.protocol_combobox, 1, 0, 1, 2)

        port_config_layout.addWidget(self.create_label("IP地址"), 2, 0, 1, 2)
        self.IP_text_edit = QLineEdit()
        self.IP_text_edit.setPlaceholderText('')
        port_config_layout.addWidget(self.IP_text_edit, 3, 0, 1, 2)

        port_config_layout.addWidget(self.create_label("端口"), 4, 0, 1, 2)
        self.port_text_edit = QLineEdit('8000')

        port_config_layout.addWidget(self.port_text_edit, 5, 0, 1, 2)

        self.button = self.create_button('启动监听', 120, 30)
        self.button.clicked.connect(self.button_a)
        port_config_layout.addWidget(self.button, 6, 0, 1, 2)
        port_config_group.setLayout(port_config_layout)



        # 创建接收区
        receive_group = QGroupBox("接收区设置")
        receive_group.setFixedSize(200, 200)
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
        send_group.setFixedSize(200, 200)
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

        self.load_file_button = self.create_button("加载文件", 100, 30)
        self.load_file_button.clicked.connect(self.load_file)

        # 布局
        main_layout = QGridLayout()
        main_layout.addWidget(port_config_group, 0, 0, 2, 1)
        main_layout.addWidget(receive_group, 2, 0)
        main_layout.addWidget(send_group, 3, 0)
        main_layout.addWidget(self.receive_text_edit, 0, 1, 2, 1)
        main_layout.addWidget(self.send_text_edit, 2, 1, 2, 1)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.load_file_button)
        button_layout.addWidget(self.send_button)
        main_layout.addLayout(button_layout, 4, 1)
        self.setLayout(main_layout)
        # Text area for log


        # Network variables
        self.server_socket = None
        self.client_sockets = []
    def  button_a(self):
        self.IP_text_edit.setReadOnly(True)
        self.port_text_edit.setReadOnly(True)

        if self.button.text() == '启动监听':
            self.start_server()
            self.button.setText('停止监听')
        elif self.button.text() == '建立连接':
            print(self.button.text())

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
    def load_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "选择文件", "", "Text Files (*.txt);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.send_text_edit.setPlainText(content)
            except Exception as e:
                self.receive_text_edit.append(f"Error loading file: {str(e)}")
    def clear_receive_area(self):
        self.receive_text_edit.clear()

    def button_change(self):
        # 根据选择的不同选项创建不同的按钮
        if self.protocol_combobox.currentText() =='TCP Server':
            self.button.setText('启动监听')
        elif self.protocol_combobox.currentText() == 'TCP Client':
            self.button.setText('建立连接')
        # 将按钮添加到布局

    def start_server(self):
        ip = self.IP_text_edit.text()
        port = int(self.port_text_edit.text())

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ip, port))
        self.server_socket.listen(5)

        self.receive_text_edit.append(f"Server started on {ip}:{port}")

        threading.Thread(target=self.accept_clients).start()

    def accept_clients(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            self.client_sockets.append(client_socket)
            self.receive_text_edit.append(f"Client connected from {client_address}")
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if data:
                    self.receive_text_edit.append(f"Received: {data}")
            except ConnectionResetError:
                self.receive_text_edit.append("Client disconnected")
                self.client_sockets.remove(client_socket)
                break


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NetworkDebuggingAssistant()
    window.show()
    sys.exit(app.exec())
