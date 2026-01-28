# Octopus 终极操作手册 (v0.5)

欢迎使用 Octopus。本手册详细记录了目前版本的所有核心能力、参数定义以及进阶用法。

---

## 1. 核心交互模式

- **AI 智能模式**: 在输入框中输入自然语言。AI 会根据下方的 **技能库** 自动编排 Action 序列。
- **PowerShell 透传 (!)**: 以 `!` 开头的指令（如 `!ls`）将绕过 AI，直接在 Windows 終端执行并返回原始内容。
- **多语言切换**: 点击顶部 `Languages` 按钮切换中英文界面。

---

## 2. 技能库全量参考 (Skills API)

### 🖱️ 鼠标 (mouse)

- `mouse.move(x, y)`: 移动到坐标 (x, y)。
- `mouse.click(button='left')`: 点击鼠标。
- `mouse.scroll(amount)`: 滚动，正数为向上。

### ⌨️ 键盘 (keyboard)

- `keyboard.type(text)`: 输入文字串。
- `keyboard.hotkey(*keys)`: 组合键（如 `['ctrl', 'c']`）。
- `keyboard.press(key)`: 模拟单键按下。

### 📂 文件 (file)

- `file.write(path, content)`: 写入文件。
- `file.read(path)`: 读取并返回文件内容。
- `file.delete(path)`: 删除指定文件。

### 🌐 网络 (network)

- `network.request(method, url, data=None)`: 执行 HTTP 请求。

### 📋 剪贴板 (clipboard) [NEW]

- `action='write'`, `text='...'`: 写入剪贴板。
- `action='read'`: 读取剪贴板内容。

### 🖥️ 系统 (system / hardware)

- `system.screen_size()`: 获取屏幕分辨率。
- `hardware.usage()`: [NEW] 实时查看 CPU、内存、磁盘占用率。
- `process.list()`: 列出当前窗口/进程。
- `process.kill(name)`: 终止指定进程。

---

## 3. 进阶技巧

1. **急停开关**: 运行过程中如需强行中止，可直接按下快捷键 **Ctrl+Alt+Q**。
2. **工作空间**: 所有的文件读写操作默认在项目根目录下的 `workspace/` 文件夹中进行，确保系统安全。
3. **自定义技能**: 您可以在 `skills/` 目录下添加自己的 Python 脚本，Octopus 会自动识别并加载它们。

---

## 4. 常见问题

- **文档不显显示?**: v0.5 版本已实现“双轨机制”，内置硬核缓存，100% 确保文档可见。
- **DeepSeek 连接失败?**: 请检查配置页面中的 API Key 和选项是否匹配。
