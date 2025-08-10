#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import numpy as np
import argparse
import socket
import threading
import json


from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QDialog, QSpinBox,
    QFormLayout, QInputDialog, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QRect, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QFontMetrics, QAction, QShortcut


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Timer Settings")
        self.setFixedSize(250, 150)

        self.talk_spin = QSpinBox()
        self.talk_spin.setRange(1, 120)
        self.talk_spin.setValue(10)
        self.talk_spin.setSuffix(" min")

        self.qna_spin = QSpinBox()
        self.qna_spin.setRange(0, 60)
        self.qna_spin.setValue(5)
        self.qna_spin.setSuffix(" min")

        layout = QFormLayout()
        layout.addRow("Talk Time:", self.talk_spin)
        layout.addRow("Q&A Time:", self.qna_spin)

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.accept)
        layout.addRow(apply_btn)

        self.setLayout(layout)

    def get_times(self):
        return self.talk_spin.value(), self.qna_spin.value()


class TimerWidget(QWidget):
    def __init__(self, talk_time=12, qna_time=3):
        super().__init__()
        self.talk_time = talk_time * 60
        self.qna_time = qna_time * 60
        self.current_phase = "Talk"
        self.is_paused = True
        self.start_time = time.perf_counter()
        self.pause_start = self.start_time
        self.time_shifts = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def sizeHint(self):
        return self.parentWidget().size() if self.parentWidget() else super().sizeHint()

    def format_time(self, seconds):
        seconds = int(seconds)
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02.0f}:{secs:02.0f}"
    
    def get_elapsed_time(self):
        if self.is_paused:
            now = self.pause_start
        else:
            now = time.perf_counter()

        elapsed_time = now - self.start_time - self.time_shifts
        return(elapsed_time)

    def start_pause_timer(self):
        now = time.perf_counter()
        if self.is_paused:
            self.time_shifts += now - self.pause_start
            self.timer.start(100)
        else:
            self.pause_start = now
            self.timer.stop()
            self.update()

        self.is_paused = not self.is_paused

    def reset_timer(self):
        now = time.perf_counter()
        self.current_phase = "Talk"
        self.is_paused = True
        self.start_time = now
        self.pause_start = now
        self.time_shifts = 0
        self.update()


    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.talk_spin.setValue(self.talk_time // 60)
        dialog.qna_spin.setValue(self.qna_time // 60)
        if dialog.exec():
            talk_minutes, qna_minutes = dialog.get_times()
            self.talk_time = talk_minutes * 60
            self.qna_time = qna_minutes * 60
            self.reset_timer()

    def adjust_time(self, delta):
        self.time_shifts += delta
        self.update()

    def adjust_custom_time(self, direction):
        text, ok = QInputDialog.getInt(self, "Adjust Time", f"Seconds to {'add' if direction == 'add' else 'remove'}:", 10, 1, 3600)
        if ok:
            self.adjust_time(text if direction == "add" else -text)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Leave 10% margin
        margin_ratio = 0.10
        size = min(self.width(), self.height())
        margin = int(size * margin_ratio)
        draw_size = size - 2 * margin
        ring_thickness = int(draw_size * 0.07)
        radius = draw_size // 2
        center = self.rect().center()

        # Arc rectangle
        arc_rect = QRect(
            center.x() - radius,
            center.y() - radius,
            2 * radius,
            2 * radius
        )

        # Time ratio
        elapsed_time = self.get_elapsed_time()
        if elapsed_time < self.talk_time:
            remaining_time = self.talk_time - elapsed_time
            time_ratio = remaining_time / self.talk_time
            sub_string = 'Talk'
        elif elapsed_time < self.qna_time + self.talk_time:
            remaining_time = self.qna_time - ( elapsed_time - self.talk_time)
            time_ratio = remaining_time / self.qna_time
            sub_string = 'Questions'
        else:
            remaining_time = 0
            time_ratio = 1
            sub_string = 'Time is up'
        
        center_string = self.format_time(remaining_time)

        if time_ratio > 0.5:
            ring_color = QColor('#32d132')
            text_color = Qt.GlobalColor.white
        elif time_ratio > 0.25:
            ring_color = QColor('#eb6b1c')
            text_color = Qt.GlobalColor.white
        else:
            ring_color = QColor('#e0142c')
            text_color = QColor('#e0142c')
        
        if not remaining_time:
            if int(time.perf_counter() * 2) % 2:
                text_color = QColor("#e0142c")
            else:
                text_color = QColor("#bd1a2e")
            ring_color = text_color
            # scale_factor = 1 + 0.15 * np.sin(time.perf_counter() * 2)
            # ring_thickness *= scale_factor
            # draw_size *= scale_factor

        if self.is_paused:
            text_color = QColor("#949494")


        # Background ring
        pen = QPen(Qt.GlobalColor.white, ring_thickness)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        painter.setPen(pen)
        painter.drawEllipse(arc_rect)

        # Foreground ring
        pen.setColor(ring_color)
        painter.setPen(pen)
        start_angle = +90 * 16  # 12 o'clock
        span_angle = int(360 * time_ratio * 16)  # Clockwise (negative)
        painter.drawArc(arc_rect, start_angle, span_angle)

        # Time text
        painter.setPen(text_color)
        font_size = int(draw_size * 0.2)
        font = QFont("Arial", font_size)
        painter.setFont(font)
        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(center_string)
        text_height = fm.height()
        painter.drawText(center.x() - text_width // 2, center.y() + text_height // 4, center_string)

        # Phase text
        phase_font = QFont("Arial", int(font_size * 0.4))
        painter.setFont(phase_font)
        fm2 = QFontMetrics(phase_font)
        phase_width = fm2.horizontalAdvance(sub_string)
        painter.drawText(center.x() - phase_width // 2, center.y() + text_height, sub_string)


class MainWindow(QMainWindow):
    remote_command = pyqtSignal(str)

    def __init__(self, talk_time, qna_time, host="0.0.0.0", port=5555):
        super().__init__()
        self.setWindowTitle("Conference Timer")
        self.setMinimumSize(600, 600)

        self.timer_widget = TimerWidget(talk_time, qna_time)
        self.setCentralWidget(self.timer_widget)

        menubar = self.menuBar()

        # Actions Menu
        actions_menu = menubar.addMenu("Actions")

        start_pause_action = QAction("Start/Pause", self)
        start_pause_action.setShortcut("Space")
        start_pause_action.triggered.connect(self.timer_widget.start_pause_timer)
        actions_menu.addAction(start_pause_action)

        reset_action = QAction("Reset", self)
        reset_action.setShortcut("R")
        reset_action.triggered.connect(self.timer_widget.reset_timer)
        actions_menu.addAction(reset_action)

        actions_menu.addSeparator()

        settings_action = QAction("Set Times", self)
        settings_action.setShortcut("Ctrl+T")
        settings_action.triggered.connect(self.timer_widget.open_settings)
        actions_menu.addAction(settings_action)

        # Adjust Menu
        adjust_menu = menubar.addMenu("Adjust Time")

        add10_action = QAction("+10s", self)
        add10_action.setShortcut("Left")
        add10_action.triggered.connect(lambda: self.timer_widget.adjust_time(10))
        adjust_menu.addAction(add10_action)

        sub10_action = QAction("-10s", self)
        sub10_action.setShortcut("Right")
        sub10_action.triggered.connect(lambda: self.timer_widget.adjust_time(-10))
        adjust_menu.addAction(sub10_action)

        adjust_menu.addSeparator()

        addx_action = QAction("+...s", self)
        addx_action.setShortcut("Ctrl+Left")
        addx_action.triggered.connect(lambda: self.timer_widget.adjust_custom_time("add"))
        adjust_menu.addAction(addx_action)

        subx_action = QAction("-...s", self)
        subx_action.setShortcut("Ctrl+Right")
        subx_action.triggered.connect(lambda: self.timer_widget.adjust_custom_time("sub"))
        adjust_menu.addAction(subx_action)

        # Ensure global shortcut activation (outside menus)
        for action in [
            start_pause_action, reset_action, settings_action,
            add10_action, sub10_action, addx_action, subx_action
        ]:
            self.addAction(action)
        
        # Start Server
        self.tcp_server = TimerServer(host, port, self.remote_command)
        self.tcp_server.start()
        self.remote_command.connect(self.handle_command)
    
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()     # Exit fullscreen
        else:
            self.showFullScreen()
    
    def handle_command(self, data):
        message = json.loads(data)

        cmd = message.get("command")
        if cmd == "startpause":
            self.timer_widget.start_pause_timer()
        elif cmd == "reset":
            talk = message.get("talk")
            qna = message.get("qna")
            if talk:
                self.timer_widget.talk_time = talk * 60
            if qna:
                self.timer_widget.qna_time = qna * 60
            self.timer_widget.reset_timer()
        elif cmd == "adjust":
            self.timer_widget.adjust_time(message.get("delta", 0))
        elif cmd == "fullscreen":
            self.toggle_fullscreen()
        else:
            print("Unknown command:", message)

    def closeEvent(self, event):
        self.tcp_server.stop()
        super().closeEvent(event)

class TimerServer(threading.Thread):
    def __init__(self, host, port, signal):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.signal = signal
        self.running = True

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind((self.host, self.port))
            server_sock.listen()

            while self.running:
                client_sock, _ = server_sock.accept()
                with client_sock:
                    data = client_sock.recv(1024)
                    if data:
                        try:
                            data = data.decode("utf-8")
                            self.signal.emit(data)
                        except Exception as e:
                            print("Invalid message:", e)

    def stop(self):
        self.running = False 

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

def start_timer():
    parser = argparse.ArgumentParser(description="Conference Timer")

    parser.add_argument("talk", type=float, nargs="?", default=None, help="Talk duration in minutes")
    parser.add_argument("qna", type=float, nargs="?", default=None, help="Q&A duration in minutes")

    # Optional named arguments (override positional if given)
    parser.add_argument("-t", "--talk", dest="talk_named", type=float, help="Talk duration in minutes")
    parser.add_argument("-q", "--qna", dest="qna_named", type=float, help="Q&A duration in minutes")

    parser.add_argument("--host", dest="host", type=str, help="Remote server host", default="0.0.0.0")
    parser.add_argument("--port", dest="port", type=int, help="Remote server port", default=5555)

    args = parser.parse_args()

    talk_time = args.talk_named if args.talk_named is not None else (args.talk if args.talk is not None else 12)
    qna_time = args.qna_named if args.qna_named is not None else (args.qna if args.qna is not None else 3)

    app = QApplication(sys.argv)
    sys.excepthook = except_hook
    threading.excepthook = lambda args: except_hook(*args[:3])
    window = MainWindow(talk_time, qna_time, host=args.host, port=args.port)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    start_timer()