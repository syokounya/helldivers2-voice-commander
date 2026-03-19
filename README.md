# 🎮 绝地潜兵2 语音战备助手

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

通过语音指令快速呼叫战备，解放双手，提升游戏体验！

</div>

---

## 📖 简介

用语音代替键盘输入战备序列。说出战备名称，程序自动发送按键到游戏。支持模糊匹配和上下文智能切换。

> 说「机炮」→ 自动输入按键序列 → 呼叫机炮战备 ✅

---

## ✨ 核心特性

- 🎤 **双模式语音识别**
  - ☁️ 阿里云在线识别 — 高准确率，需要网络和账号
  - 💾 Vosk 离线识别 — 完全离线，无需账号
- 🎯 **智能匹配** — 支持模糊匹配、前缀匹配、拼音匹配
- 🔄 **上下文感知** — 重复说同一关键词自动切换相似战备
- 🔊 **音频优化** — 内置降噪、回音消除、噪音门
- 🛠️ **指令编辑器** — 可视化编辑战备列表，支持热更新
- 🔒 **隐私保护** — 配置文件加密存储，一键清除

---

## 📦 快速开始

### 方法一：下载可执行文件（推荐）

1. 前往 [Releases](https://github.com/syokounya/helldivers2-voice-commander/releases) 页面
2. 下载最新版本的 `Helldiver-Voice-Commander-vX.X.X.7z`
3. 解压到任意目录
4. 运行 `Helldiver Voice Assistant.exe`
5. 在「设置」Tab 中选择识别模式并完成配置
6. 开始使用！

### 方法二：从源码运行

```bash
git clone https://github.com/syokounya/helldivers2-voice-commander.git
cd helldivers2-voice-commander
pip install -r requirements.txt
python main_modular.py
```

---

## ⚙️ 识别模式配置

### 模式一：阿里云在线识别（推荐）

**优点**：准确率高、支持云端降噪  
**缺点**：需要网络连接和阿里云账号

**配置步骤**：
1. 登录 [阿里云控制台](https://www.aliyun.com/)，开通「智能语音交互」服务
2. 创建项目（类型选「实时语音转写」），获取：
   - APP KEY
   - Access Key ID
   - Access Key Secret
3. 在程序「设置」Tab 选择「阿里云在线识别」，填入凭证保存

### 模式二：Vosk 离线识别

**优点**：完全离线，无需账号  
**缺点**：准确率略低，需下载模型（约 50MB）

**配置步骤**：
1. 访问 [Vosk 模型下载页面](https://alphacephei.com/vosk/models)
2. 下载中文模型：`vosk-model-cn-0.22`
3. 解压到程序根目录下的 `./vosk` 文件夹，结构如下：
   ```
   程序根目录/
   ├── vosk/
   │   ├── am/
   │   ├── conf/
   │   ├── graph/
   │   └── ivector/
   └── Helldiver Voice Assistant.exe
   ```
4. 在程序「设置」Tab 选择「Vosk 离线识别」即可

---

## 🎮 使用方法

1. 在「主界面」Tab 配置本局战备槽位（共 4 个）
2. 勾选需要的全局指令（增援、补给等）
3. 点击「开始监听」
4. 进入游戏，按住 `Ctrl` 键说出战备名称
5. 程序自动发送按键序列

### 匹配技巧

| 说法 | 匹配结果 |
|------|----------|
| 「机炮」 | 机炮哨戒 |
| 「飞鹰」 | 飞鹰500kg炸弹（或其他飞鹰战备） |
| 「加特林」 | 加特林哨戒 / 轨道加特林（上下文轮换） |
| 「补给」 | 补给战备（全局指令） |

---

## 🔧 系统要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 10 / 11 |
| Python | 3.8+（仅源码运行需要）|
| 麦克风 | 任意设备 |
| 网络 | 阿里云模式需要，Vosk 模式不需要 |
| 内存 | 建议 2GB 以上 |
| 磁盘 | Vosk 模式额外需要 50MB |

---

## 📝 常见问题

**Q：识别不准确？**  
A：检查麦克风音量，启用「设置」中所有音频处理选项，在安静环境下使用。

**Q：按键无法发送到游戏？**  
A：若游戏以管理员权限运行，本程序也需要以管理员身份运行（右键 → 以管理员身份运行）。

**Q：如何分享给朋友？**  
A：在「设置」Tab 点击「清除隐私信息」后，直接分享压缩包即可。对方需自行配置阿里云密钥（或使用 Vosk 离线模式）。

**Q：提示「模型路径不存在」？**  
A：确认 `vosk` 文件夹在程序根目录下，且包含 `am`、`conf`、`graph` 等子文件夹，参考 [VOSK_README.md](VOSK_README.md)。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 `git checkout -b feature/xxx`
3. 提交更改并推送
4. 打开 Pull Request

---

## 📄 许可证

MIT License — 详见 [LICENSE](LICENSE)

## 🙏 致谢

- [阿里云智能语音服务](https://www.aliyun.com/product/nls)
- [Vosk 离线语音识别](https://alphacephei.com/vosk/)
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)

---

<div align="center">

如果这个项目对你有帮助，欢迎点个 ⭐ Star！

[提交问题](https://github.com/syokounya/helldivers2-voice-commander/issues)

</div>
