# VSCode Debug 调试指南

本文档说明如何在 VSCode 中调试 Playwright 自动化测试。

## 问题解决

### ❌ 之前的问题
```
ModuleNotFoundError: No module named 'pages'
```

### ✅ 已修复
已在以下文件中配置 Python 路径：
1. `conftest.py` - 添加项目根目录到 `sys.path`
2. `.vscode/launch.json` - 配置 debug 环境变量
3. `.vscode/settings.json` - 配置终端环境变量

---

## 调试方法（3 种）

### 方法1：使用 VSCode Debug（推荐）

#### 步骤：
1. 在测试代码中打断点（点击行号左侧）
2. 打开要调试的测试文件（如 `tests/mar/test_mar.py`）
3. 按 `F5` 或点击左侧"运行和调试"图标
4. 选择调试配置：
   - `Pytest: Debug Current File` - 调试当前文件所有测试
   - `Pytest: Debug All Tests` - 调试所有测试
   - `Pytest: Debug MAR Tests` - 调试用药记录模块

#### 可用的 Debug 配置：

| 配置名称 | 用途 | 使用场景 |
|---------|------|---------|
| `Pytest: Debug Current File` | 调试当前文件 | 调试单个测试文件 |
| `Pytest: Debug Current Test` | 调试选中的测试 | 调试单个测试方法 |
| `Pytest: Debug All Tests` | 调试所有测试 | 全量调试 |
| `Pytest: Debug MAR Tests` | 调试用药记录模块 | 调试特定模块 |
| `Python: Current File` | 运行 Python 文件 | 运行普通 Python 脚本 |

---

### 方法2：使用 VSCode Testing 面板

#### 步骤：
1. 点击左侧"测试"图标（烧杯图标）
2. VSCode 会自动发现所有测试用例
3. 右键点击测试用例 → "调试测试"
4. 代码会在断点处暂停

#### 优点：
- 可视化测试树结构
- 快速运行/调试单个测试
- 显示测试结果

---

### 方法3：命令行调试（高级）

```bash
# 在终端中运行（已自动配置 PYTHONPATH）
pytest tests/mar/test_mar.py -v -s

# 调试特定测试
pytest tests/mar/test_mar.py::TestMar::test_click_mar_tab -v -s

# 使用 pdb 调试器
pytest tests/mar/test_mar.py --pdb
```

---

## Debug 配置详解

### 1. conftest.py 配置

```python
import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
```

**作用**：确保在任何位置运行测试都能正确导入模块。

---

### 2. launch.json 配置

关键配置项：
```json
{
    "cwd": "${workspaceFolder}",        // 工作目录为项目根目录
    "env": {
        "PYTHONPATH": "${workspaceFolder}"  // 环境变量
    },
    "console": "integratedTerminal",    // 使用集成终端
    "justMyCode": false                 // 可以调试第三方库代码
}
```

---

### 3. settings.json 配置

```json
{
    "python.testing.pytestEnabled": true,  // 启用 pytest
    "terminal.integrated.env.osx": {
        "PYTHONPATH": "${workspaceFolder}"  // macOS 终端环境变量
    }
}
```

---

## 调试技巧

### 1. 设置断点

```python
def test_click_mar_tab(self, authenticated_page: Page):
    mar_page = MarPage(authenticated_page)
    mar_page.open()
    mar_page.click_mar_tab()  # ← 点击这一行左侧设置断点
```

### 2. 条件断点

右键断点 → "编辑断点" → 添加条件：
```python
mar_tab_text == "用药记录"
```

### 3. 日志断点

右键断点 → "编辑断点" → 勾选"日志消息"：
```python
mar_tab_text: {mar_tab_text}
```

### 4. 查看变量

调试时：
- 鼠标悬停在变量上查看值
- 左侧"变量"面板查看所有局部变量
- "监视"面板添加表达式

### 5. 调试控制台

在调试控制台中执行 Python 代码：
```python
# 查看页面 URL
>>> page.url

# 获取元素文本
>>> page.locator("button").text_content()

# 执行 Playwright 方法
>>> page.screenshot(path="debug.png")
```

---

## 常见问题

### Q1: 断点不生效？

**解决方案**：
1. 确保选择了正确的 debug 配置（`Pytest: Debug Current File`）
2. 确保断点设置在可执行代码行（不是注释或空行）
3. 重启 VSCode

### Q2: 仍然报 `ModuleNotFoundError`？

**解决方案**：
```bash
# 1. 重启 VSCode
# 2. 检查 Python 解释器是否正确
Cmd + Shift + P → "Python: Select Interpreter"

# 3. 在终端中验证 PYTHONPATH
echo $PYTHONPATH

# 4. 手动设置 PYTHONPATH（临时）
export PYTHONPATH=/Users/hantongxue/Desktop/work/autotest:$PYTHONPATH
```

### Q3: Debug 太慢？

**优化方案**：
```json
// launch.json
{
    "justMyCode": true,  // 只调试自己的代码，不进入第三方库
    "args": [
        "${file}",
        "-v",
        "--tb=short"  // 简化错误回溯
    ]
}
```

### Q4: 如何调试单个测试方法？

**方法1**：使用 Testing 面板（推荐）
- 在测试面板中找到测试方法
- 右键 → "调试测试"

**方法2**：使用命令行
```bash
pytest tests/mar/test_mar.py::TestMar::test_click_mar_tab -v -s
```

**方法3**：使用 `Pytest: Debug Current Test` 配置
1. 选中测试方法名 `test_click_mar_tab`
2. 按 F5
3. 选择 `Pytest: Debug Current Test`

---

## 调试 Playwright 特殊技巧

### 1. 使用 page.pause() 暂停

```python
def test_click_mar_tab(self, authenticated_page: Page):
    mar_page = MarPage(authenticated_page)
    mar_page.open()

    # 暂停执行，打开 Playwright Inspector
    authenticated_page.pause()

    mar_page.click_mar_tab()
```

### 2. 慢速执行

```python
# conftest.py
@pytest.fixture(scope="session")
def browser_type_launch_args():
    return {
        "headless": False,
        "slow_mo": 1000  # 每个操作延迟 1 秒
    }
```

### 3. 录制 Trace

```bash
# 运行时保留失败测试的 trace
pytest tests/mar/ --trace-mode=retain-on-failure

# 查看 trace（在浏览器中打开）
playwright show-trace test-results/test_click_mar_tab_20251231_160000.zip
```

### 4. 截图调试

```python
def test_click_mar_tab(self, authenticated_page: Page):
    mar_page = MarPage(authenticated_page)
    mar_page.open()

    # 调试截图
    authenticated_page.screenshot(path="debug_before_click.png")
    mar_page.click_mar_tab()
    authenticated_page.screenshot(path="debug_after_click.png")
```

---

## 快捷键

| 操作 | macOS | Windows/Linux |
|------|-------|---------------|
| 开始调试 | `F5` | `F5` |
| 继续执行 | `F5` | `F5` |
| 单步跳过 | `F10` | `F10` |
| 单步进入 | `F11` | `F11` |
| 单步跳出 | `Shift+F11` | `Shift+F11` |
| 停止调试 | `Shift+F5` | `Shift+F5` |
| 重启调试 | `Cmd+Shift+F5` | `Ctrl+Shift+F5` |

---

## 总结

现在你可以：

✅ 在 VSCode 中直接 Debug 测试文件
✅ 不会再遇到 `ModuleNotFoundError`
✅ 使用断点、变量监视等调试功能
✅ 使用 Playwright Inspector 进行可视化调试

**推荐工作流**：
1. 使用 VSCode Testing 面板查看所有测试
2. 右键单个测试 → "调试测试"
3. 在关键位置设置断点
4. 使用调试控制台执行 Playwright 命令
5. 失败时查看 Allure 报告 + Trace 文件

Happy Debugging! 🐛🔍
