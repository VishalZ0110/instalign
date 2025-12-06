import os
import time
from playwright.sync_api import sync_playwright

def login(user_name, password, headless=False):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        print(f"Navigating to Instagram login page...")
        page.goto("https://www.instagram.com")
        
        # Wait for form to load
        page.wait_for_selector('input[name="username"]')
        
        # Fill credentials
        print(f"Logging in as {user_name}...")
        page.fill('input[name="username"]', user_name)
        page.fill('input[name="password"]', password)
        
        # Click login
        page.click('button[type="submit"]')
        
        # Wait for navigation or specific element that indicates success
        # Usually checking for a profile icon or specific home element
        # We can wait for the "Not Now" button for notifications or "Save Info"
        try:
            page.wait_for_selector('svg[aria-label="Home"]', timeout=5000)
            print("Login successful.")
        except:
            print("Login might have failed or took too long. Checking for 'Save Info' or 'Not Now'...")
            # Sometimes there are interstitials
            time.sleep(5)

        # Save cookies
        context.storage_state(path="session.json")
        
        print("Session saved to session.json")
        browser.close()

def get_context(playwright, headless=True):
    browser = playwright.chromium.launch(headless=headless)
    if os.path.exists("session.json"):
        context = browser.new_context(storage_state="session.json")
        print("Loaded session from session.json")
    else:
        context = browser.new_context()
        print("No session file found. Starting fresh context.")
    return browser, context
