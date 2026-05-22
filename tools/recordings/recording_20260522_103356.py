import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(storage_state="/var/folders/0w/m2th_ccs4gg2ny_99qtvmq1h0000gn/T/tmptuhicqrz.json")
    page = context.new_page()
    page.goto("https://aixmy.miaobi.cn/#/home/profile")
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
