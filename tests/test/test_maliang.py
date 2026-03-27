import os
import posixpath
import tempfile
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import allure
import openpyxl
from playwright.sync_api import Page

from pages.modules.test.test_maliang import MaliangPage
from utils.assertion import Assertion
from utils.logger import Logger

logger = Logger.get_logger("TestMaliang")
assertion = Assertion("TestMaliang")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXCEL_CANDIDATES = (
    PROJECT_ROOT / "ttttt.xlsx",
    PROJECT_ROOT / "ttttt.csv",
)


def _resolve_excel_path() -> str:
    """优先使用真正的 xlsx 文件，避免图片被当成普通 CSV 丢失。"""
    for candidate in EXCEL_CANDIDATES:
        if candidate.exists():
            logger.info(f"使用模板源文件: {candidate}")
            return str(candidate)
    raise FileNotFoundError(f"未找到模板文件，可选路径: {', '.join(str(path) for path in EXCEL_CANDIDATES)}")


EXCEL_PATH = _resolve_excel_path()

XML_NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pkg": "http://schemas.openxmlformats.org/package/2006/relationships",
    "xdr": "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}


def _normalize_zip_path(base_path: str, target: str) -> str:
    """将 xlsx 包内的相对 Target 解析为标准归档路径。"""
    if target.startswith("/"):
        return target.lstrip("/")
    return posixpath.normpath(posixpath.join(posixpath.dirname(base_path), target))


def _extract_images_from_xlsx_package(workbook_path: Path) -> dict[int, bytes]:
    """直接解析 xlsx 压缩包中的 drawing/media，规避 openpyxl 在部分环境下取不到 ws._images。"""
    image_map: dict[int, bytes] = {}

    with ZipFile(workbook_path) as archive:
        workbook_xml = ET.fromstring(archive.read("xl/workbook.xml"))
        active_view = workbook_xml.find("main:bookViews/main:workbookView", XML_NS)
        active_index = int(active_view.get("activeTab", "0")) if active_view is not None else 0

        sheets = workbook_xml.findall("main:sheets/main:sheet", XML_NS)
        if not sheets:
            return image_map

        target_sheet = sheets[min(active_index, len(sheets) - 1)]
        sheet_rel_id = target_sheet.attrib[f"{{{XML_NS['rel']}}}id"]

        workbook_rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        sheet_target = None
        for rel in workbook_rels.findall("pkg:Relationship", XML_NS):
            if rel.attrib.get("Id") == sheet_rel_id:
                sheet_target = _normalize_zip_path("xl/workbook.xml", rel.attrib["Target"])
                break
        if not sheet_target:
            return image_map

        sheet_xml = ET.fromstring(archive.read(sheet_target))
        drawing_node = sheet_xml.find("main:drawing", XML_NS)
        if drawing_node is None:
            return image_map

        drawing_rel_id = drawing_node.attrib.get(f"{{{XML_NS['rel']}}}id")
        if not drawing_rel_id:
            return image_map

        sheet_rels_path = posixpath.join(
            posixpath.dirname(sheet_target),
            "_rels",
            f"{posixpath.basename(sheet_target)}.rels",
        )
        sheet_rels_xml = ET.fromstring(archive.read(sheet_rels_path))

        drawing_target = None
        for rel in sheet_rels_xml.findall("pkg:Relationship", XML_NS):
            if rel.attrib.get("Id") == drawing_rel_id:
                drawing_target = _normalize_zip_path(sheet_target, rel.attrib["Target"])
                break
        if not drawing_target:
            return image_map

        drawing_xml = ET.fromstring(archive.read(drawing_target))
        drawing_rels_path = posixpath.join(
            posixpath.dirname(drawing_target),
            "_rels",
            f"{posixpath.basename(drawing_target)}.rels",
        )
        drawing_rels_xml = ET.fromstring(archive.read(drawing_rels_path))
        embed_to_media: dict[str, str] = {}
        for rel in drawing_rels_xml.findall("pkg:Relationship", XML_NS):
            media_target = _normalize_zip_path(drawing_target, rel.attrib["Target"])
            embed_to_media[rel.attrib["Id"]] = media_target

        anchors = drawing_xml.findall("xdr:oneCellAnchor", XML_NS) + drawing_xml.findall("xdr:twoCellAnchor", XML_NS)
        for anchor in anchors:
            row_node = anchor.find("xdr:from/xdr:row", XML_NS)
            blip_node = anchor.find(".//a:blip", XML_NS)
            if row_node is None or blip_node is None:
                continue

            embed_id = blip_node.attrib.get(f"{{{XML_NS['rel']}}}embed")
            media_path = embed_to_media.get(embed_id or "")
            if not media_path:
                continue

            image_map[int(row_node.text) + 1] = archive.read(media_path)

    return image_map


def _extract_sheet_images(workbook_path: Path, worksheet) -> dict[int, bytes]:
    """优先使用 openpyxl 的图片对象，失败时回退到 xlsx 包解析。"""
    image_map: dict[int, bytes] = {}

    for img in getattr(worksheet, "_images", []):
        excel_row = img.anchor._from.row + 1
        image_map[excel_row] = img._data()

    if image_map:
        logger.info(f"openpyxl 读取到 {len(image_map)} 张嵌入图片")
        return image_map

    logger.warning("openpyxl 未读取到 ws._images，回退到 xlsx 压缩包解析")
    return _extract_images_from_xlsx_package(workbook_path)


def _load_templates_from_excel(excel_path: str) -> list[dict]:
    """从 Excel 提取模板数据（标题、文案、封面图片），图片保存到临时目录。

    Returns:
        list of {'title': str, 'wengan': str, 'image_path': str | None}
    """
    workbook_path = Path(excel_path)
    # 若文件扩展名异常但内容仍是 xlsx，用 BytesIO 绕过 openpyxl 的扩展名校验
    with workbook_path.open("rb") as f:
        wb = openpyxl.load_workbook(BytesIO(f.read()))
    ws = wb.active

    image_map = _extract_sheet_images(workbook_path, ws)

    if not image_map:
        raise ValueError(f"模板文件中未读取到任何嵌入图片: {workbook_path}")

    tmp_dir = tempfile.mkdtemp(prefix="maliang_covers_")
    templates = []

    for excel_row, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        _, wengan, title = row[0], row[1], row[2]
        if not title or not wengan:
            continue

        img_data = image_map.get(excel_row)
        if not img_data:
            raise ValueError(f"第 {excel_row} 行未找到封面图片，标题: {title}")

        image_path = os.path.join(tmp_dir, f"cover_{excel_row}.png")
        with open(image_path, "wb") as f:
            f.write(img_data)

        templates.append({"title": title, "wengan": wengan, "image_path": image_path})

    logger.info(f"从 Excel 加载了 {len(templates)} 条模板数据，封面图片已提取到 {tmp_dir}")
    return templates


@allure.feature("马良模板批量创建")
class TestMaliangBatch:
    @allure.story("批量添加模板")
    @allure.title("从 Excel 批量创建马良模板")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_batch_add_templates(self, page: Page):
        templates = _load_templates_from_excel(EXCEL_PATH)
        assert templates, "Excel 中未读取到有效模板数据"

        maliang_page = MaliangPage(page)

        for i, tmpl in enumerate(templates[:28], start=1):
            with allure.step(f"添加第 {i} 条模板：{tmpl['title']}"):
                logger.info(f"[{i}/{len(templates)}] 添加模板: {tmpl['title']}")
                logger.info(f"[{i}/{len(templates)}] 封面路径: {tmpl['image_path']}")
                maliang_page.open()
                maliang_page.add_template(
                    title=tmpl["title"],
                    wengan=tmpl["wengan"],
                    image_path=tmpl["image_path"],
                )
                logger.info(f"添加模板: {tmpl['title']} 完成")
                # page.wait_for_timeout(10000)
