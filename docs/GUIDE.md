# Octopus 操作指南 (v0.2 - 全能版)

欢迎使用 Octopus。v0.2 版本引入了 **PowerShell 透传** 和 **协议多元化** 支持。

## 1. 核心交互方式

Octopus 现支持两种主要的交互模式：

- **AI 代理模式**：在前端输入框直接输入自然语言（如“帮我写一个 python 脚本”），后台 LLM 将其解析为 Action 序列。
- **PowerShell 透传模式**：在输入框开头使用 `!` 符号（如 `!ls`, `!dir`, `!Get-Service`），命令将直接在后台 PowerShell 终端执行，结果实时返回日志区。

## 2. API 与协议配置 (多元化)

点击右上角齿轮 **(⚙️)**，您可以配置以下协议：

| 协议 / 平台 | 说明 |
| :--- | :--- |
| **OpenAI** | 兼容所有标准 OpenAI 接口。 |
| **Google Gemini** | 深度集成 Gemini Pro/Flash 模型。 |
| **Anthropic** | 原生支持 Claude 3/3.5 模型系列。 |
| **Local** | 适配 Ollama, LM Studio 等本地运行的大模型。 |
| **Universal HTTP** | **万能模式**。您可以填入任何 API 地址，手动适配非标接口。 |

## 3. 增强技能库 (Skills)

本版本新增了以下核心技能：

- **Network (网络)**: 执行 HTTP GET/POST 请求，获取互联网数据。
- **Process (进程)**: 查看 (`list`) 或终止 (`kill`) 系统的运行进程。
- **File (文件)**: 原子化的读写操作，限制在 `workspace` 安全目录内。

## 4. 命令行交互 (CLI)

如果您更喜欢在终端工作，可以使用 `agent.ps1`：

- `.\agent.ps1 shell`: 进入交互式对话模式。
- `.\agent.ps1 skill create <name>`: 快速创建新的技能开发模板。
- `.\agent.ps1 config edit`: 在默认编辑器中直接调整全局配置。

## 5. 安全与停机

- 全局急停：**Ctrl + Alt + Q**。
- 日志透明：Web 端日志详尽记录了每一条由 AI 生成或手动输入的终端指令。
