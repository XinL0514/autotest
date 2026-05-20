# -*- coding: utf-8 -*-
import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.config import BASE_URL

RECORDINGS_DIR = PROJECT_ROOT / "tools" / "recordings"
DEFAULT_AUTH_FILE = PROJECT_ROOT / "test_data" / "auth_state.json"
DEFAULT_DEVICE = "Galaxy S9+"
DEFAULT_BROWSER = "chromium"
BROWSER_TYPES = ["chromium", "firefox", "webkit"]
OUTPUT_FORMATS = ["python", "pytest"]


def parse_viewport(value: str) -> str:
    try:
        w, h = value.split(",")
        width, height = int(w), int(h)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--viewport 格式应为 width,height，例如 1920,1080") from exc
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("--viewport 宽高必须大于 0")
    return f"{width},{height}"


def sanitize_output_name(name: str) -> str:
    normalized = name.strip().replace(".py", "")
    if not normalized:
        raise ValueError("--output 不能为空")
    if any(sep in normalized for sep in ("/", "\\")):
        raise ValueError("--output 只能是文件名，不能包含路径")
    return normalized


def build_output_path(output_name: Optional[str]) -> Path:
    RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
    if output_name:
        safe_name = sanitize_output_name(output_name)
        return RECORDINGS_DIR / f"{safe_name}.py"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return RECORDINGS_DIR / f"recording_{timestamp}.py"


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python tools/record.py",
        description="Playwright codegen 录制脚本（已适配当前 autotest 项目）",
    )

    parser.add_argument("url", nargs="?", default=BASE_URL, help="录制目标 URL，默认使用 config/config.py 的 BASE_URL")
    parser.add_argument("--platform", "-p", action="store_true", help="桌面模式（不启用移动设备模拟）")
    parser.add_argument("--device", "-d", default=None, help=f"移动设备名称，默认 {DEFAULT_DEVICE}")
    parser.add_argument("--browser", "-b", choices=BROWSER_TYPES, default=DEFAULT_BROWSER, help="浏览器类型")
    parser.add_argument("--viewport", "-v", type=parse_viewport, help="视口大小，格式 width,height")
    parser.add_argument("--lang", "-l", help="浏览器语言，例如 zh-CN")
    parser.add_argument("--ignore-https-errors", action="store_true", help="忽略 HTTPS 证书错误")

    parser.add_argument("--auth", action="store_true", help="加载 test_data/auth_state.json 作为登录态")
    parser.add_argument("--auth-file", help="自定义登录态文件路径（覆盖 --auth 默认文件）")
    parser.add_argument("--save-auth", action="store_true", help="录制结束保存登录态到 test_data/auth_state.json")
    parser.add_argument("--save-auth-file", help="自定义保存登录态路径（覆盖 --save-auth 默认文件）")

    parser.add_argument("--output", "-o", help="输出文件名（不含 .py），默认 recording_时间戳")
    parser.add_argument("--format", "-f", choices=OUTPUT_FORMATS, default="python", help="codegen 输出格式")
    parser.add_argument("--list-devices", action="store_true", help="列出可用设备并退出")

    return parser


def list_devices() -> int:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            names = sorted(p.devices.keys())
            for name in names:
                print(name)
            print(f"\nTotal: {len(names)}")
            return 0
    except Exception as exc:
        print(f"列出设备失败: {exc}")
        return 1


def resolve_auth_paths(args: argparse.Namespace) -> tuple[Optional[Path], Optional[Path]]:
    load_auth = None
    save_auth = None

    if args.auth_file:
        load_auth = Path(args.auth_file).expanduser().resolve()
    elif args.auth:
        load_auth = DEFAULT_AUTH_FILE

    if args.save_auth_file:
        save_auth = Path(args.save_auth_file).expanduser().resolve()
    elif args.save_auth:
        save_auth = DEFAULT_AUTH_FILE

    return load_auth, save_auth


def validate_args(args: argparse.Namespace, load_auth: Optional[Path]) -> None:
    if args.platform and args.device:
        raise ValueError("--platform 与 --device 不能同时使用")

    if load_auth and not load_auth.exists():
        raise FileNotFoundError(f"登录态文件不存在: {load_auth}")


def build_codegen_command(
    args: argparse.Namespace,
    output_file: Path,
    load_auth: Optional[Path],
    save_auth: Optional[Path],
) -> list[str]:
    cmd = [
        sys.executable,
        "-m",
        "playwright",
        "codegen",
        args.url,
        "--target",
        args.format,
        "--output",
        str(output_file),
    ]

    if not args.platform:
        device = args.device or DEFAULT_DEVICE
        cmd.extend(["--device", device])

    if args.browser != DEFAULT_BROWSER:
        cmd.extend(["--browser", args.browser])

    if args.viewport:
        cmd.extend(["--viewport-size", args.viewport])

    if args.lang:
        cmd.extend(["--lang", args.lang])

    if args.ignore_https_errors:
        cmd.append("--ignore-https-errors")

    if load_auth:
        cmd.extend(["--load-storage", str(load_auth)])

    if save_auth:
        save_auth.parent.mkdir(parents=True, exist_ok=True)
        cmd.extend(["--save-storage", str(save_auth)])

    return cmd


def main() -> int:
    parser = create_parser()
    args = parser.parse_args()

    if args.list_devices:
        return list_devices()

    try:
        output_file = build_output_path(args.output)
        load_auth, save_auth = resolve_auth_paths(args)
        validate_args(args, load_auth)
    except Exception as exc:
        print(f"参数错误: {exc}")
        return 2

    cmd = build_codegen_command(args, output_file, load_auth, save_auth)

    print("=" * 60)
    print("Playwright 录制（autotest）")
    print("=" * 60)
    print(f"URL: {args.url}")
    print(f"Output: {output_file}")
    print(f"Browser: {args.browser}")
    print(f"Mode: {'desktop' if args.platform else 'device'}")
    if not args.platform:
        print(f"Device: {args.device or DEFAULT_DEVICE}")
    print(f"Auth load: {load_auth if load_auth else 'none'}")
    print(f"Auth save: {save_auth if save_auth else 'none'}")
    print("Command:")
    print(" ".join(cmd))
    print("关闭录制浏览器窗口即可结束录制")
    print("=" * 60)

    try:
        process = subprocess.Popen(cmd, cwd=str(PROJECT_ROOT))
        exit_code = process.wait()
    except KeyboardInterrupt:
        print("录制已中断")
        return 1
    except FileNotFoundError as exc:
        print(f"启动失败: {exc}")
        return 1

    if exit_code != 0:
        print(f"录制失败，退出码: {exit_code}")
        return exit_code

    if not output_file.exists():
        print(f"录制结束，但未找到输出文件: {output_file}")
        return 1

    if output_file.stat().st_size == 0:
        print(f"录制完成，但输出文件为空: {output_file}")
        return 1

    print(f"录制完成: {output_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
