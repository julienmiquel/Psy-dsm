from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost:8501")

        # Check for the main title
        expect(page.get_by_text("DSM-5 Character Profile Generator")).to_be_visible()

        # Check for the text area
        expect(page.get_by_label("Character Description")).to_be_visible()

        # Check for the "Generate Profile" button
        expect(page.get_by_role("button", name="Generate Profile")).to_be_visible()

        # Check for the "Toggle Chat Mode" checkbox
        expect(page.get_by_label("Toggle Chat Mode")).to_be_visible()

        page.screenshot(path="jules-scratch/verification/verification.png")
        browser.close()

if __name__ == "__main__":
    run()
