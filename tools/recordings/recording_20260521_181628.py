import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(storage_state="/var/folders/0w/m2th_ccs4gg2ny_99qtvmq1h0000gn/T/tmpxh_d0w6b.json")
    page = context.new_page()
    page.goto("https://aixmy.miaobi.cn/#/home/profile")
    page.get_by_role("button", name="开始上课").click()
    page.locator(".work-thumbnail").click()
    page.get_by_role("button", name="启动课件，开始上课").click()
    page.get_by_role("button", name="自动生成房间号").click()
    page.get_by_role("button", name="立即进入").click()
    page.locator("iframe").content_frame.locator("div").filter(has_text=re.compile(r"^文生图$")).first.click()
    page.locator("iframe").content_frame.locator("#tinymce-editor-1779358609514").fill("/文生图﻿老虎")
    page.locator("iframe").content_frame.locator(".message-input-button-send-btn").click()
    page.locator("iframe").content_frame.locator("img").nth(4).click()
    page.locator("iframe").content_frame.get_by_text("图生图").click()
    page.locator("iframe").content_frame.locator("#tinymce-editor-1779358609514").fill("/图生图﻿黑色的老虎")
    page.locator("iframe").content_frame.locator(".message-input-button-send-btn").click()
    page.locator("div").filter(has_text=re.compile(r"^下课$")).nth(1).click()
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
