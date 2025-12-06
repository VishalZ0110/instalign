import argparse
import os
import getpass
from playwright.sync_api import sync_playwright
from auth import login
from scraper import scrape_followers_and_following
from actions import process_actions
from utils import save_list, read_list


def run():
    parser = argparse.ArgumentParser(description="Instagram Follower Manager")
    parser.add_argument("--scan-only", action="store_true", help="Only scan and compute differences, no actions")
    parser.add_argument("--use-lists", action="store_true", help="Use existing lists from information/ folder instead of scraping")
    parser.add_argument("--delete-session", action="store_true", help="Delete session.json after running")
    parser.add_argument("--no-headless-login", action="store_true", help="Run login in headless mode (useful in case of 2FA)")
    args = parser.parse_args()

    if args.scan_only and args.use_lists:
        print("Error: --scan-only and --use-lists cannot be used together.")
        return

    print("--- Instagram Follower Manager ---")

    # Login (Always Headless)
    user_name = None
    if not os.path.exists("session.json"):
        print("No session found. Please log in.")
        user_name = input("Username: ")
        password = getpass.getpass("Password: ")
        login(user_name, password, headless=not args.no_headless_login)
        # Login saves session.json, so we can proceed.
    
    not_following_back = set()
    you_dont_follow_back = set()
    
    # Scrape Phase (Always Headless)
    if not args.use_lists:
        with sync_playwright() as p:
            # Launch browser with session
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(storage_state="session.json")
            page = context.new_page()
            
            # If username was not provided during login (because session existed), ask for it now
            if not user_name:
                user_name = input("Enter the username to manage (your username): ")
            
            # Scrape
            followers, following = scrape_followers_and_following(page, user_name)
            
            # Compute differences
            followers_set = set(followers)
            following_set = set(following)
            
            not_following_back = following_set - followers_set
            you_dont_follow_back = followers_set - following_set
            
            print(f"\nAnalysis Results:")
            print(f"Followers: {len(followers_set)}")
            print(f"Following: {len(following_set)}")
            print(f"Not following you back: {len(not_following_back)}")
            print(f"You don't follow back: {len(you_dont_follow_back)}")
            
            save_list("not_following_back.txt", list(not_following_back))
            save_list("you_dont_follow_back.txt", list(you_dont_follow_back))
            
            browser.close()
            
    else:
        # Load lists mode
        if not user_name:
             user_name = input("Enter the username to manage (your username): ")

        print("Loading lists from file...")
        not_following_back = read_list("not_following_back.txt")
        you_dont_follow_back = read_list("you_dont_follow_back.txt")
        print(f"Loaded {len(not_following_back)} users who don't follow back.")
        print(f"Loaded {len(you_dont_follow_back)} users you don't follow back.")

    if args.scan_only:
        print("Scan only mode. Exiting.")
        # We don't delete session here to allow re-use
        return

    # Actions Phase
    print("\n--- Actions ---")
    print("⚠️ WARNING: You would be unfollowing or following a lot of users.")
    print("Proceed with caution.")
    
    if not_following_back:
        choice = input(f"""
        You have {len(not_following_back)} users who don't follow you back.
        What action do you want to perform?
        1. Unfollow all users : All the users will be unfollowed in one go.
        2. Unfollow users one at a time. A browser window opens for each account so you can unfollow manually. Close the window if you choose not to proceed.
        3. Skip unfollow process.
        Select your option: """)
        
        if choice.lower() == '1':
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                context = browser.new_context(storage_state="session.json")
                page = context.new_page()
                page.goto(f"https://www.instagram.com/{user_name}/")
                page.wait_for_load_state("domcontentloaded")

                process_actions(page, user_name, "unfollow", not_following_back)
                browser.close()
                
        elif choice.lower() == '2':
            # Manual action loop
            print("Starting manual unfollow process...")
            for user in not_following_back:
                print(f"Opening profile for {user}...")
                with sync_playwright() as p:
                    # Visible browser
                    browser = p.chromium.launch(headless=False)
                    try:
                        context = browser.new_context(storage_state="session.json")
                    except Exception as e:
                         # Fallback if session is invalid or missing
                         print(f"Error loading session: {e}. Starting fresh.")
                         context = browser.new_context()
                    
                    page = context.new_page()
                    page.goto(f"https://www.instagram.com/{user}/")
                    
                    print(f"Please process {user} manually.")
                    print("Close the browser window to proceed to the next user.")
                    
                    try:
                         # Wait for the page or context to be closed by the user
                         page.wait_for_event("close", timeout=0)
                    except Exception:
                         pass
                    
                    print(f"Finished with {user}.")
                    # Browser closes automatically due to context manager, but explicit verification helps
                    if browser.is_connected():
                         browser.close()
        elif choice.lower() == '3':
                print("Skipping unfollow process.")

    if you_dont_follow_back:
        choice = input(f"""
        You have {len(you_dont_follow_back)} users who you don't follow back.
        What action do you want to perform?
        1. Follow back all users : All the users will be followed back in one go.
        2. Follow back users one at a time. A browser window opens for each account so you can follow manually. Close the window if you choose not to proceed.
        3. Skip follow back process.
        Select your option: """)
        
        if choice.lower() == '1':
             with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                context = browser.new_context(storage_state="session.json")
                page = context.new_page()
                page.goto(f"https://www.instagram.com/{user_name}/")
                page.wait_for_load_state("domcontentloaded")

                process_actions(page, user_name, "follow_back", you_dont_follow_back)
                browser.close()

        elif choice.lower() == '2':
            # Manual action loop
            print("Starting manual follow back process...")
            for user in you_dont_follow_back:
                print(f"Opening profile for {user}...")
                with sync_playwright() as p:
                    # Visible browser
                    browser = p.chromium.launch(headless=True)
                    try:
                        context = browser.new_context(storage_state="session.json")
                    except Exception as e:
                         # Fallback if session is invalid or missing
                         print(f"Error loading session: {e}. Starting fresh.")
                         context = browser.new_context()
                    
                    page = context.new_page()
                    page.goto(f"https://www.instagram.com/{user}/")
                    
                    print(f"Please follow {user} manually.")
                    print("Close the browser window to proceed to the next user.")
                    
                    try:
                         # Wait for the page or context to be closed by the user
                         page.wait_for_event("close", timeout=0)
                    except Exception:
                         pass
                    
                    print(f"Finished with {user}.")
                    # Browser closes automatically due to context manager, but explicit verification helps
                    if browser.is_connected():
                         browser.close()
        elif choice.lower() == '3':
            print("Skipping follow back process.")
    
    print("Done.")
    
    # Delete session
    if args.delete_session:
        if os.path.exists("session.json"):
            os.remove("session.json")


if __name__ == "__main__":
    run()
