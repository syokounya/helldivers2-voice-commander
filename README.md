# 🎮 Helldivers 2 Voice Commander

<div align="center">

**语音控制战备系统 | Voice-Controlled Stratagem System**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

[English](#english) | [中文](#中文)

</div>

---

## 中文

### 📖 简介

**Helldivers 2 Voice Commander** 是一个基于语音识别的《绝地潜兵2》战备助手。通过语音指令快速呼叫战备，解放双手，提升游戏体验！

### ✨ 核心特性

- 🎤 **实时语音识别** - 基于阿里云智能语音服务，识别准确快速
- 🎯 **智能匹配系统** - 支持模糊匹配、前缀匹配、拼音匹配
- 🔄 **上下文感知** - 自动记忆最近使用的战备，智能切换相似战备
- 🎨 **现代化 GUI** - 简洁美观的图形界面，支持窗口缩放
- 🔊 **音频优化** - 内置降噪、回音消除、噪音门等音频处理
- 🔒 **隐私保护** - 配置文件加密存储，支持一键清除隐私信息
- ⚡ **轻量高效** - 低资源占用，不影响游戏性能

### 🎬 演示

> 说"机炮" → 自动输入按键序列 → 呼叫机炮战备 ✅

### 📦 快速开始

#### 方法 1：下载可执行文件（推荐）

1. 前往 [Releases](https://github.com/你的用户名/helldivers2-voice-commander/releases) 页面
2. 下载最新版本的 `Helldivers2-Voice-Commander-vX.X.X.zip`
3. 解压到任意目录
4. 运行 `Helldivers2-Voice-Commander.exe`
5. 在"设置"Tab 中配置阿里云密钥
6. 开始使用！

#### 方法 2：从源码运行

```bash
# 克隆仓库
git clone https://github.com/你的用户名/helldivers2-voice-commander.git
cd helldivers2-voice-commander

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main_modular.py
```

### ⚙️ 配置说明

#### 1. 获取阿里云密钥

1. 登录 [阿里云控制台](https://www.aliyun.com/)
2. 开通"智能语音交互"服务
3. 创建项目（项目类型：实时语音转写）
4. 获取以下凭证：
   - **APP KEY**
   - **Access Key ID**
   - **Access Key Secret**

#### 2. 配置程序

1. 打开程序，切换到"设置"Tab
2. 填写阿里云凭证
3. 点击"保存配置"
4. 配置会加密保存在本地

### 🎮 使用方法

#### 基础使用

1. 在"主界面"Tab 配置本局战备（4个槽位）
2. 勾选需要的全局指令（增援、补给等）
3. 点击"开始监听"
4. 进入游戏，按住 `Ctrl` 键说话
5. 说出战备名称（如"机炮"、"轨道炮"）
6. 自动输入按键序列

#### 高级技巧

- **模糊匹配**：说"弹链"可以匹配"弹链榴弹发射器"
- **前缀匹配**：说"飞鹰"可以匹配"飞鹰500kg炸弹"
- **智能切换**：重复说"加特林"会自动切换到"轨道加特林"、"重装加特林"
- **上下文权重**：最近使用的战备会优先匹配

### 🎯 支持的战备

- ✅ 所有支援武器（机炮、重机枪、榴弹发射器等）
- ✅ 所有轨道打击（轨道炮、轨道加特林等）
- ✅ 所有飞鹰打击（飞鹰500kg炸弹、飞鹰空袭等）
- ✅ 所有防御建筑（哨戒炮、护盾发生器等）
- ✅ 所有背包和载具
- ✅ 全局指令（增援、补给、SOS等）

完整列表请查看 [stratagems.json](stratagems.json)

### 🔧 系统要求

- **操作系统**：Windows 10/11
- **Python**：3.8 或更高版本（仅源码运行需要）
- **麦克风**：任意麦克风设备
- **网络**：需要连接互联网（调用阿里云 API）
- **内存**：建议 2GB 以上

### 📝 常见问题

#### Q: 识别不准确怎么办？

A: 
1. 检查麦克风音量是否合适
2. 启用"音频处理设置"中的所有选项
3. 尽量在安静环境下使用
4. 说话清晰，语速适中

#### Q: 按键无法发送到游戏？

A: 
1. 确保游戏窗口处于活动状态
2. 如果游戏以管理员权限运行，本程序也需要以管理员权限运行
3. 右键程序 → 以管理员身份运行

#### Q: 如何分享给朋友？

A: 
1. 在"设置"Tab 点击"清除隐私信息"
2. 分享整个文件夹
3. 接收者需要配置自己的阿里云密钥

#### Q: 支持其他语音识别服务吗？

A: 目前仅支持阿里云。如需其他服务，可以修改 `modules/aliyun_asr.py`

### 🤝 贡献

欢迎提交 Issue 和 Pull Request！

#### 如何贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

### 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

### 🙏 致谢

- [阿里云智能语音服务](https://www.aliyun.com/product/nls)
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/)
- [pynput](https://github.com/moses-palmer/pynput)

### 📞 联系方式

- **GitHub Issues**: [提交问题](https://github.com/你的用户名/helldivers2-voice-commander/issues)
- **Email**: your.email@example.com

### ⚠️ 免责声明

本项目仅供学习交流使用，不得用于商业用途。使用本软件产生的任何后果由使用者自行承担。

---

## English

### 📖 Introduction

**Helldivers 2 Voice Commander** is a voice-controlled stratagem assistant for Helldivers 2. Call stratagems quickly with voice commands, free your hands, and enhance your gaming experience!

### ✨ Key Features

- 🎤 **Real-time Speech Recognition** - Powered by Aliyun ASR, accurate and fast
- 🎯 **Smart Matching System** - Supports fuzzy matching, prefix matching, and pinyin matching
- 🔄 **Context-Aware** - Remembers recently used stratagems, intelligently switches between similar ones
- 🎨 **Modern GUI** - Clean and beautiful interface with window scaling support
- 🔊 **Audio Optimization** - Built-in noise reduction, echo cancellation, and noise gate
- 🔒 **Privacy Protection** - Encrypted configuration storage with one-click privacy clearing
- ⚡ **Lightweight & Efficient** - Low resource usage, doesn't affect game performance

### 🎬 Demo

> Say "Machine Gun" → Auto input key sequence → Call Machine Gun stratagem ✅

### 📦 Quick Start

#### Method 1: Download Executable (Recommended)

1. Go to [Releases](https://github.com/yourusername/helldivers2-voice-commander/releases)
2. Download the latest `Helldivers2-Voice-Commander-vX.X.X.zip`
3. Extract to any directory
4. Run `Helldivers2-Voice-Commander.exe`
5. Configure Aliyun credentials in "Settings" tab
6. Start using!

#### Method 2: Run from Source

```bash
# Clone repository
git clone https://github.com/yourusername/helldivers2-voice-commander.git
cd helldivers2-voice-commander

# Install dependencies
pip install -r requirements.txt

# Run program
python main_modular.py
```

### ⚙️ Configuration

#### 1. Get Aliyun Credentials

1. Login to [Aliyun Console](https://www.aliyun.com/)
2. Enable "Intelligent Speech Interaction" service
3. Create a project (Type: Real-time Speech Recognition)
4. Get credentials:
   - **APP KEY**
   - **Access Key ID**
   - **Access Key Secret**

#### 2. Configure Program

1. Open program, switch to "Settings" tab
2. Fill in Aliyun credentials
3. Click "Save Configuration"
4. Configuration will be encrypted and saved locally

### 🎮 Usage

#### Basic Usage

1. Configure stratagems (4 slots) in "Main" tab
2. Check global commands (Reinforce, Resupply, etc.)
3. Click "Start Listening"
4. Enter game, hold `Ctrl` key and speak
5. Say stratagem name (e.g., "Machine Gun", "Orbital Cannon")
6. Auto input key sequence

#### Advanced Tips

- **Fuzzy Matching**: Say "Eagle" to match "Eagle 500kg Bomb"
- **Prefix Matching**: Say "Orbital" to match "Orbital Precision Strike"
- **Smart Switching**: Repeatedly saying "Gatling" switches between "Gatling Sentry", "Orbital Gatling", "Heavy Machine Gun"
- **Context Weight**: Recently used stratagems are prioritized

### 🎯 Supported Stratagems

- ✅ All Support Weapons (Machine Gun, Heavy MG, Grenade Launcher, etc.)
- ✅ All Orbital Strikes (Orbital Cannon, Orbital Gatling, etc.)
- ✅ All Eagle Strikes (Eagle 500kg Bomb, Eagle Airstrike, etc.)
- ✅ All Defensive Buildings (Sentries, Shield Generator, etc.)
- ✅ All Backpacks and Vehicles
- ✅ Global Commands (Reinforce, Resupply, SOS, etc.)

Full list: [stratagems.json](stratagems.json)

### 🔧 System Requirements

- **OS**: Windows 10/11
- **Python**: 3.8+ (only for running from source)
- **Microphone**: Any microphone device
- **Network**: Internet connection required (Aliyun API)
- **RAM**: 2GB+ recommended

### 📝 FAQ

#### Q: Recognition not accurate?

A: 
1. Check microphone volume
2. Enable all options in "Audio Processing Settings"
3. Use in quiet environment
4. Speak clearly at moderate speed

#### Q: Keys not sent to game?

A: 
1. Ensure game window is active
2. If game runs as administrator, run this program as administrator too
3. Right-click program → Run as administrator

#### Q: How to share with friends?

A: 
1. Click "Clear Privacy Data" in "Settings" tab
2. Share the entire folder
3. Receiver needs to configure their own Aliyun credentials

### 🤝 Contributing

Issues and Pull Requests are welcome!

#### How to Contribute

1. Fork this repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file

### 🙏 Acknowledgments

- [Aliyun Intelligent Speech Service](https://www.aliyun.com/product/nls)
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/)
- [pynput](https://github.com/moses-palmer/pynput)

### 📞 Contact

- **GitHub Issues**: [Submit Issue](https://github.com/yourusername/helldivers2-voice-commander/issues)
- **Email**: your.email@example.com

### ⚠️ Disclaimer

This project is for educational purposes only. Not for commercial use. Users are responsible for any consequences.

---

<div align="center">

**Made with ❤️ for Helldivers 2 Community**

⭐ Star this repo if you find it helpful!

</div>
