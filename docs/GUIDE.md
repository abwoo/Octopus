# Octopus 操作指南 (v0.1)

欢迎使用 Octopus，这是一个由 AI 驱动的 Windows 自动化执行引擎。

## 1. 核心架构

Octopus 采用 **一键驱动，全端同步** 的逻辑。无论您是在 PowerShell 使用 `.\agent.ps1`，还是在 Web Dashboard 点击按钮，执行路径完全一致。

- **逻辑链条**：Dashboard -> FastAPI -> **CLI (Subprocess)** -> Core Agent -> Hardware/System
- **透明度**：Web 端的日志区域会实时显示正在执行的原始 Python 终端命令。

## 2. LLM 平台配置

点击 Dashboard 右上角的齿轮图标 **(⚙️)** 进行配置：

| 平台类型 | 配置说明 | 适用场景 |
| :--- | :--- | :--- |
| **Google Gemini** | 输入 API Key | 性能强劲，长上下文支持 |
| **OpenAI Cloud** | 输入 sk-xxx | 行业标准方案 |
| **Local LLM** | 开启 Ollama/LM Studio 并填写 Base URL | 隐私保护，无网络环境 |
| **Custom** | 填写兼容 OpenAI 协议的自定义端点 | 中转、私有化部署 |

## 3. 常用指令与动作

您可以通过底部输入框下达自然语言指令：

- **鼠标操作**：`mouse.move(x, y)`, `mouse.click()`
- **文件管理**：`file.write(path, content)`, `file.read(path)`
- **系统工具**：`system.screen_size()`, `system.info()`
- **组合指令示例**：“帮我在桌面创建一个名为 'MyBot' 的文件夹，并在里面写一个 hello.txt”

## 4. 安全机制

- **紧急停机**：按下全局快捷键 **Ctrl + Alt + Q** 立即停止所有 Agent 活动。
- **沙盒运行**：所有文件操作默认限制在项目根目录下的 `workspace/` 文件夹内。

## 5. 维护与更新

项目具备自动同步功能，运行 `.\sync.ps1` 可将您的本地修改推送至云端。
