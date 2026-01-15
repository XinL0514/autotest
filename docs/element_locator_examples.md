# Element 元素定位器配置类 - 完整使用手册

本文档提供 Element 配置类的完整使用示例，涵盖所有定位方式和实际场景。

## 目录
- [快速开始](#快速开始)
- [1. 基础定位方式（8种）](#1-基础定位方式8种)
  - [1.1 Role 定位器（最推荐）](#11-role-定位器最推荐)
  - [1.2 Text 文本定位器](#12-text-文本定位器)
  - [1.3 Placeholder 占位符定位器](#13-placeholder-占位符定位器)
  - [1.4 Label 标签定位器](#14-label-标签定位器)
  - [1.5 Test ID 定位器（最稳定）](#15-test-id-定位器最稳定)
  - [1.6 Title 标题属性定位器](#16-title-标题属性定位器)
  - [1.7 Alt Text 图片替代文本定位器](#17-alt-text-图片替代文本定位器)
  - [1.8 CSS 选择器](#18-css-选择器)
  - [1.9 XPath 选择器](#19-xpath-选择器)
- [2. 链式操作](#2-链式操作)
  - [2.1 filter() 筛选](#21-filter-筛选)
  - [2.2 first() 第一个](#22-first-第一个)
  - [2.3 last() 最后一个](#23-last-最后一个)
  - [2.4 nth(n) 第 n 个](#24-nthn-第-n-个)
- [3. 组合使用（复杂场景）](#3-组合使用复杂场景)
- [4. 实际业务场景示例](#4-实际业务场景示例)
- [定位器选择建议](#定位器选择建议)

---

## 快速开始

### 导入 Element 类

```python
from utils.element import Element
from pages.base_page import BasePage
```

### 基础示例

```python
# 定义元素
LOGIN_BUTTON = Element(
    "role", ("button", "登录"),
    desc="登录按钮"
)

# 使用元素
class LoginPage(BasePage):
    def login(self):
        self.click(LOGIN_BUTTON)
```

### Element 参数说明

```python
Element(
    by="role",                          # 定位方式（必填）
    value=("button", "登录"),            # 定位值（必填）
    desc="登录按钮",                     # 元素描述（强烈推荐）
    exact=False,                        # 是否精确匹配
    filter_params={"has_text": "复制"}, # filter 筛选参数
    nth=1,                              # 获取第 n 个（索引从0开始）
    first=False,                        # 获取第一个
    last=False,                         # 获取最后一个
    timeout=5000                        # 自定义超时时间（毫秒）
)
```

---

## 1. 基础定位方式（8种）

### 1.1 Role 定位器（最推荐）

基于 ARIA role 属性，最符合可访问性标准，推荐优先使用。

```python
# ========== 按钮 ==========
LOGIN_BUTTON = Element(
    "role", ("button", "登录"),
    desc="登录按钮"
)

SUBMIT_BUTTON = Element(
    "role", ("button", "提交"),
    desc="提交按钮",
    exact=True  # 精确匹配，避免匹配到 "提交订单"
)

# 只指定 role，不指定 name
ANY_BUTTON = Element(
    "role", ("button",),
    desc="任意按钮"
)

# ========== 输入框 ==========
USERNAME_INPUT = Element(
    "role", ("textbox", "用户名"),
    desc="用户名输入框"
)

PASSWORD_INPUT = Element(
    "role", ("textbox", "密码"),
    desc="密码输入框"
)

SEARCH_INPUT = Element(
    "role", ("searchbox", "搜索"),
    desc="搜索框"
)

# ========== 复选框/单选框 ==========
AGREE_CHECKBOX = Element(
    "role", ("checkbox", "我已阅读并同意"),
    desc="同意协议复选框"
)

MALE_RADIO = Element(
    "role", ("radio", "男"),
    desc="性别单选框-男"
)

# ========== 链接 ==========
REGISTER_LINK = Element(
    "role", ("link", "立即注册"),
    desc="注册链接"
)

# ========== 标题 ==========
PAGE_HEADING = Element(
    "role", ("heading", "用户管理"),
    desc="页面标题"
)

# ========== 表格 ==========
USER_TABLE = Element(
    "role", ("table",),
    desc="用户列表表格"
)

TABLE_ROW = Element(
    "role", ("row", "张三"),
    desc="张三的数据行"
)

TABLE_CELL = Element(
    "role", ("cell", "admin@example.com"),
    desc="邮箱单元格"
)

# ========== 下拉列表 ==========
CITY_SELECT = Element(
    "role", ("combobox", "选择城市"),
    desc="城市下拉框"
)

# ========== 对话框 ==========
CONFIRM_DIALOG = Element(
    "role", ("dialog", "确认删除"),
    desc="确认删除弹窗"
)

# ========== 标签页 ==========
SETTINGS_TAB = Element(
    "role", ("tab", "设置"),
    desc="设置标签页"
)
```

---

### 1.2 Text 文本定位器

通过元素的文本内容定位。

```python
# ========== 精确匹配 ==========
WELCOME_TEXT = Element(
    "text", "欢迎回来",
    desc="欢迎语",
    exact=True  # 只匹配 "欢迎回来"，不匹配 "欢迎回来，张三"
)

# ========== 模糊匹配 ==========
ERROR_MESSAGE = Element(
    "text", "错误",
    desc="错误提示信息",
    exact=False  # 匹配包含"错误"的所有文本
)

# ========== 匹配部分文本 ==========
SUCCESS_HINT = Element(
    "text", "操作成功",
    desc="成功提示"
)

# ========== 匹配特殊字符 ==========
PRICE_LABEL = Element(
    "text", "¥99.00",
    desc="价格标签"
)
```

---

### 1.3 Placeholder 占位符定位器

通过输入框的 placeholder 属性定位，适用于输入框。

```python
# ========== 输入框占位符 ==========
USERNAME_FIELD = Element(
    "placeholder", "请输入用户名",
    desc="用户名输入框"
)

EMAIL_FIELD = Element(
    "placeholder", "example@email.com",
    desc="邮箱输入框",
    exact=True
)

SEARCH_BOX = Element(
    "placeholder", "搜索商品、店铺",
    desc="搜索框"
)

PHONE_FIELD = Element(
    "placeholder", "手机号",
    desc="手机号输入框"
)
```

---

### 1.4 Label 标签定位器

通过 `<label>` 标签的文本定位关联的表单元素。

```python
# ========== 表单标签 ==========
USERNAME_BY_LABEL = Element(
    "label", "用户名：",
    desc="通过标签定位用户名输入框"
)

BIRTHDAY_PICKER = Element(
    "label", "出生日期",
    desc="生日选择器",
    exact=True
)

# ========== 复选框标签 ==========
REMEMBER_ME = Element(
    "label", "记住我",
    desc="记住密码选项"
)

# ========== 单选框标签 ==========
GENDER_MALE = Element(
    "label", "男",
    desc="性别-男"
)
```

---

### 1.5 Test ID 定位器（最稳定）

通过 `data-testid` 属性定位，最稳定，推荐用于关键元素。

```python
# HTML 示例: <button data-testid="submit-btn">提交</button>

SUBMIT_BTN = Element(
    "testid", "submit-btn",
    desc="提交按钮"
)

DELETE_BTN = Element(
    "testid", "delete-user-123",
    desc="删除用户按钮"
)

USER_AVATAR = Element(
    "testid", "user-avatar",
    desc="用户头像"
)

LOGIN_FORM = Element(
    "testid", "login-form",
    desc="登录表单"
)
```

---

### 1.6 Title 标题属性定位器

通过元素的 `title` 属性定位（鼠标悬停提示）。

```python
# HTML 示例: <button title="点击保存">💾</button>

SAVE_ICON = Element(
    "title", "点击保存",
    desc="保存图标按钮"
)

HELP_ICON = Element(
    "title", "帮助",
    desc="帮助图标",
    exact=True
)

CLOSE_BUTTON = Element(
    "title", "关闭",
    desc="关闭按钮"
)
```

---

### 1.7 Alt Text 图片替代文本定位器

通过 `<img>` 标签的 `alt` 属性定位。

```python
# HTML 示例: <img src="logo.png" alt="公司Logo">

COMPANY_LOGO = Element(
    "alt_text", "公司Logo",
    desc="公司标志图片"
)

PRODUCT_IMAGE = Element(
    "alt_text", "iPhone 15 Pro",
    desc="商品主图"
)

USER_PHOTO = Element(
    "alt_text", "用户头像",
    desc="个人照片"
)
```

---

### 1.8 CSS 选择器

使用 CSS 选择器语法定位元素。

```python
# ========== ID 选择器 ==========
LOGIN_FORM_CSS = Element(
    "css", "#login-form",
    desc="登录表单"
)

# ========== Class 选择器 ==========
ERROR_MESSAGE_CSS = Element(
    "css", ".error-message",
    desc="错误提示信息"
)

# ========== 属性选择器 ==========
DISABLED_INPUT = Element(
    "css", "input[disabled]",
    desc="禁用的输入框"
)

REQUIRED_FIELD = Element(
    "css", "input[required]",
    desc="必填字段"
)

# ========== 复杂选择器 ==========
FIRST_TABLE_CELL = Element(
    "css", "table tbody tr:first-child td:nth-child(2)",
    desc="表格第一行第二列"
)

ACTIVE_TAB = Element(
    "css", ".nav-tabs > li.active > a",
    desc="当前激活的标签页"
)

# ========== 伪类选择器 ==========
CHECKED_CHECKBOX = Element(
    "css", "input[type='checkbox']:checked",
    desc="已选中的复选框"
)
```

---

### 1.9 XPath 选择器

使用 XPath 表达式定位元素。

```python
# ========== 相对路径（推荐） ==========
USERNAME_XPATH = Element(
    "xpath", "//input[@name='username']",
    desc="用户名输入框"
)

# ========== 文本匹配 ==========
BUTTON_BY_TEXT = Element(
    "xpath", "//button[text()='登录']",
    desc="登录按钮"
)

CONTAINS_TEXT = Element(
    "xpath", "//div[contains(text(), '成功')]",
    desc="包含'成功'的div"
)

# ========== 属性匹配 ==========
BY_CLASS = Element(
    "xpath", "//div[@class='alert alert-danger']",
    desc="错误提示框"
)

BY_ID = Element(
    "xpath", "//input[@id='password']",
    desc="密码框"
)

# ========== 层级关系 ==========
PARENT_TO_CHILD = Element(
    "xpath", "//form[@id='login']//input[@type='submit']",
    desc="登录表单中的提交按钮"
)

FOLLOWING_SIBLING = Element(
    "xpath", "//label[text()='用户名']/following-sibling::input",
    desc="用户名标签后的输入框"
)

# ========== 索引定位 ==========
SECOND_ROW = Element(
    "xpath", "(//table//tr)[2]",
    desc="表格第二行"
)

THIRD_BUTTON = Element(
    "xpath", "(//button[@class='btn'])[3]",
    desc="第三个按钮"
)

# ========== 复杂条件 ==========
COMPLEX_XPATH = Element(
    "xpath", "//tr[td[1]='张三' and td[2]='管理员']//button[text()='编辑']",
    desc="张三管理员行的编辑按钮"
)
```

---

## 2. 链式操作

### 2.1 filter() 筛选

通过 `filter_params` 参数进行筛选。

```python
# ========== has_text 筛选 ==========
COPY_BUTTON = Element(
    "role", ("button", "操作"),
    desc="复制按钮",
    filter_params={"has_text": "复制"}
)

DELETE_LINK = Element(
    "role", ("link",),
    desc="删除链接",
    filter_params={"has_text": "删除"}
)

# ========== has_not_text 反向筛选 ==========
NOT_DISABLED_BUTTON = Element(
    "role", ("button",),
    desc="非禁用按钮",
    filter_params={"has_not_text": "禁用"}
)
```

---

### 2.2 first() 第一个

获取匹配的第一个元素。

```python
FIRST_CHECKBOX = Element(
    "role", ("checkbox",),
    desc="第一个复选框",
    first=True
)

FIRST_ROW = Element(
    "css", "table tbody tr",
    desc="表格第一行数据",
    first=True
)

FIRST_PRODUCT = Element(
    "css", ".product-card",
    desc="第一个商品卡片",
    first=True
)
```

---

### 2.3 last() 最后一个

获取匹配的最后一个元素。

```python
LAST_ITEM = Element(
    "css", ".list-item",
    desc="列表最后一项",
    last=True
)

LAST_MESSAGE = Element(
    "role", ("listitem",),
    desc="最新消息",
    last=True
)

LAST_TAB = Element(
    "role", ("tab",),
    desc="最后一个标签页",
    last=True
)
```

---

### 2.4 nth(n) 第 n 个

获取指定索引位置的元素（索引从 0 开始）。

```python
# ========== 正向索引 ==========
SECOND_ROW = Element(
    "css", "table tbody tr",
    desc="表格第二行",
    nth=1  # 索引从 0 开始，1 表示第二个
)

THIRD_BUTTON = Element(
    "role", ("button", "删除"),
    desc="第三个删除按钮",
    nth=2
)

FIFTH_ITEM = Element(
    "css", ".menu-item",
    desc="第五个菜单项",
    nth=4
)

# ========== 负向索引（倒数） ==========
SECOND_LAST = Element(
    "css", ".notification",
    desc="倒数第二条通知",
    nth=-2
)
```

---

## 3. 组合使用（复杂场景）

### 3.1 filter + first

筛选后取第一个匹配的元素。

```python
FIRST_ACTIVE_TAB = Element(
    "role", ("tab",),
    desc="第一个激活的标签页",
    filter_params={"has_text": "已激活"},
    first=True
)

FIRST_COMPLETED_TASK = Element(
    "role", ("listitem",),
    desc="第一个已完成任务",
    filter_params={"has_text": "已完成"},
    first=True
)
```

---

### 3.2 filter + nth

筛选后取第 n 个元素。

```python
THIRD_PENDING_ORDER = Element(
    "role", ("row",),
    desc="第三个待处理订单",
    filter_params={"has_text": "待处理"},
    nth=2
)

SECOND_ERROR_MESSAGE = Element(
    "css", ".message",
    desc="第二条错误消息",
    filter_params={"has_text": "错误"},
    nth=1
)
```

---

### 3.3 filter + last

筛选后取最后一个元素。

```python
LATEST_COMMENT = Element(
    "role", ("article",),
    desc="最新评论",
    filter_params={"has_text": "评论时间"},
    last=True
)

LAST_WARNING = Element(
    "css", ".alert-warning",
    desc="最后一个警告",
    filter_params={"has_text": "警告"},
    last=True
)
```

---

## 4. 实际业务场景示例

### 4.1 登录页面

```python
from pages.base_page import BasePage
from utils.element import Element


class LoginPage(BasePage):
    """登录页面元素定义"""

    # 输入框 - 使用 placeholder
    USERNAME_INPUT = Element(
        "placeholder", "请输入用户名/手机号/邮箱",
        desc="用户名输入框"
    )

    PASSWORD_INPUT = Element(
        "placeholder", "请输入密码",
        desc="密码输入框"
    )

    # 复选框 - 使用 label
    REMEMBER_ME = Element(
        "label", "记住我",
        desc="记住密码复选框"
    )

    # 按钮 - 使用 role
    LOGIN_BUTTON = Element(
        "role", ("button", "登录"),
        desc="登录按钮",
        exact=True
    )

    # 链接 - 使用 role
    FORGOT_PASSWORD_LINK = Element(
        "role", ("link", "忘记密码"),
        desc="忘记密码链接"
    )

    REGISTER_LINK = Element(
        "role", ("link", "立即注册"),
        desc="注册链接"
    )

    # 错误提示 - 使用 css
    ERROR_MESSAGE = Element(
        "css", ".login-error",
        desc="登录错误提示"
    )

    # 验证码 - 使用 testid
    CAPTCHA_IMAGE = Element(
        "testid", "captcha-img",
        desc="验证码图片"
    )

    CAPTCHA_INPUT = Element(
        "placeholder", "验证码",
        desc="验证码输入框"
    )


    def login(self, username: str, password: str, remember: bool = False):
        """登录操作"""
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)

        if remember:
            self.check(self.REMEMBER_ME)

        self.click(self.LOGIN_BUTTON)
```

---

### 4.2 表格操作页面

```python
class UserManagePage(BasePage):
    """用户管理页面"""

    # 搜索框
    SEARCH_INPUT = Element(
        "role", ("searchbox", "搜索用户"),
        desc="用户搜索框"
    )

    SEARCH_BUTTON = Element(
        "role", ("button", "搜索"),
        desc="搜索按钮"
    )

    # 添加按钮
    ADD_USER_BUTTON = Element(
        "role", ("button", "添加用户"),
        desc="添加用户按钮"
    )

    # 表格
    USER_TABLE = Element(
        "role", ("table",),
        desc="用户列表表格"
    )

    # 第一行数据
    FIRST_USER_ROW = Element(
        "css", "table tbody tr",
        desc="第一个用户行",
        first=True
    )

    # 第三行数据
    THIRD_USER_ROW = Element(
        "css", "table tbody tr",
        desc="第三个用户行",
        nth=2
    )

    # 批量操作
    FIRST_CHECKBOX = Element(
        "role", ("checkbox",),
        desc="第一个复选框",
        first=True
    )

    BATCH_DELETE_BUTTON = Element(
        "role", ("button", "批量删除"),
        desc="批量删除按钮"
    )

    # 分页
    NEXT_PAGE_BUTTON = Element(
        "role", ("button", "下一页"),
        desc="下一页按钮"
    )


    def search_user(self, keyword: str):
        """搜索用户"""
        self.fill(self.SEARCH_INPUT, keyword)
        self.click(self.SEARCH_BUTTON)

    def get_user_edit_button(self, username: str) -> Element:
        """获取指定用户的编辑按钮（动态定位）"""
        return Element(
            "xpath", f"//tr[td[text()='{username}']]//button[text()='编辑']",
            desc=f"{username} 的编辑按钮"
        )

    def edit_user(self, username: str):
        """编辑指定用户"""
        edit_btn = self.get_user_edit_button(username)
        self.click(edit_btn)
```

---

### 4.3 商品列表页面

```python
class ProductListPage(BasePage):
    """商品列表页面"""

    # 筛选器
    CATEGORY_FILTER = Element(
        "role", ("combobox", "商品分类"),
        desc="分类筛选器"
    )

    PRICE_MIN_INPUT = Element(
        "placeholder", "最低价",
        desc="最低价输入框"
    )

    PRICE_MAX_INPUT = Element(
        "placeholder", "最高价",
        desc="最高价输入框"
    )

    APPLY_FILTER_BUTTON = Element(
        "role", ("button", "应用筛选"),
        desc="应用筛选按钮"
    )

    # 商品卡片
    FIRST_PRODUCT = Element(
        "css", ".product-card",
        desc="第一个商品卡片",
        first=True
    )

    THIRD_PRODUCT = Element(
        "css", ".product-card",
        desc="第三个商品卡片",
        nth=2
    )

    LAST_PRODUCT = Element(
        "css", ".product-card",
        desc="最后一个商品卡片",
        last=True
    )

    # 第一个在售商品（filter + first）
    FIRST_AVAILABLE_PRODUCT = Element(
        "css", ".product-card",
        desc="第一个在售商品",
        filter_params={"has_text": "立即购买"},
        first=True
    )

    # 第二个折扣商品（filter + nth）
    SECOND_DISCOUNT_PRODUCT = Element(
        "css", ".product-card",
        desc="第二个折扣商品",
        filter_params={"has_text": "折扣"},
        nth=1
    )


    def get_product_by_name(self, product_name: str) -> Element:
        """根据商品名称定位商品卡片"""
        return Element(
            "text", product_name,
            desc=f"商品: {product_name}"
        )

    def get_add_to_cart_button(self, product_name: str) -> Element:
        """获取指定商品的加购按钮"""
        return Element(
            "xpath",
            f"//div[contains(text(), '{product_name}')]/ancestor::div[@class='product-card']//button[text()='加入购物车']",
            desc=f"{product_name} 的加购按钮"
        )
```

---

### 4.4 表单页面

```python
class UserFormPage(BasePage):
    """用户表单页面"""

    # 基本信息
    USERNAME_INPUT = Element(
        "label", "用户名",
        desc="用户名输入框"
    )

    EMAIL_INPUT = Element(
        "label", "邮箱地址",
        desc="邮箱输入框"
    )

    PHONE_INPUT = Element(
        "placeholder", "请输入11位手机号",
        desc="手机号输入框"
    )

    # 性别单选
    GENDER_MALE = Element(
        "label", "男",
        desc="性别-男"
    )

    GENDER_FEMALE = Element(
        "label", "女",
        desc="性别-女"
    )

    # 角色多选
    ROLE_ADMIN = Element(
        "label", "管理员",
        desc="角色-管理员"
    )

    ROLE_USER = Element(
        "label", "普通用户",
        desc="角色-普通用户"
    )

    # 下拉选择
    DEPARTMENT_SELECT = Element(
        "label", "所属部门",
        desc="部门下拉框"
    )

    # 日期选择
    BIRTHDAY_PICKER = Element(
        "label", "出生日期",
        desc="生日选择器"
    )

    # 文本域
    BIO_TEXTAREA = Element(
        "placeholder", "请输入个人简介...",
        desc="个人简介文本域"
    )

    # 提交按钮
    SUBMIT_BUTTON = Element(
        "testid", "submit-form",
        desc="提交表单按钮"
    )

    CANCEL_BUTTON = Element(
        "role", ("button", "取消"),
        desc="取消按钮"
    )


    def fill_user_info(self, username: str, email: str, gender: str):
        """填写用户信息"""
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.EMAIL_INPUT, email)

        if gender == "男":
            self.click(self.GENDER_MALE)
        else:
            self.click(self.GENDER_FEMALE)

        self.click(self.SUBMIT_BUTTON)
```

---

### 4.5 对话框/弹窗

```python
class DialogPage(BasePage):
    """对话框页面"""

    # 确认对话框
    CONFIRM_DIALOG = Element(
        "role", ("dialog", "确认操作"),
        desc="确认对话框"
    )

    CONFIRM_TITLE = Element(
        "role", ("heading", "确认删除"),
        desc="对话框标题"
    )

    CONFIRM_MESSAGE = Element(
        "text", "确定要删除吗？此操作不可恢复。",
        desc="确认提示信息"
    )

    CONFIRM_YES_BUTTON = Element(
        "role", ("button", "确定"),
        desc="确定按钮",
        exact=True
    )

    CONFIRM_NO_BUTTON = Element(
        "role", ("button", "取消"),
        desc="取消按钮"
    )

    # 关闭按钮
    CLOSE_BUTTON = Element(
        "title", "关闭",
        desc="对话框关闭按钮"
    )

    # 提示框
    SUCCESS_TOAST = Element(
        "css", ".toast-success",
        desc="成功提示框"
    )

    ERROR_TOAST = Element(
        "css", ".toast-error",
        desc="错误提示框"
    )

    # 最新的一条提示
    LATEST_TOAST = Element(
        "css", ".toast",
        desc="最新提示框",
        last=True
    )


    def confirm_delete(self):
        """确认删除操作"""
        self.wait_for_selector(self.CONFIRM_DIALOG)
        self.click(self.CONFIRM_YES_BUTTON)
```

---

### 4.6 复杂表格场景

```python
class OrderTablePage(BasePage):
    """订单表格页面"""

    # 表格头部
    TABLE_HEADER = Element(
        "role", ("rowheader", "订单号"),
        desc="订单号列头"
    )

    # 所有数据行
    ALL_ROWS = Element(
        "css", "table tbody tr",
        desc="所有订单行"
    )

    # 第一个待支付订单
    FIRST_PENDING_ORDER = Element(
        "css", "table tbody tr",
        desc="第一个待支付订单",
        filter_params={"has_text": "待支付"},
        first=True
    )

    # 最后一个已完成订单
    LAST_COMPLETED_ORDER = Element(
        "css", "table tbody tr",
        desc="最后一个已完成订单",
        filter_params={"has_text": "已完成"},
        last=True
    )

    # 第三个已发货订单
    THIRD_SHIPPED_ORDER = Element(
        "css", "table tbody tr",
        desc="第三个已发货订单",
        filter_params={"has_text": "已发货"},
        nth=2
    )

    # 批量操作
    SELECT_ALL_CHECKBOX = Element(
        "role", ("checkbox", "全选"),
        desc="全选复选框"
    )

    BATCH_EXPORT_BUTTON = Element(
        "role", ("button", "批量导出"),
        desc="批量导出按钮"
    )


    def get_order_row(self, order_id: str) -> Element:
        """根据订单号定位订单行"""
        return Element(
            "role", ("row",),
            desc=f"订单 {order_id} 的行",
            filter_params={"has_text": order_id}
        )

    def get_order_detail_button(self, order_id: str) -> Element:
        """获取订单详情按钮"""
        return Element(
            "xpath", f"//tr[contains(., '{order_id}')]//button[text()='查看详情']",
            desc=f"订单 {order_id} 的详情按钮"
        )

    def cancel_order(self, order_id: str):
        """取消订单"""
        cancel_btn = Element(
            "xpath", f"//tr[td[text()='{order_id}']]//button[text()='取消订单']",
            desc=f"订单 {order_id} 的取消按钮"
        )
        self.click(cancel_btn)
```

---

## 定位器选择建议

| 场景 | 推荐定位器 | 示例 | 优点 |
|------|-----------|------|------|
| **按钮** | `role` | `("button", "提交")` | 符合可访问性标准 |
| **输入框** | `placeholder` 或 `label` | `"请输入用户名"` | 语义清晰 |
| **链接** | `role` | `("link", "注册")` | 可读性好 |
| **复选框/单选框** | `label` | `"记住我"` | 与用户视角一致 |
| **文本内容** | `text` | `"欢迎回来"` | 直观 |
| **图片** | `alt_text` | `"产品图片"` | 语义化 |
| **关键元素** | `testid`（最稳定） | `"submit-btn"` | 不受UI变化影响 |
| **复杂定位** | `xpath` 或 `css` | `"//tr[td='张三']//button"` | 灵活强大 |
| **动态列表** | `filter` + `nth` | `filter_params={"has_text": "已完成"}, nth=2` | 精准定位 |

---

## 最佳实践

### 1. 优先级顺序

推荐按以下优先级选择定位器：

1. **testid** - 最稳定，适用于关键元素
2. **role** - 符合可访问性标准，推荐日常使用
3. **placeholder / label** - 适用于表单元素
4. **text** - 适用于文本内容
5. **css / xpath** - 作为兜底方案

### 2. 描述信息

**必须为每个元素添加 desc 描述**，方便：
- 日志追踪
- 错误排查
- 团队协作

```python
# ✅ 好的写法
LOGIN_BTN = Element(
    "role", ("button", "登录"),
    desc="登录按钮"  # 清晰描述
)

# ❌ 不推荐
LOGIN_BTN = Element(
    "role", ("button", "登录")  # 缺少描述
)
```

### 3. 命名规范

元素常量命名建议：
- 使用全大写 + 下划线
- 以元素类型结尾（BUTTON, INPUT, LINK 等）

```python
# ✅ 好的命名
USERNAME_INPUT = Element(...)
SUBMIT_BUTTON = Element(...)
FORGOT_PASSWORD_LINK = Element(...)

# ❌ 不推荐
username = Element(...)
btn_submit = Element(...)
```

### 4. 动态定位器

对于需要动态参数的元素，使用方法返回 Element 对象：

```python
def get_user_edit_button(self, username: str) -> Element:
    """获取指定用户的编辑按钮"""
    return Element(
        "xpath", f"//tr[td[text()='{username}']]//button[text()='编辑']",
        desc=f"{username} 的编辑按钮"
    )

# 使用
self.click(self.get_user_edit_button("张三"))
```

---

## 日志输出示例

使用 Element 配置类后，日志会自动包含元素描述：

```
[INFO] 尝试点击元素: 登录按钮 [role=('button', '登录')]
[DEBUG] 构建定位器: 登录按钮 [role=('button', '登录')]
[DEBUG] 使用 Role 定位器: role=button, name=登录
[INFO] 成功点击元素: 登录按钮 [role=('button', '登录')]
```

对于复杂定位器（带 filter + nth）：

```
[INFO] 尝试点击元素: 第二个待支付订单 [css=table tbody tr]
[DEBUG] 构建定位器: 第二个待支付订单 [css=table tbody tr]
[DEBUG] 应用 filter: {'has_text': '待支付'}
[DEBUG] 应用 nth(1)
[INFO] 成功点击元素: 第二个待支付订单 [css=table tbody tr]
```

---

## 常见问题 FAQ

### Q1: Element 和原有的元组定位器可以混用吗？

**可以**。框架完全向后兼容，三种定位器可以同时使用：

```python
class MyPage(BasePage):
    # 旧方式（仍然支持）
    OLD_BUTTON = ("button", "登录")

    # 新方式（推荐）
    NEW_BUTTON = Element("role", ("button", "登录"), desc="登录按钮")

    def test_method(self):
        self.click(self.OLD_BUTTON)  # ✅ 可以
        self.click(self.NEW_BUTTON)  # ✅ 推荐
        self.click("#login-btn")     # ✅ 可以
```

### Q2: filter_params 支持哪些参数？

常用参数：
- `has_text`: 包含指定文本
- `has_not_text`: 不包含指定文本
- `has`: 包含子元素（需传入 Locator，建议用 XPath 代替）

### Q3: first、last、nth 可以同时使用吗？

**不可以**。这三个参数互斥，Element 类会在初始化时进行验证。

```python
# ❌ 错误用法
ELEMENT = Element("css", ".item", first=True, nth=2)  # 会抛出 ValueError

# ✅ 正确用法
FIRST = Element("css", ".item", first=True)
SECOND = Element("css", ".item", nth=1)
```

### Q4: 如何处理动态文本内容？

使用 XPath 的 `contains()` 函数或动态构建 Element：

```python
# 方法1: XPath contains
ERROR_MSG = Element(
    "xpath", "//div[contains(text(), '错误')]",
    desc="错误提示"
)

# 方法2: 动态构建
def get_user_row(self, username: str) -> Element:
    return Element(
        "xpath", f"//tr[td[text()='{username}']]",
        desc=f"{username} 的数据行"
    )
```

---

## 总结

Element 配置类提供了：

✅ **支持所有 Playwright 定位方式**（8种）
✅ **元素描述信息**（desc），方便日志追踪和问题排查
✅ **链式操作**（filter、first、last、nth）
✅ **向后兼容**，可与原有定位器混用
✅ **类型安全**，IDE 提示友好
✅ **配置化管理**，定位器集中维护

开始使用 Element 配置类，让你的自动化测试更加健壮、可维护！
