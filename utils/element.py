from dataclasses import dataclass, field
from typing import Union, Tuple, Dict, Any, Optional


@dataclass
class Element:
    """元素定位器配置类

    支持 Playwright 所有定位方式 + 链式操作 + 描述信息

    Examples:
        # 基础用法
        LOGIN_BTN = Element("role", ("button", "登录"), desc="登录按钮")

        # 带 exact 参数
        USERNAME = Element("placeholder", "请输入用户名", desc="用户名输入框", exact=True)

        # 使用 filter
        COPY_BTN = Element(
            "role", ("button", "操作"),
            desc="复制按钮",
            filter_params={"has_text": "复制"}
        )

        # 使用 nth
        FIRST_ROW = Element("css", "table tr", desc="第一行", nth=0)

        # 使用 first()
        FIRST_ITEM = Element("css", ".item", desc="第一个项目", first=True)

        # 组合使用
        TARGET_CELL = Element(
            "role", ("cell",),
            desc="包含'已完成'的第二个单元格",
            filter_params={"has_text": "已完成"},
            nth=1
        )
    """

    by: str  # 定位方式: role, text, placeholder, label, testid, css, xpath, title, alt_text
    value: Union[str, Tuple[str, ...]]  # 定位值
    desc: str = ""  # 元素描述（用于日志和报错）

    # Playwright 参数
    exact: bool = False  # 精确匹配

    # 链式操作参数
    filter_params: Optional[Dict[str, Any]] = None  # filter() 参数，如 {"has_text": "复制"}
    nth: Optional[int] = None  # nth(n) 获取第 n 个
    first: bool = False  # first() 获取第一个
    last: bool = False  # last() 获取最后一个

    # 其他可选参数
    timeout: Optional[int] = None  # 自定义超时时间

    def __post_init__(self):
        """验证参数合法性"""
        valid_methods = [
            "role", "text", "placeholder", "label", "testid",
            "css", "xpath", "title", "alt_text"
        ]
        if self.by not in valid_methods:
            raise ValueError(
                f"不支持的定位方式: {self.by}，"
                f"支持的方式: {', '.join(valid_methods)}"
            )

        # 确保 filter_params 是字典
        if self.filter_params is None:
            self.filter_params = {}

        # 验证互斥的链式操作
        chain_operations = [self.first, self.last, self.nth is not None]
        if sum(chain_operations) > 1:
            raise ValueError(
                "first、last、nth 只能使用其中一个，不能同时使用"
            )

    def get_description(self) -> str:
        """获取元素的完整描述（用于日志）"""
        if self.desc:
            return f"{self.desc} [{self.by}={self.value}]"
        else:
            return f"[{self.by}={self.value}]"
