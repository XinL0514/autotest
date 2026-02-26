import yaml
from pathlib import Path


class DataLoader:
    TEST_DATA_DIR = Path(__file__).resolve().parent.parent / "test_data"

    @staticmethod
    def load_yaml(file_name: str) -> dict:
        file_path = DataLoader.TEST_DATA_DIR / file_name
        if not file_path.exists():
            raise FileNotFoundError(f"测试数据文件不存在: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if data is None:
            raise ValueError(f"测试数据文件为空: {file_path}")
        if not isinstance(data, dict):
            raise TypeError(
                f"测试数据文件结构错误: {file_path}, 期望 dict，实际为 {type(data).__name__}"
            )
        return data

    @staticmethod
    def get_test_data(file_name: str, key: str) -> dict:
        data = DataLoader.load_yaml(file_name)
        if key not in data:
            available_keys = ", ".join(map(str, data.keys())) if data else "无"
            raise KeyError(
                f"测试数据 key 不存在: '{key}' (文件: {file_name})，可用 keys: {available_keys}"
            )

        value = data[key]
        if not isinstance(value, dict):
            raise TypeError(
                f"测试数据 key 结构错误: '{key}' (文件: {file_name})，"
                f"期望 dict，实际为 {type(value).__name__}"
            )
        return value
