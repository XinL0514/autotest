import pytest

from pages.modules.aixmy.aixmy_page import AixmyPage
from utils.logger import Logger

logger = Logger.get_logger("AixmyFixtures")


@pytest.fixture
def end_class(request):
    """
    后置下课 fixture。

    用法：在测试方法参数里声明 end_class，并在进入课堂后调用
    end_class(aixmy_page) 注册页面对象。测试结束后自动调用下课接口。

    示例：
        def test_foo(self, authenticated_page, end_class):
            aixmy_page = AixmyPage(authenticated_page)
            ...
            aixmy_page.launch_courseware()
            end_class(aixmy_page)   # 注册，后置自动下课
            ...
    """
    _page_obj: AixmyPage | None = None

    def register(page_obj: AixmyPage) -> None:
        nonlocal _page_obj
        _page_obj = page_obj

    yield register

    if _page_obj is None:
        return
    try:
        _page_obj.end_class_via_api()
    except Exception as e:
        logger.warning(f"end_class teardown failed: {e}")
