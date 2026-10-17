from playwright.sync_api import sync_playwright
from src.config.settings import BOT_NAME

def run():
    print(f"Starting {BOT_NAME}...")
    with sync_playwright() as p:
        # Launch browser in headed mode as specified
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://example.com")
        print("Page title:", page.title())
        browser.close()

if __name__ == "__main__":
    run()
