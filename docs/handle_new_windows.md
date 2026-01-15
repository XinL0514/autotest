# Playwright 新窗口/新标签页处理指南

## 核心概念

### ❌ Selenium 的方式（需要切换）
```python
# Selenium 需要手动切换窗口句柄
driver.switch_to.window(driver.window_handles[1])
```

### ✅ Playwright 的方式（获取 Page 对象）
```python
# Playwright 不需要"切换"，每个页面是独立的 Page 对象
with page.context.expect_page() as new_page_info:
    page.click("#open-new-window")
new_page = new_page_info.value  # 获取新 Page 对象
```

**关键区别**：
- Selenium：一个 driver 对象，需要切换到不同窗口
- Playwright：多个 Page 对象，直接操作对应的对象

---

## 使用 BasePage 封装的方法

BasePage 提供了 4 个新窗口处理方法：

### 1. click_and_handle_new_page() - 点击并获取新页面

**最常用的方法**，一行代码搞定点击 + 获取新页面。

```python
def test_open_new_tab(self, authenticated_page: Page):
    mar_page = MarPage(authenticated_page)

    # 点击会打开新标签页的按钮，自动获取新页面对象
    new_page = mar_page.click_and_handle_new_page(
        Element("role", ("button", "在新标签页打开"), desc="打开按钮")
    )

    # 在新页面操作
    new_page.click("#download-btn")
    new_page.fill("#comment", "测试评论")

    # 在原页面操作（不需要切换）
    mar_page.click(("button", "刷新"))

    # 关闭新页面
    new_page.close()
```

---

### 2. get_all_pages() - 获取所有页面

查看当前打开了多少个页面。

```python
def test_check_pages(self, authenticated_page: Page):
    page = BasePage(authenticated_page)

    # 获取所有页面
    all_pages = page.get_all_pages()
    print(f"当前打开了 {len(all_pages)} 个页面")

    # 遍历所有页面
    for i, p in enumerate(all_pages):
        print(f"页面 {i}: {p.url}")
```

---

### 3. close_all_new_windows() - 关闭所有新窗口

批量关闭除当前页面外的所有窗口。

```python
def test_close_all_windows(self, authenticated_page: Page):
    page = BasePage(authenticated_page)

    # 打开多个新窗口
    new_page1 = page.click_and_handle_new_page(("button", "打开窗口1"))
    new_page2 = page.click_and_handle_new_page(("button", "打开窗口2"))
    new_page3 = page.click_and_handle_new_page(("button", "打开窗口3"))

    # 一键关闭所有新窗口
    page.close_all_new_windows()

    # 现在只剩原窗口
    all_pages = page.get_all_pages()
    assert len(all_pages) == 1
```

---

### 4. switch_to_latest_page() - 切换到最新页面

更新当前 Page 对象为最新打开的页面。

```python
def test_switch_to_latest(self, authenticated_page: Page):
    mar_page = MarPage(authenticated_page)

    # 点击按钮（会打开新页面）
    mar_page.click(("button", "查看详情"))

    # 切换到新页面（更新 mar_page.page）
    mar_page.switch_to_latest_page()

    # 现在所有操作都在新页面上
    mar_page.click("#download")  # 在新页面点击
    mar_page.fill("#comment", "测试")  # 在新页面填写
```

⚠️ **注意**：这个方法会改变 `self.page`，慎用！推荐使用方法1。

---

## 实际场景示例

### 场景1: 点击"在新标签页打开"链接

```python
class DetailPage(BasePage):
    """详情页"""

    OPEN_IN_NEW_TAB = Element(
        "role", ("link", "在新标签页打开"),
        desc="在新标签页打开链接"
    )

    def open_detail_in_new_tab(self):
        """打开详情页到新标签页"""
        # 点击并获取新页面
        new_page = self.click_and_handle_new_page(self.OPEN_IN_NEW_TAB)

        # 返回新页面对象，供测试用例使用
        return new_page


# 测试用例
def test_view_detail_in_new_tab(self, authenticated_page: Page):
    detail_page = DetailPage(authenticated_page)

    # 打开新标签页
    new_tab = detail_page.open_detail_in_new_tab()

    # 在新标签页操作
    assert "详情" in new_tab.title()
    new_tab.click("#download-pdf")

    # 在原页面操作
    detail_page.click(("button", "返回列表"))

    # 关闭新标签页
    new_tab.close()
```

---

### 场景2: 点击按钮触发弹窗（window.open）

```python
class UserManagePage(BasePage):
    """用户管理页面"""

    EXPORT_BUTTON = Element(
        "role", ("button", "导出数据"),
        desc="导出数据按钮"
    )

    def export_data(self):
        """导出数据（会打开新窗口显示下载链接）"""
        # 点击导出按钮，会弹出新窗口
        export_window = self.click_and_handle_new_page(self.EXPORT_BUTTON)

        # 在导出窗口操作
        download_link = export_window.get_by_role("link", name="下载文件")
        download_url = download_link.get_attribute("href")

        # 关闭导出窗口
        export_window.close()

        return download_url


# 测试用例
def test_export_data(self, authenticated_page: Page):
    user_page = UserManagePage(authenticated_page)

    # 导出数据
    download_url = user_page.export_data()

    # 验证下载链接
    assert download_url.endswith(".xlsx")
```

---

### 场景3: 处理多个新窗口

```python
def test_multiple_windows(self, authenticated_page: Page):
    page = BasePage(authenticated_page)

    # 打开3个新窗口
    window1 = page.click_and_handle_new_page(("button", "打开窗口1"))
    window2 = page.click_and_handle_new_page(("button", "打开窗口2"))
    window3 = page.click_and_handle_new_page(("button", "打开窗口3"))

    # 在不同窗口操作（不需要切换）
    window1.fill("#input1", "窗口1的数据")
    window2.fill("#input2", "窗口2的数据")
    window3.fill("#input3", "窗口3的数据")

    # 在原窗口操作
    page.click(("button", "原窗口按钮"))

    # 关闭所有新窗口
    window1.close()
    window2.close()
    window3.close()

    # 或者一键关闭
    # page.close_all_new_windows()
```

---

### 场景4: target="_blank" 的链接

```python
def test_open_blank_link(self, authenticated_page: Page):
    page = BasePage(authenticated_page)

    # HTML: <a href="/help" target="_blank">帮助文档</a>

    # 点击 target="_blank" 的链接
    help_page = page.click_and_handle_new_page(
        Element("role", ("link", "帮助文档"), desc="帮助链接")
    )

    # 在帮助页面操作
    assert "帮助" in help_page.title()
    help_page.click("#search-help")

    # 关闭帮助页面
    help_page.close()
```

---

### 场景5: 验证新窗口内容后关闭

```python
def test_verify_popup_content(self, authenticated_page: Page):
    page = BasePage(authenticated_page)

    # 点击"查看协议"按钮（会打开新窗口）
    popup = page.click_and_handle_new_page(
        Element("role", ("button", "查看用户协议"), desc="用户协议按钮")
    )

    # 在弹窗中验证内容
    assertion = Assertion()
    title = popup.title()
    assertion.assert_contains(title, "用户协议", "验证弹窗标题")

    content = popup.get_by_role("article").text_content()
    assertion.assert_contains(content, "隐私条款", "验证协议内容")

    # 关闭弹窗
    popup.close()
```

---

## 直接使用 Playwright API

如果不想用 BasePage 的封装方法，也可以直接使用 Playwright API：

### 方式1: context.expect_page()（推荐）

```python
def test_new_page_direct(self, authenticated_page: Page):
    page = authenticated_page

    # 监听新页面事件
    with page.context.expect_page() as new_page_info:
        page.click("button:has-text('打开新页面')")

    new_page = new_page_info.value

    # 操作新页面
    new_page.click("#some-button")

    # 关闭新页面
    new_page.close()
```

---

### 方式2: page.wait_for_event('popup')

```python
def test_popup_event(self, authenticated_page: Page):
    page = authenticated_page

    # 方式2：使用 wait_for_event
    with page.expect_popup() as popup_info:
        page.click("a[target='_blank']")

    popup = popup_info.value
    popup.wait_for_load_state()

    # 操作弹窗
    print(popup.url)

    # 关闭弹窗
    popup.close()
```

---

### 方式3: context.pages 获取所有页面

```python
def test_get_all_pages(self, authenticated_page: Page):
    page = authenticated_page

    # 点击前只有1个页面
    print(f"当前页面数: {len(page.context.pages)}")  # 1

    # 点击打开新页面
    page.click("button:has-text('打开新页面')")
    page.wait_for_timeout(1000)  # 等待新页面打开

    # 获取所有页面
    all_pages = page.context.pages
    print(f"现在页面数: {len(all_pages)}")  # 2

    # 获取新页面（最后一个）
    new_page = all_pages[-1]

    # 操作新页面
    new_page.click("#button")

    # 关闭新页面
    new_page.close()
```

---

## 常见问题

### Q1: 什么时候需要处理新窗口？

当你遇到以下情况时：
- 点击按钮/链接打开了新标签页
- HTML 中有 `target="_blank"`
- JavaScript 使用 `window.open()`
- 弹出窗口、对话框（不是 alert/confirm）

### Q2: Playwright 需要切换窗口吗？

**不需要！** Playwright 不需要像 Selenium 那样"切换"窗口。

- Selenium：`driver.switch_to.window(handle)`
- Playwright：获取新的 `Page` 对象，直接操作

### Q3: 如何判断点击会打开新窗口？

检查 HTML：
```html
<!-- 会打开新窗口 -->
<a href="/detail" target="_blank">查看详情</a>
<button onclick="window.open('/help')">帮助</button>

<!-- 不会打开新窗口 -->
<a href="/detail">查看详情</a>
<button onclick="location.href='/help'">帮助</button>
```

### Q4: 新窗口打开失败怎么办？

检查是否浏览器阻止了弹窗：
```python
# 创建上下文时允许弹窗
context = browser.new_context(
    # ... 其他配置
    # 默认已允许弹窗，通常不需要额外配置
)
```

### Q5: 可以同时操作多个窗口吗？

**可以！** 每个 Page 对象是独立的：

```python
# 同时在3个窗口操作
window1.fill("#input1", "数据1")
window2.fill("#input2", "数据2")
window3.fill("#input3", "数据3")
```

### Q6: 关闭新窗口后，原窗口还能用吗？

**能！** 每个 Page 对象是独立的：

```python
new_page = page.click_and_handle_new_page(...)
new_page.click("#button")
new_page.close()  # 关闭新窗口

# 原窗口仍然可用
page.click("#original-button")  # ✅ 正常工作
```

---

## 最佳实践

### 1. 推荐使用 click_and_handle_new_page()

```python
# ✅ 推荐：使用封装方法
new_page = self.click_and_handle_new_page(locator)

# ❌ 不推荐：手动处理（除非有特殊需求）
with self.page.context.expect_page() as info:
    self.click(locator)
new_page = info.value
```

### 2. 使用完毕后关闭新窗口

```python
# ✅ 推荐：及时关闭
new_page = self.click_and_handle_new_page(locator)
new_page.click("#button")
new_page.close()  # 关闭窗口

# ❌ 不推荐：不关闭（可能导致资源浪费）
new_page = self.click_and_handle_new_page(locator)
new_page.click("#button")
# 忘记关闭
```

### 3. 使用 with 语句自动关闭

```python
# ✅ 更好：使用 context manager
new_page = self.click_and_handle_new_page(locator)
try:
    new_page.click("#button")
    new_page.fill("#input", "test")
finally:
    new_page.close()
```

### 4. 添加清晰的注释

```python
# ✅ 推荐：注释说明这是新窗口操作
# 在新窗口中下载文件
download_page = self.click_and_handle_new_page(self.DOWNLOAD_BUTTON)
download_page.click("#confirm-download")
download_page.close()

# 回到原窗口继续操作
self.click(self.REFRESH_BUTTON)
```

---

## 总结

| 特性 | Selenium | Playwright |
|------|----------|------------|
| 窗口模型 | 单个 driver，多个 handle | 多个独立 Page 对象 |
| 切换窗口 | `driver.switch_to.window(handle)` | 不需要切换，直接操作对应 Page |
| 获取新窗口 | `driver.window_handles[-1]` | `context.expect_page()` |
| 同时操作多窗口 | 需要频繁切换 | 直接操作不同 Page 对象 |
| 复杂度 | 较复杂 | 更简单直观 |

**Playwright 的优势**：
- ✅ 不需要切换窗口
- ✅ 每个页面是独立对象，操作更清晰
- ✅ 可以同时操作多个窗口
- ✅ 代码更简洁易读
