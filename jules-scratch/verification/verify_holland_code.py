
from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("http://localhost:32123")

    page.get_by_label("Character Description").fill("A character who is artistic and enjoys helping people.")
    page.get_by_role("button", name="Generate Profile").click()
    page.wait_for_selector("text=Holland Code (RIASEC) Assessment")

    page.screenshot(path="jules-scratch/verification/verification.png")
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
