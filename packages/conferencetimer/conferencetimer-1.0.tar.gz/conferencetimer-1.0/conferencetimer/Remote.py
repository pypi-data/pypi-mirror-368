#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import socket
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel,
    QLineEdit, QHBoxLayout, QDoubleSpinBox
)

class RemoteControlWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Remote Timer Controller")

        self.host_input = QLineEdit("127.0.0.1")
        self.port_input = QLineEdit("5555")
        self.talk_time = QDoubleSpinBox()
        self.qna_time = QDoubleSpinBox()
        self.talk_time.setMaximum(9999)
        self.qna_time.setMaximum(9999)
        self.talk_time.setValue(12)
        self.qna_time.setValue(3)

        self.status = QLabel("Disconnected")

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Host:"))
        layout.addWidget(self.host_input)
        layout.addWidget(QLabel("Port:"))
        layout.addWidget(self.port_input)

        layout.addWidget(QLabel("Talk Duration (min):"))
        layout.addWidget(self.talk_time)
        layout.addWidget(QLabel("Q&A Duration (min):"))
        layout.addWidget(self.qna_time)

        btns = [
            ("Start/Pause", lambda: self.send({"command": "startpause"})),
            ("Set Times", self.send_set_times),
            ("+10s", lambda: self.send({"command": "adjust", "delta": 10})),
            ("-10s", lambda: self.send({"command": "adjust", "delta": -10})),
            ("Fullscreen", lambda: self.send({"command": "fullscreen"})),
        ]

        for label, func in btns:
            btn = QPushButton(label)
            btn.clicked.connect(func)
            layout.addWidget(btn)

        layout.addWidget(self.status)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def send_set_times(self):
        self.send({
            "command": "reset",
            "talk": self.talk_time.value(),
            "qna": self.qna_time.value(),
        })

    def send(self, msg):
        host = self.host_input.text().strip()
        port = int(self.port_input.text().strip())
        try:
            with socket.create_connection((host, port), timeout=2) as s:
                s.sendall(json.dumps(msg).encode("utf-8"))
            self.status.setText("Sent: " + msg["command"])
        except Exception as e:
            self.status.setText("Error: " + str(e))

def start_remote():
    app = QApplication(sys.argv)
    window = RemoteControlWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    start_remote()
