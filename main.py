# -*- coding: utf-8 -*-
"""
大肥鱼 · 设置窗口 + 关于窗口
=============================
用 PySide6 的 QWebEngineView 加载 settings.html（浅色系），前端用 QWebChannel
通过 backend 对象调用 Python 处理事件。

两个窗口都：
- 隐藏系统自带标题栏（导航栏），换成自定义标题栏（可拖动、圆形按钮）
- 背景浅色（白色/浅灰），整体加一点圆角
- 图标统一使用 images/tb.webp

前端可用方法（见 settings.html）：
    backend.get_settings(cb(json))   -> 读取当前设置（JSON 字符串）
    backend.save_settings(json)      -> 保存设置并写入 settings.json
    backend.open_website(url)        -> 用系统默认浏览器打开网址
    backend.open_about()             -> 弹出「关于」窗口（独立小窗口）

依赖安装：
    pip install PySide6 PySide6-Addons PySide6-Essentials
"""

import json
import os
import sys

from PySide6.QtCore import (
    Qt, QUrl, QObject, Slot, QStandardPaths, QPointF, QRect, QRectF,
)
from PySide6.QtGui import (
    QColor, QDesktopServices, QIcon, QLinearGradient, QPainter, QPen,
    QPolygonF, QPixmap, QRegion,
)
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QPushButton,
    QVBoxLayout, QWidget,
)
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineWidgets import QWebEngineView

# ============ 应用信息（想改名只改这两处） ============
APP_NAME = "大肥鱼"
APP_VERSION = "1.0"

# 关于窗口
SUPPORT_URL = "https://huiyi0923.github.io/jszc.html"

# 应用图标 images/tb.webp（相对于当前目录或本文件目录，取第一个存在的）
def _app_icon_path():
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in (os.path.join(os.getcwd(), "images", "tb.webp"),
                 os.path.join(here, "images", "tb.webp"),
                 os.path.join(here, "..", "images", "tb.webp")):
        if os.path.exists(cand):
            return cand
    return os.path.join(here, "images", "tb.webp")


APP_ICON_PATH = _app_icon_path()


def app_icon():
    """返回 QIcon（images/tb.webp）；文件不存在则返回空图标。"""
    return QIcon(APP_ICON_PATH)


def load_icon(size=40):
    """返回缩放后的 QPixmap；若 tb.webp 缺失则退回手绘小鱼。"""
    pm = QPixmap(APP_ICON_PATH)
    if pm.isNull():
        return make_fish_icon(size)
    return pm.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)


# 默认设置（默认宠物大小 180）
DEFAULT_SETTINGS = {
    "talkInterval": 20,   # 每隔多少秒碎碎念一次
    "petSize": 180,       # 宠物显示尺寸（像素）
    "showTalk": True,     # 是否显示碎碎念文字气泡
    "alwaysTop": True,    # 窗口是否置顶
    "websites": [         # 网站列表
        {"name": "个人主页", "url": "https://suyanxi.top"},
        {"name": "github源码", "url": "https://github.com/huiyi0923/Desktop-Widget---Anime"},
    ],
}


def _config_path():
    """settings.json 放在用户配置目录下，不随代码文件走。"""
    base = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppConfigLocation
    )
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "pet_settings.json")


# ============ 圆角窗口区域（把方角抠成圆角） ============
def rounded_region(w, h, r):
    reg = QRegion()
    reg = reg.united(QRegion(r, 0, max(0, w - 2 * r), h))          # 中间竖条
    reg = reg.united(QRegion(0, r, w, max(0, h - 2 * r)))          # 中间横条
    for cx, cy in ((r, r), (w - r, r), (r, h - r), (w - r, h - r)):  # 四个圆角
        reg = reg.united(QRegion(QRect(cx - r, cy - r, 2 * r, 2 * r),
                                 QRegion.RegionType.Ellipse))
    return reg


# ============ 备用：手绘小鱼图标（tb.webp 缺失时才用） ============
def make_fish_icon(size=40, radius_ratio=0.24):
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    grad = QLinearGradient(0, 0, size, size)
    grad.setColorAt(0, QColor(139, 124, 246))
    grad.setColorAt(1, QColor(167, 139, 250))
    p.setBrush(grad)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(QRectF(0, 0, size, size),
                      size * radius_ratio, size * radius_ratio)
    p.setBrush(QColor(255, 255, 255))
    s = float(size)
    p.drawEllipse(QRectF(s * 0.24, s * 0.30, s * 0.52, s * 0.40))
    p.drawPolygon(QPolygonF([
        QPointF(s * 0.26, s * 0.50),
        QPointF(s * 0.08, s * 0.30),
        QPointF(s * 0.08, s * 0.70),
    ]))
    p.drawPolygon(QPolygonF([
        QPointF(s * 0.50, s * 0.30),
        QPointF(s * 0.52, s * 0.16),
        QPointF(s * 0.62, s * 0.34),
    ]))
    p.setBrush(QColor(255, 255, 255))
    p.drawEllipse(QRectF(s * 0.62, s * 0.40, s * 0.10, s * 0.10))
    p.setBrush(QColor(30, 30, 40))
    p.drawEllipse(QRectF(s * 0.655, s * 0.43, s * 0.05, s * 0.05))
    p.end()
    return pm


# ============ 自定义标题栏（可拖动 + 圆形按钮） ============
class TitleBar(QWidget):
    def __init__(self, win, title, icon_pm=None,
                 buttons=("min", "max", "close"), colored=True):
        super().__init__(win)
        self.win = win
        self._drag = False
        self._start = None
        self.setFixedHeight(44)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 0, 12, 0)
        lay.setSpacing(8)
        if icon_pm is not None:
            ic = QLabel(self)
            ic.setPixmap(icon_pm)
            lay.addWidget(ic)
        t = QLabel(title, self)
        lay.addWidget(t)
        lay.addStretch(1)

        for name in buttons:
            b = QPushButton(self)
            b.setFixedSize(26, 26)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setObjectName(name)
            if name == "min":
                b.setText("─")
            elif name == "max":
                b.setText("□")
            else:
                b.setText("✕")
            if name == "min":
                b.clicked.connect(win.showMinimized)
            elif name == "max":
                b.clicked.connect(self._toggle_max)
            else:
                b.clicked.connect(win.close)
            lay.addWidget(b)

        if colored:
            # 设置窗口：最小化/最大化/关闭用不同底色区分
            self.setStyleSheet("""
                QLabel { background: transparent; color:#1f2937;
                         font-size:13.5px; font-weight:600; }
                QPushButton { border:none; border-radius:13px;
                              color:#374151; font-size:14px; }
                QPushButton#min   { background:#e5e7eb; }
                QPushButton#min:hover   { background:#d1d5db; }
                QPushButton#max   { background:#c7d2fe; }
                QPushButton#max:hover   { background:#a5b4fc; }
                QPushButton#close { background:#fecaca; }
                QPushButton#close:hover { background:#fca5a5; }
            """)
        else:
            # 关于窗口：只有最小化/关闭，都用灰色，不区分底色
            self.setStyleSheet("""
                QLabel { background: transparent; color:#1f2937;
                         font-size:12.5px; }
                QPushButton { border:none; border-radius:13px;
                              color:#374151; font-size:14px; background:#e5e7eb; }
                QPushButton:hover { background:#d1d5db; }
            """)

    def _toggle_max(self):
        if self.win.isMaximized():
            self.win.showNormal()
        else:
            self.win.showMaximized()
        self.win._apply_rounded()

    # -------- 拖动窗口 --------
    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag = True
            self._start = (e.globalPosition().toPoint()
                           - self.win.frameGeometry().topLeft())
            e.accept()

    def mouseMoveEvent(self, e):
        if self._drag and e.buttons() & Qt.MouseButton.LeftButton:
            self.win.move(e.globalPosition().toPoint() - self._start)
            e.accept()

    def mouseReleaseEvent(self, e):
        self._drag = False
        e.accept()


# ============ Python 后端（前端 JS 通过 QWebChannel 调用） ============
class Backend(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = dict(DEFAULT_SETTINGS)
        self._load()

    def _load(self):
        path = _config_path()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for k, v in data.items():
                    self.settings[k] = v
            except Exception as e:
                print("[设置] 读取配置失败，使用默认值：", e)

    def _save(self):
        path = _config_path()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)
        print("[设置] 已保存到", path)

    @Slot(result=str)
    def get_settings(self):
        """前端初始化时调用，返回设置 + 应用名/版本（JSON）。"""
        data = dict(self.settings)
        data["appName"] = APP_NAME
        data["appVersion"] = APP_VERSION
        return json.dumps(data, ensure_ascii=False)

    @Slot(str)
    def save_settings(self, json_str):
        try:
            data = json.loads(json_str)
            self.settings.update(data)
            self._save()
        except Exception as e:
            print("[设置] 保存失败：", e)

    @Slot(str)
    def open_website(self, url):
        print("[打开网站]", url)
        QDesktopServices.openUrl(QUrl(url))

    @Slot()
    def open_about(self):
        print("[关于] 弹出关于窗口")
        win = AboutWindow()
        win.show()


# ============ 设置主窗口 ============
class MainWin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} · 设置")
        self.setWindowIcon(app_icon())
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.backend = Backend()
        self.channel = QWebChannel()
        self.channel.registerObject("backend", self.backend)

        self.webview = QWebEngineView()
        # 直接用 webview 自带的 page，不要另建 QWebEnginePage
        self.webview.page().setWebChannel(self.channel)
        base = os.path.dirname(os.path.abspath(__file__))
        self.webview.load(QUrl.fromLocalFile(os.path.join(base, "settings.html")))

        # 外层圆角浅色容器
        outer = QFrame(self)
        outer.setObjectName("outer")
        outer.setStyleSheet(
            "#outer { background:#f7f8fc;"
            "border:1px solid rgba(15,23,42,.08);"
            "border-radius:14px; }"
        )
        v = QVBoxLayout(outer)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)
        v.addWidget(TitleBar(self, f"{APP_NAME} · 设置",
                             icon_pm=load_icon(24),
                             buttons=("min", "max", "close"), colored=True))
        v.addWidget(self.webview, 1)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(outer)

        self.resize(880, 600)
        self._apply_rounded()

    def _apply_rounded(self):
        # 最大化时不圆角，恢复时再圆角
        if self.isMaximized():
            self.clearMask()
        else:
            self.setMask(rounded_region(self.width(), self.height(), 14))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_rounded()


# ============ 关于窗口（小、竖着 2:3、只有最小化/关闭） ============
class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"关于 {APP_NAME}")
        self.setWindowIcon(app_icon())
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        outer = QFrame(self)
        outer.setObjectName("outer")
        outer.setStyleSheet(
            "#outer { background:#f7f8fc;"
            "border:1px solid rgba(15,23,42,.08);"
            "border-radius:14px; }"
        )
        v = QVBoxLayout(outer)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)
        v.addWidget(TitleBar(self, f"关于 {APP_NAME}",
                             buttons=("min", "close"), colored=False))
        v.addWidget(self._content(), 1)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(outer)

        # 竖着 2:3（300 × 450）
        self.resize(300, 450)
        self._apply_rounded()

    def _content(self):
        box = QWidget(self)
        box.setStyleSheet("background:transparent;")
        c = QVBoxLayout(box)
        c.setContentsMargins(24, 6, 24, 18)
        c.setSpacing(4)

        icon = QLabel(box)
        icon.setPixmap(load_icon(84))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c.addWidget(icon)

        name = QLabel(APP_NAME, box)
        name.setStyleSheet("font-size:22px;font-weight:700;color:#1f2937;")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c.addWidget(name)

        ver = QLabel(f"版本 {APP_VERSION}", box)
        ver.setStyleSheet("font-size:12.5px;color:#7c6cf0;")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c.addWidget(ver)
        c.addSpacing(14)

        info1 = QLabel("本软件 GIF 由 AI 生成，\n源代码可在 GitHub 免费下载。", box)
        info1.setStyleSheet("font-size:13px;color:#5b6574;")
        info1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info1.setWordWrap(True)
        c.addWidget(info1)

        warn = QLabel("如果你是付费获得的，那你被骗了。", box)
        warn.setStyleSheet("font-size:13px;color:#dc2626;")
        warn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warn.setWordWrap(True)
        c.addWidget(warn)

        c.addStretch(1)

        # 最底下一行版权声明：中文版权 + 英文版权 + 可点击的「微清技术支持部」
        foot = QLabel(
            f"© 2026 {APP_NAME} · Copyright © 2026 Weiqing Network All Rights "
            f"Reserved · "
            f"<a href=\"{SUPPORT_URL}\" style=\"color:#7c6cf0;\">微清技术支持部</a>",
            box,
        )
        foot.setStyleSheet("font-size:11px;color:#9aa4b0;")
        foot.setTextFormat(Qt.TextFormat.RichText)
        foot.setOpenExternalLinks(False)
        foot.setWordWrap(True)
        foot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        foot.linkActivated.connect(
            lambda url: QDesktopServices.openUrl(QUrl(url)))
        c.addWidget(foot)

        return box

    def _apply_rounded(self):
        if self.isMaximized():
            self.clearMask()
        else:
            self.setMask(rounded_region(self.width(), self.height(), 14))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_rounded()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationDisplayName(APP_NAME)
    app.setApplicationName(APP_NAME)
    app.setWindowIcon(app_icon())
    w = MainWin()
    w.show()
    sys.exit(app.exec())
#（注：内容由AI生成）
