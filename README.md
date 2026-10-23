# 大肥鱼 · PySide6 桌面猫娘宠物（透明宠物挂件 / Desktop Pet）

> 一只住在你桌面角落、会自己碎碎念、能被你拖动、会跳舞睡觉的二次元猫娘桌面宠物。
基于 **Python + PySide6** 开发，窗口完全透明、隐藏系统标题栏，播放 **AI 生成的透明 GIF 动画**。

<div align="center">

![大肥鱼](./images/tb.webp)

**版本 v1.0** ｜ **作者：Yanxi** ｜ **个人网站：[https://suyanxi.top](https://suyanxi.top)**

</div>

***

## 目录

- [项目简介](#%E9%A1%B9%E7%9B%AE%E7%AE%80%E4%BB%8B)
- [核心特性](#%E6%A0%B8%E5%BF%83%E7%89%B9%E6%80%A7)
- [运行效果](#%E8%BF%90%E8%A1%8C%E6%95%88%E6%9E%9C)
- [环境要求](#%E7%8E%AF%E5%A2%83%E8%A6%81%E6%B1%82)
- [快速开始](#%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B)
- [目录结构](#%E7%9B%AE%E5%BD%95%E7%BB%93%E6%9E%84)
- [鼠标交互说明](#%E9%BC%A0%E6%A0%87%E4%BA%A4%E4%BA%92%E8%AF%B4%E6%98%8E)
- [动作动画列表](#%E5%8A%A8%E4%BD%9C%E5%8A%A8%E7%94%BB%E5%88%97%E8%A1%A8)
- [设置窗口](#%E8%AE%BE%E7%BD%AE%E7%AA%97%E5%8F%A3)
- [自定义与二次开发](#%E8%87%AA%E5%AE%9A%E4%B9%89%E4%B8%8E%E4%BA%8C%E6%AC%A1%E5%BC%80%E5%8F%91)
- [常见问题 FAQ](#%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98-faq)
- [免责声明](#%E5%85%8D%E8%B4%A3%E5%A3%B0%E6%98%8E)
- [开源许可](#%E5%BC%80%E6%BA%90%E8%AE%B8%E5%8F%AF)

***

## 项目简介

**大肥鱼**（英文名 **Big Fat Fish / Dafeiyu**）是一款运行在 **Windows**桌面上的\*\*透明桌面宠物（Desktop Pet / Desktop Widget / Desktop Mascot）\*\*程序。

它以 **DeepSeek 风格的猫娘（catgirl / kemonomimi）二次元形象**为基础，形象与全部动作动画均由 **AI 辅助生成**。程序使用 **Python / PySide6（Qt for Python）** 实现：

- 将窗口背景设置为**全透明**，并**隐藏 Windows 系统自带的标题栏（导航栏）**；
- 通过播放 **透明背景 GIF** 呈现猫娘的各种动作；
- 支持鼠标**点击、拖拽、右键菜单**等交互，待机时会**自动碎碎念**并在左上角弹出文字气泡；
- 内置一个用 **HTML + QWebChannel** 实现的**美化设置窗口**，告别原生控件丑陋外观。

项目代码结构清晰、注释完整，适合 **Python 桌面开发学习者**、**PySide6 爱好者**、**二次元 / Vtuber 衍生周边**创作者参考与二次开发。

***

## 核心特性

- 🪟 **透明无边框窗口**：`FramelessWindowHint + WA_TranslucentBackground`，整个窗口任意形状，只显示猫娘本身。
- 🎞️ 6 **种 GIF 动作动画**：待机（idle）、点击回应（click）、拖拽（drag）、碎碎念（talk）、跳舞（dance）、睡觉（sleep）、开心蹦跳（happy）。
- 🖱️ **丰富的鼠标交互**：左键单击回应、按住拖动、右键弹出美化菜单、双击退出。
- 💬 **自动碎碎念气泡**：待机每隔 20 秒随机显示一句话，文字出现在宠物左上角。
- 📋 **美化右键菜单**：圆角样式、灰色分隔线（左右留白）、悬停变灰、字体紧凑小巧。
- ⚙️ **HTML 设置窗口**：基于 `QWebEngineView + QWebChannel`，前端 HTML/CSS 控制界面，后端 Python 处理事件，浅色系双栏设计。
- 🐟 **统一应用图标**：窗口 / 设置 / 关于 / 页面 favicon 统一使用 `images/tb.webp` 猫娘图标。
- 🪄 **高清防模糊渲染**：针对 Windows 高分屏（125% / 150% 缩放）专门做了 `SmoothTransformation + DevicePixelRatio` 平滑缩放，彻底解决 GIF 放大变糊问题。
- 🔁 **状态机式动作切换**：每个动作播完自动回待机；拖拽松手立即回待机，不会卡在某个动画上。
- 🧩 **模块化结构**：宠物主程序 / 设置窗口 / 关于窗口 / HTML 页面分层清晰，易于扩展。

***

## 运行效果

> 说明：以下为本程序实际运行效果展示（透明背景 GIF 由 AI 生成）。

| 动作 | 触发方式 | 预览文件 |
| --- | --- | --- |
| 待机 | 鼠标不动 | `idle.gif` |
| 点击回应 | 左键单击 | `click.gif` |
| 拖拽动画 | 按住左键拖动 | `drag.gif` |
| 碎碎念说话 | 待机自动 / 菜单 | `talk.gif` |
| 跳舞 | 右键菜单 | `dance.gif` |
| 睡觉 | 右键菜单 | `sleep.gif` |
| 开心蹦跳 | 右键菜单 | `happy.gif` |

***

## 环境要求

- **操作系统**：Windows 10/11（推荐）
- **Python**：3.9 及以上
- **依赖库**：`PySide6`（包含 QtWebEngine）

> 提示：窗口置顶、透明、隐藏标题栏在 Linux 部分桌面环境可能受限，建议以 Windows 为主运行环境。

***

## 快速开始

### 1. 克隆 / 下载项目

```bash
git clone https://github.com/huiyi0923/Desktop-Widget---Anime.git
cd Desktop-Widget---Anime/pyside6
```

### 2. 安装依赖

```bash
pip install PySide6 PySide6-Addons PySide6-Essentials
```

### 3. 运行宠物

```bash
python 大肥鱼.py
```

启动后，一只透明背景的猫娘就会出现在桌面角落，默认置顶显示。

> 首次运行如果报 `QWebEngine` 相关错误，请确认 `PySide6-Addons`、`PySide6-Essentials` 已完整安装。

***

## 目录结构

```
pyside6/
├── 大肥鱼.py              # 主程序：桌面宠物（窗口 + GIF + 交互 + 右键菜单）
├── ui/
│   ├── main.py            # 设置窗口 + 关于窗口（QWebEngineView + QWebChannel）
│   └── settings.html      # 设置页面（浅色系双栏 UI）
├── images/
│   └── tb.webp            # 应用图标（DeepSeek 风格猫娘）
├── gif/
│   ├── idle.gif               # 待机 / 小动作
│   ├── click.gif              # 点击回应
│   ├── drag.gif               # 拖拽动画
│   ├── talk.gif               # 碎碎念说话
│   ├── dance.gif              # 跳舞
│   ├── sleep.gif              # 睡觉
│   ├── happy.gif              # 开心蹦跳
│   └── angry.gif              # 生气（等待后续添加）
```

***

## 鼠标交互说明

| 操作 | 触发动作 | 说明 |
| --- | --- | --- |
| 鼠标不动 | 待机（idle） | 默认状态，每隔 20 秒自动碎碎念一次 |
| 左键单击 | 点击回应（click） | 播放 3 秒后自动回待机 |
| 按住左键拖动 | 拖拽动画（drag） | 拖动过程中播放，松手立即回待机 |
| 右键单击 | 弹出动作菜单 | 选择跳舞 / 睡觉 / 开心 / 设置 / 退出 |
| 双击左键 | 退出程序 | 关闭宠物 |
| 待机超时 | 碎碎念（talk） | 左上角随机显示一句台词 |

> **动作恢复机制**：所有一次性动作（点击、碎碎念、跳舞、睡觉等）播完后都会通过定时器自动切回待机；拖拽使用「看门狗」检测鼠标停止移动，即使漏掉 MouseRelease 也能自动回待机。此机制已在多轮迭代中重点修复，不会再出现「卡在某个动画回不到待机」的问题。

***

## 动作动画列表

`大肥鱼.py` 顶部定义了动作映射与播放时长，可按需增删：

```python
GIF_FILES = {
    "idle": "idle.gif",   # 待机
    "click": "click.gif", # 点击回应
    "drag": "drag.gif",   # 拖拽
    "talk": "talk.gif",   # 碎碎念
    "dance": "dance.gif", # 跳舞
    "sleep": "sleep.gif", # 睡觉
    "happy": "happy.gif", # 开心
}
```

缺失的 GIF 会自动从右键菜单隐藏，程序不会报错。

***

## 设置窗口

在宠物上**右键 → 设置**，即可打开「大肥鱼 · 设置」窗口。该窗口：

- 采用 **HTML + CSS** 渲染界面（浅色系、圆角、双栏布局），比原生控件美观；
- 通过 **QWebChannel** 与 Python 后端交互，实现：

| 设置项 | 说明 |
| --- | --- |
| 碎碎念间隔 | 每隔多少秒自动说话一次 |
| 宠物大小 | 显示尺寸（像素），默认 180 |
| 显示文字气泡 | 是否显示碎碎念文字 |
| 窗口置顶 | 是否始终显示在最前面 |
| 网站列表 | 可打开的个人主页 / GitHub 源码等链接 |

设置会保存到用户配置目录下的 `pet_settings.json`，重启后依然生效。

「关于」窗口为独立小窗（300 × 450，竖 2:3），只含最小化 / 关闭，展示版权与免责声明。

***

## 自定义与二次开发

### 更换猫娘形象 / GIF

把新的透明 GIF 放到 `pyside6/` 目录并替换对应文件名即可，例如替换 `idle.gif` 即为新的待机动画。

### 修改碎碎念台词

编辑 `大肥鱼.py` 中的 `TALK_TEXTS` 列表：

```python
TALK_TEXTS = [
    "要吃更多token～",
    "主人，摸摸头嘛～",
    "今天也要加油喵！",
    # ... 随意添加
]
```

### 修改默认设置

编辑 `main.py` 中的 `DEFAULT_SETTINGS` 字典，可调整默认大小、碎碎念间隔、默认网站列表等。

### 更换应用图标

统一替换 `images/tb.webp` 即可，宠物窗口、设置窗口、关于窗口、页面 favicon 会自动同步。

### 增加新动作

1. 把 GIF 放到目录下；
2. 在 `GIF_FILES` 和 `ACTION_LABELS` 中登记动作；
3. 可选：在 `ACTION_MS` 设置该动作的播放时长。

***

## 常见问题 FAQ

**Q1：GIF 在图片查看器里清晰，但运行到程序里很糊？**
A：这是高分屏缩放导致的。本程序已内置平滑缩放 + DPR 适配，请使用最新版 `大肥鱼.py`，不要用 `label.setScaledContents(True)`（快速缩放，低质量）。

**Q2：拖拽后回不到待机？**
A：旧版本存在此问题，已通过「看门狗 + 状态机」修复。请更新到 v1.0 的 `大肥鱼.py`。

**Q3：GIF 没有加载出来？**
A：确认 GIF 与 `大肥鱼.py` 在同一目录，且文件名与 `GIF_FILES` 映射一致。

**Q4：`from ui.main import ...` 报错？**
A：确保 `大肥鱼.py` 与 `ui/` 文件夹在同一级目录，且目录名是 `ui`（不要用 `html`，会与 Python 标准库重名）。

**Q5：`cannot import name 'QPointF' from 'PySide6.QtGui'`？**
A：Qt6 中 `QPointF / QRect / QRectF` 在 `PySide6.QtCore`，本项目代码已按此分块导入，更新代码即可。

**Q6：右键菜单太大了？**
A：本项目已把菜单样式缩小（圆角 9px、紧凑内边距、12px 字号），如需微调改 `大肥鱼.py` 中的 `MENU_QSS`。

***

## 免责声明

- **代码由 AI 辅助生成**：本项目（Python / PySide6 源码、GIF 动画、猫娘形象）均由 AI 辅助完成，仅供学习、研究、个人娱乐与二次开发参考。
- **形象来源**：宠物形象基于 **DeepSeek 风格的猫娘（catgirl）二次元形象**，由 AI 生成。
- **禁止商用**：本项目**禁止任何形式的商业使用**（包括但不限于出售、打包收费、企业内使用、广告投放、以此牟利的衍生品等）。
- **免费声明**：本项目源码可在 GitHub 免费下载。**如果你是付费获得的，那么你被骗了。** 请向「yanxi@suyanxi.top」举报或反馈。
- 本软件 GIF 由 AI 生成，可能与原画存在差异，请以实际运行效果为准。

***

## 开源许可

本软件遵循 **自定义禁止商用许可证（Custom No-Commercial License）**：

- ✅ 允许：个人学习、研究、收藏、非商业二次开发、非商业分享。
- ❌ 禁止：任何形式的**商用**、转售、收取会员费 / 授权费、企业项目内置使用、广告牟利。
- 📌 保留版权声明：`© 2026 大肥鱼 · Copyright © 2026 Weiqing Network All Rights Reserved`

商用授权与合作请联系「微清技术支持部」（见关于窗口）。

***

## 关于项目

- **开发者**：Yanxi
- **技术维护**：微清网络（MicroCent Network）
- **开源地址**：[GitHub](https://github.com/huiyi0923/Desktop-Widget---Anime)

如果这个猫娘宠物让你开心，欢迎 Star ⭐ 和 Fork，也欢迎提交 Issue 反馈问题或想法。

***

## SEO 关键词

`桌面宠物` `桌面挂件` `PySide6` `Python` `Qt` `Qt6` `桌面猫娘` `猫娘` `catgirl` `二次元` `透明窗口` `无边框窗口` `GIF 宠物` `桌面宠物动画` `Desktop Pet` `Desktop Widget` `Desktop Mascot` `Desktop Pet GIF` `Widget` `Windows` `macOS` `Linux` `QWebChannel` `QWebEngineView` `DeepSeek` `AI 生成` `透明宠物` `桌面精灵` `Anime` `Kemonomimi` `Tray Icon` `桌面宠物程序` `宠物源码` `免费开源`
