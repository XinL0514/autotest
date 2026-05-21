import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(storage_state="/Users/hantongxue/Desktop/work/autotest/test_data/auth_state.json")
    page = context.new_page()
    page.goto("https://aixmy.miaobi.cn/#/home/profile")
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
