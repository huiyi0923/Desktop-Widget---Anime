# -*- coding: utf-8 -*-
"""
PySide6 桌面透明宠物（GIF 动作切换版 · v5 多动作+选择菜单+碎碎念文字）
=====================================================================
功能：
1. 隐藏 Windows 自带标题栏（导航栏），窗口背景全透明
2. 播放透明 GIF，并按鼠标事件切换动作：
   - 待机/小动作（鼠标不动）  -> idle.gif
   - 拖拽动画（按住左键拖动）-> drag.gif
   - 左键单击   -> 播放「点击回应」动画，播完自动回待机
   - 右键单击   -> 弹出动作选择菜单，选中后播放该动作，播完自动回待机
   - 双击左键   -> 退出
   - 待机每 20 秒自动碎碎念一次，并在宠物左上角随机显示一句话
3. 所有动作 GIF 都放在本脚本同目录；缺失的 GIF 自动从菜单里隐藏，不会报错

v5 新增：
- 多动作支持：dance/sleep/happy/angry（跳舞/睡觉/开心蹦跳/生气）
- 右键弹出动作选择菜单（QMenu），选择即播放，播完回待机
- talk 触发时，宠物左上角 QLabel 随机显示 TALK_TEXTS 里的一句话

依赖安装：
    pip install PySide6

用法：
    把各动作 GIF 放在本文件同目录，然后：
    python pet_window.py
"""

import os
import random
import sys
import time

from PySide6.QtCore import Qt, QTimer, QPoint, QSize
from PySide6.QtGui import QMovie, QCursor
from PySide6.QtWidgets import (
    QApplication, QLabel, QMenu, QWidget,
)

# GIF 文件名与动作的映射（放在本脚本同目录）
GIF_FILES = {
    "idle": "idle.gif",      # 待机/小动作
    "click": "click.gif",    # 点击回应
    "drag": "drag.gif",      # 拖拽动画
    "talk": "talk.gif",      # 碎碎念说话
    "dance": "dance.gif",    # 跳舞
    "sleep": "sleep.gif",    # 睡觉
    "happy": "happy.gif",    # 开心蹦跳
    "angry": "angry.gif",    # 生气
}

# 动作选择菜单里显示的中文名（drag 靠鼠标手势触发，不进菜单）
ACTION_LABELS = {
    "idle": "待机",
    "click": "点击回应",
    "talk": "碎碎念",
    "dance": "跳舞",
    "sleep": "打哈欠",
    "happy": "开心蹦跳",
    "angry": "生气",
}

# 每个动作播放多久后自动回待机（毫秒）
ACTION_MS = {
    "click": 3000,
    "talk": 5000,
    "dance": 6000,
    "sleep": 6000,
    "happy": 5000,
    "angry": 5000,
}

# 碎碎念时左上角随机展示的文字
TALK_TEXTS = [
    "要吃更多token～",
    "主人，摸摸头嘛～",
    "今天也要加油喵！",
    "肚子饿了…想吃token～",
    "陪我玩一会儿嘛",
    "代码写不动啦…",
    "你在看什么呢～",
]

WINDOW_SIZE = 200           # 宠物显示尺寸（像素）
TALK_INTERVAL_MS = 20000    # 待机时每隔 10 秒碎碎念一次
DRAG_THRESHOLD = 10         # 移动超过该像素才算拖拽（否则算点击）
DRAG_WATCH_MS = 400         # 拖拽中超过该时长没有鼠标移动 = 已松手


class PetWindow(QWidget):
    def __init__(self):
        super().__init__()

        # ========== 1. 隐藏系统自带标题栏（导航栏） ==========
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )

        # ========== 2. 窗口背景全透明 ==========
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(WINDOW_SIZE, WINDOW_SIZE)

        # ========== 3. 加载 GIF ==========
        # 不要用 label.setScaledContents(True)：那是快速缩放（低质量），
        # 在高分屏（Windows 125%/150% 缩放）上会把小 GIF 拉大变糊。
        # 正确做法见 _on_frame：每帧 SmoothTransformation 平滑缩放 + DPR 适配。
        self.label = QLabel(self)
        self.label.setGeometry(0, 0, WINDOW_SIZE, WINDOW_SIZE)
        self.label.setAlignment(Qt.AlignCenter)

        self.movies = {}
        base = os.path.dirname(os.path.abspath(__file__))
        for action, fname in GIF_FILES.items():
            path = os.path.join(base, fname)
            if os.path.exists(path):
                m = QMovie(path)
                m.setCacheMode(QMovie.CacheAll)
                self.movies[action] = m
            else:
                print(f"[提示] 未找到 {fname}（对应动作：{action}），"
                      f"该动作将从菜单中隐藏。")

        if not self.movies:
            raise FileNotFoundError(
                "没有找到任何 GIF，请把动作 GIF 放在脚本同目录"
            )

        # ========== 4. 碎碎念文字（宠物左上角） ==========
        self.talk_label = QLabel(self)
        self.talk_label.setGeometry(6, 6, WINDOW_SIZE - 12, 56)
        self.talk_label.setWordWrap(True)
        self.talk_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.talk_label.setStyleSheet(
            "QLabel {"
            "  color: #ffffff;"
            "  background-color: rgba(20, 20, 30, 170);"
            "  border-radius: 8px;"
            "  padding: 4px 8px;"
            "  font-size: 13px;"
            "  font-weight: bold;"
            "}"
        )
        self.talk_label.hide()

        # ---------- 状态机（state 初始为 None，不能预置 "idle"）----------
        self.movie = None
        self.state = None            # idle / click / drag / talk / dance / ...
        self._grabbed = False
        self._pressed = False
        self._moved = False
        self._last_move = 0.0

        # 一次性动作播完后回待机
        self._back_to_idle = QTimer(self)
        self._back_to_idle.setSingleShot(True)
        self._back_to_idle.timeout.connect(self._to_idle)

        # 待机时周期性碎碎念
        self._talk_timer = QTimer(self)
        self._talk_timer.timeout.connect(self._maybe_talk)
        self._talk_timer.start(TALK_INTERVAL_MS)

        # 拖拽看门狗：停止移动超时 = 松手
        self._drag_watch = QTimer(self)
        self._drag_watch.setInterval(100)
        self._drag_watch.timeout.connect(self._on_drag_watch)

        # 启动即播放待机
        self.set_action("idle")

    # ---------- 动作切换 ----------
    def set_action(self, action: str):
        movie = self.movies.get(action)
        if movie is None:
            return  # 该动作的 GIF 缺失，保持当前状态
        if self.state == action:
            return
        if self.movie is not None:
            try:
                self.movie.frameChanged.disconnect(self._on_frame)
            except (RuntimeError, TypeError):
                pass
            self.movie.stop()
        self.movie = movie
        self.movie.frameChanged.connect(self._on_frame)
        self.movie.start()
        self.state = action
        # 碎碎念时显示左上角随机文字，其它动作隐藏
        if action == "talk":
            self.talk_label.setText(random.choice(TALK_TEXTS))
            self.talk_label.show()
        else:
            self.talk_label.hide()

    def _to_idle(self):
        self.set_action("idle")

    # ---------- 每帧平滑缩放（防模糊的关键） ----------
    def _on_frame(self, _frame):
        if self.movie is None:
            return
        pm = self.movie.currentPixmap()
        if pm.isNull():
            return
        dpr = self.devicePixelRatioF()
        target = QSize(
            round(WINDOW_SIZE * dpr),
            round(WINDOW_SIZE * dpr),
        )
        scaled = pm.scaled(
            target, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        scaled.setDevicePixelRatio(dpr)
        self.label.setPixmap(scaled)

    # ---------- 待机时的碎碎念 ----------
    def _maybe_talk(self):
        if self.state == "idle" and "talk" in self.movies:
            self._back_to_idle.stop()
            self.set_action("talk")
            self._back_to_idle.start(ACTION_MS.get("talk", 5000))

    # ---------- 动作选择菜单 ----------
    def _show_action_menu(self):
        menu = QMenu(self)
        for action, label in ACTION_LABELS.items():
            if action in self.movies:      # 只列出有 GIF 的动作
                menu.addAction(label, lambda a=action: self._run_chosen(a))
        menu.addSeparator()
        menu.addAction("退出", self.close)
        menu.exec(QCursor.pos())

    def _run_chosen(self, action: str):
        self._back_to_idle.stop()          # 取消残留的「回待机」定时
        if action == "idle":
            self._to_idle()
            return
        self.set_action(action)
        ms = ACTION_MS.get(action)
        if ms:
            self._back_to_idle.start(ms)

    # ---------- 拖拽看门狗：松手兜底 ----------
    def _on_drag_watch(self):
        if self._pressed and self._moved:
            if time.monotonic() - self._last_move > DRAG_WATCH_MS / 1000:
                self._end_drag()

    def _end_drag(self):
        self._pressed = False
        self._moved = False
        if self._grabbed:
            try:
                self.releaseMouse()
            except (RuntimeError, TypeError):
                pass
            self._grabbed = False
        self._drag_watch.stop()
        self._to_idle()

    # ---------- 鼠标事件 ----------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._back_to_idle.stop()
            self._pressed = True
            self._moved = False
            self._last_move = time.monotonic()
            self._press_pos = event.globalPosition().toPoint()
            self._drag_offset = (
                    self._press_pos - self.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):
        if self._pressed and event.buttons() & Qt.LeftButton:
            self._last_move = time.monotonic()
            dist = (event.globalPosition().toPoint()
                    - self._press_pos).manhattanLength()
            if dist > DRAG_THRESHOLD and not self._moved:
                self._moved = True
                self.grabMouse()
                self._grabbed = True
                self._drag_watch.start()
                self.set_action("drag")
            if self._moved:
                self.move(event.globalPosition().toPoint()
                          - self._drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._pressed:
            if not self._moved:
                # 纯单击 -> 播放点击回应动画，3 秒后回待机
                self._pressed = False
                self.set_action("click")
                self._back_to_idle.start(ACTION_MS.get("click", 3000))
            else:
                # 拖拽结束 -> 立即回待机
                self._end_drag()
            event.accept()

    def contextMenuEvent(self, event):
        # 右键 -> 弹出动作选择菜单
        self._back_to_idle.stop()
        self._show_action_menu()
        event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PetWindow()
    win.show()
    sys.exit(app.exec())
