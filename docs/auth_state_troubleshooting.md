# 认证状态管理问题排查与解决

## 问题描述

每次运行测试时都会重新登录，即使已经配置了认证状态管理（cookie 管理）。

---

## 问题根因

通过诊断工具 `scripts/check_auth_state.py` 发现：

```
🍪 Cookies 数量: 0
⚠️  警告: 没有 cookies
```

**核心问题**：认证状态文件 `test_data/auth_state.json` 虽然存在，但是 **没有保存 cookies**。

---

## 为什么没有 cookies？

可能的原因：
1. ❌ 登录时页面还没有完全加载完成就保存了状态
2. ❌ 登录时网站没有设置 cookies（登录失败）
3. ❌ 保存认证状态的时机太早，cookies 还没有被设置

---

## 解决方案

### 1. 增强登录流程（已完成）

在 `conftest.py` 的 `_perform_login()` 函数中：

✅ **增加详细日志**
```python
print("ℹ️  访问登录页面...")
print(f"ℹ️  输入用户名: {login_data['username']}")
print("ℹ️  等待登录完成（查找'用药记录'按钮）...")
```

✅ **增加等待时间**
```python
# 等待登录成功
page.wait_for_selector("button:has-text('用药记录')", timeout=10000)  # 10秒

# 额外等待，确保所有 cookies 都设置完成
page.wait_for_timeout(1000)
```

✅ **保存前检查 cookies**
```python
cookies = context.cookies()
print(f"ℹ️  当前 Cookies 数量: {len(cookies)}")

if len(cookies) == 0:
    print("⚠️  警告: 登录后没有 cookies，可能登录失败！")
    # 保存调试截图
    page.screenshot(path="test_data/login_debug.png")
```

### 2. 增强认证状态验证（已完成）

在 `_is_auth_state_valid()` 函数中：

✅ **增加超时时间**
```python
page.goto(BASE_URL, timeout=15000)  # 从 10 秒增加到 15 秒
page.wait_for_timeout(2000)         # 从 1 秒增加到 2 秒
page.wait_for_selector("button:has-text('用药记录')", timeout=10000)  # 从 5 秒增加到 10 秒
```

✅ **增加详细日志**
```python
print("ℹ️  开始验证认证状态...")
print(f"ℹ️  访问主页: {BASE_URL}")
print("ℹ️  检查登录状态（查找'用药记录'按钮）...")
```

---

## 使用方法

### 1. 清除旧的认证状态

```bash
# 删除旧的认证状态文件（强制重新登录）
rm test_data/auth_state.json
```

### 2. 运行诊断工具

```bash
# 检查认证状态文件的详细信息
python3 scripts/check_auth_state.py
```

**正常输出应该是：**
```
🍪 Cookies 数量: X  (X > 0)
🍪 Cookies 详情:
   1. cookie_name_1       | domain.com             | 过期: 2025-12-31 17:00:00 ✅ 有效
   2. cookie_name_2       | domain.com             | 过期: 会话结束
   ...
```

### 3. 运行测试并观察日志

```bash
pytest tests/mar/test_mar.py -v -s
```

**正常流程应该显示：**

```
============================================================
📋 认证状态检查开始
============================================================
ℹ️  开始验证认证状态...
ℹ️  访问主页: http://your-base-url
ℹ️  检查登录状态（查找'用药记录'按钮）...
✅ 认证状态有效，找到'用药记录'按钮
✅ 使用现有有效的认证状态（文件创建于 5.2 分钟前）
============================================================
```

**如果需要重新登录，会显示：**

```
🔄 开始重新登录...

🔐 执行登录流程...
ℹ️  访问登录页面...
ℹ️  输入用户名: your_username
ℹ️  输入密码: ********
ℹ️  等待登录完成（查找'用药记录'按钮）...
✅ 登录成功，已检测到主页元素
ℹ️  等待 cookies 设置...
ℹ️  当前 Cookies 数量: 5
ℹ️  Cookies 示例:
      - session_id: example.com
      - user_token: example.com
      - remember_me: example.com
✅ 登录状态已保存到: test_data/auth_state.json
```

---

## 认证状态管理机制

### Session Scope 说明

```python
@pytest.fixture(scope="session")
def authenticated_state(browser: Browser) -> Path:
    """Session 级别的 fixture"""
```

**行为特点：**
- ✅ 在一次 pytest 运行中，只会执行一次登录
- ✅ 同一次运行的所有测试共享同一个认证状态
- ⚠️ 每次重新运行 pytest，会重新检查认证状态

### 三重检查机制

每次运行测试时，会依次检查：

1. **文件存在性检查**
   ```
   检查: test_data/auth_state.json 是否存在
   不存在 → 重新登录
   ```

2. **文件过期检查**
   ```
   检查: 文件修改时间是否超过 1 小时
   过期 → 重新登录
   ```

3. **认证状态有效性检查**
   ```
   检查: 使用保存的 cookies 访问主页，能否找到'用药记录'按钮
   找不到 → 重新登录（之前的问题出在这里）
   ```

只有三个检查都通过，才会复用现有的认证状态。

---

## 常见问题

### Q1: 为什么第一次运行测试会登录？

**答**：正常现象。第一次运行时 `auth_state.json` 不存在，必须登录一次保存认证状态。

### Q2: 为什么每次重新运行 pytest 都检查认证状态？

**答**：因为 `scope="session"`，每次新的 pytest 进程启动时，session 重新开始，所以会重新检查。但如果认证状态有效，不会重新登录。

### Q3: 如何强制重新登录？

```bash
# 删除认证状态文件
rm test_data/auth_state.json

# 运行测试
pytest tests/mar/test_mar.py -v -s
```

### Q4: 认证状态的有效期是多久？

```python
# conftest.py
AUTH_STATE_EXPIRY = 60 * 60  # 1 小时
```

可以根据实际 token 过期时间调整。

### Q5: 如果登录失败怎么办？

登录失败时会：
1. 打印详细错误信息
2. 保存调试截图到 `test_data/login_debug.png`
3. 抛出异常，终止测试

---

## 调试技巧

### 1. 查看认证状态文件内容

```bash
# 查看 JSON 内容
cat test_data/auth_state.json | python3 -m json.tool

# 或使用诊断工具
python3 scripts/check_auth_state.py
```

### 2. 查看登录截图

如果登录失败或 cookies 为空，会自动保存截图：
```
test_data/login_debug.png   # 登录后但 cookies 为空
test_data/login_error.png   # 登录过程出错
```

### 3. 增加日志级别

在测试中临时增加等待时间，观察页面状态：
```python
def _perform_login(browser: Browser) -> Path:
    # ...
    login_page.login(username, password)

    # 增加等待时间，观察浏览器
    page.wait_for_timeout(5000)  # 等待 5 秒

    cookies = context.cookies()
    print(f"Cookies: {cookies}")  # 打印所有 cookies
```

---

## 总结

### 问题根因
- 认证状态文件没有保存 cookies

### 解决方案
1. ✅ 增加登录后的等待时间
2. ✅ 保存前检查 cookies 数量
3. ✅ 增加详细日志输出
4. ✅ 增加认证状态验证的超时时间
5. ✅ 提供诊断工具

### 验证方法
```bash
# 1. 删除旧的认证状态
rm test_data/auth_state.json

# 2. 运行测试
pytest tests/mar/test_mar.py -v -s

# 3. 观察日志输出
# 应该显示: ℹ️  当前 Cookies 数量: X (X > 0)

# 4. 再次运行测试
pytest tests/mar/test_mar.py -v -s

# 5. 应该显示: ✅ 使用现有有效的认证状态
```

如果仍然每次都重新登录，请查看日志中具体是哪个检查失败了。
