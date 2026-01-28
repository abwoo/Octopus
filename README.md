# 🐙 Octopus: Hybrid Action Execution Engine

**AI-Native Windows 自动化执行引擎 | PowerShell 透传 | 多协议兼容 (DeepSeek/GPT/Claude)**

[![Version](https://img.shields.io/badge/version-v0.5-blue.svg)](https://github.com/abwoo/Octopus)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

---

## 🚀 欢迎使用 Octopus

Octopus 是一个专为 Windows 系统设计的**模型无关 (Model-Agnostic)** 执行层。它为 AI 大模型提供了一个安全、结构化的硬件操作接口，支持鼠标、键盘、文件系统、网络以及系统进程的深度控制。

### ✨ 核心特性

- **Aurora UI (极光视觉)**: 极简主义玻璃拟态设计，流光背景，顶级交互体验。
- **PowerShell 透传 (!)**: 无需复杂配置，直接在控制台以 `!` 前缀运行原生 PowerShell 指令。
- **协议多元化**: 原生支持 **DeepSeek**、OpenAI、Gemini、Anthropic 以及任何通用 HTTP 代理。
- **多语言系统 (i18n)**: 界面与文档支持中英双语一键切换。
- **全能技能库**: 剪贴板控制、硬件监控、文件沙箱、进程管理、网络请求。

---

## 🛠️ 从零开始：安装与启动

### 1. 环境准备

确保您的 Windows 系统已安装以下环境：

- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js (LTS)](https://nodejs.org/en) (用于 Dashboard 界面)
- [Git](https://git-scm.com/downloads)

### 2. 一键快速部署

打开 PowerShell (管理员模式)，直接运行：

```powershell
# 克隆仓库并安装所有依赖
git clone https://github.com/abwoo/Octopus.git
cd Octopus
.\install.ps1
```

### 3. 启动 Dashboard

运行以下命令，系统会自动启动后端 API 和前端界面，并在浏览器中打开：

```powershell
.\start_dashboard.ps1
```

---

## 📖 使用指南

### 仪表盘交互 (Dashboard)

1. **Languages**: 点击右上角切换至“中文”界面。
2. **API Configuration**: 进入侧边栏，选择您的模型供应商（如 DeepSeek），填入 API Key。
3. **Instruction Guide**: 查看内置的**全量操作手册**，详细了解所有 Skill 的参数定义。

### 命令行工具 (CLI)

Octopus 提供了强大的 CLI 工具 `agent.ps1`：

```powershell
.\agent.ps1 shell         # 进入交互式 Shell 模式
.\agent.ps1 status        # 检查内核与环境状态
.\agent.ps1 skill create  # 快速生成新技能模板
```

---

## 🏗️ 项目架构

```text
Octopus/
├── api/                  # FastAPI 后端实现
├── cli/                  # 命令行交互逻辑
├── core/                 # 代理核心与硬件执行原始层
├── skills/               # 技能扩展插件库 (Clipboard, Hardware, etc.)
├── web/                  # React + Vite 前端 (Aurora UI)
├── docs/                 # 项目文档 (GUIDE.md)
└── workspace/            # 安全沙箱操作目录
```

---

## 🛡️ 安全机制

1. **急停开关**: 运行中按下 **Ctrl+Alt+Q** 立即中断所有 AI 动作。
2. **操作间隔**: 强制执行硬件操作间的 300ms 冷却时间，防止系统过载。
3. **文件沙箱**: 所有读写操作被限制在 `workspace/` 目录下，保护系统核心文件。

---

## 🤝 贡献与感谢

本项目的架构参考了 **moltbot** 与 **agno** 的优秀模式。
欢迎提交 Issue 或 Pull Request 来增加更多有趣的 Skills！

## 📄 开源协议

本项目基于 [MIT](LICENSE) 协议开源。
