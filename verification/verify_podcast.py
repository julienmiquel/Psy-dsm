import os
import time
from playwright.sync_api import sync_playwright

def verify_podcast_generation():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to the app
        page.goto("http://localhost:8501")

        # Wait for title
        page.wait_for_selector("h1")

        # Take screenshot of initial state
        page.screenshot(path="verification/initial_state.png")

        # Note: I cannot actually generate a podcast because it requires API calls which are mocked in tests
        # but in the real running app they would fail without a valid key or mock.
        # However, I can verify the UI structure is present.

        # Since the button only appears after TCC program is generated,
        # and TCC program is generated after profile,
        # and profile generation requires API...

        # I can't easily verify the podcast button without mocking the backend services in the running app.

        # But I can verify the main page loads.

        browser.close()

if __name__ == "__main__":
    verify_podcast_generation()
