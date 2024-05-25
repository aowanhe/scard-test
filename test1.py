import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QComboBox, QLineEdit, QVBoxLayout, \
    QHBoxLayout, QGridLayout, QWidget, QGroupBox, QCheckBox, QRadioButton


class CameraDebugAssistant(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('摄像头调试助手')
        self.setGeometry(100, 100, 800, 600)

        # 主窗口布局
        main_layout = QHBoxLayout()

        # 左侧控制面板布局
        control_panel = QVBoxLayout()

        # 端口设置组
        port_settings_group = QGroupBox("端口设置")
        port_settings_layout = QVBoxLayout()
        self.protocol_type = QComboBox()
        self.protocol_type.addItems(["TCP Server", "TCP Client"])
        self.local_ip = QLineEdit("172.26.36.196")
        self.port = QLineEdit("8000")
        port_settings_layout.addWidget(QLabel("协议类型"))
        port_settings_layout.addWidget(self.protocol_type)
        port_settings_layout.addWidget(QLabel("本地IP地址"))
        port_settings_layout.addWidget(self.local_ip)
        port_settings_layout.addWidget(QLabel("服务器端口"))
        port_settings_layout.addWidget(self.port)
        port_settings_group.setLayout(port_settings_layout)

        # 协议配置组
        protocol_config_group = QGroupBox("协议配置")
        protocol_config_layout = QVBoxLayout()
        self.protocol_transfer = QRadioButton("协议传输")
        self.jpeg_data = QRadioButton("JPEG数据")
        self.data_end = QCheckBox("数据端")
        self.crc_16 = QCheckBox("CRC-16")
        protocol_config_layout.addWidget(self.protocol_transfer)
        protocol_config_layout.addWidget(self.jpeg_data)
        protocol_config_layout.addWidget(self.data_end)
        protocol_config_layout.addWidget(self.crc_16)
        protocol_config_group.setLayout(protocol_config_layout)

        # 设备选择
        self.device_select = QComboBox()
        self.device_select.addItems(["设备1", "设备2"])

        # 添加到左侧控制面板
        control_panel.addWidget(port_settings_group)
        control_panel.addWidget(protocol_config_group)
        control_panel.addWidget(QLabel("设备选择"))
        control_panel.addWidget(self.device_select)

        # 图像显示区域
        self.image_label = QLabel("图像显示区域")
        self.image_label.setStyleSheet("background-color: lightgray;")
        self.image_label.setFixedSize(640, 480)

        # 将控件添加到主布局
        main_layout.addLayout(control_panel)
        main_layout.addWidget(self.image_label)

        # 设置主窗口中心部件
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraDebugAssistant()
    window.show()
    sys.exit(app.exec())
