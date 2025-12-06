from utils import save_list, random_sleep


def get_profile_counts(page, user_name):
    print(f"Navigating to {user_name}'s profile...")
    page.goto(f"https://www.instagram.com/{user_name}/")
    page.wait_for_load_state("domcontentloaded")
    
    followers_selector = f'a[href="/{user_name}/followers/"]'
    following_selector = f'a[href="/{user_name}/following/"]'
    
    page.wait_for_selector(followers_selector)
    
    followers_text = page.locator(followers_selector).inner_text()
    following_text = page.locator(following_selector).inner_text()
    
    # Text is usually like "972 followers" or just "972" inside a span
    # The selector found in references: 
    # <a ...><span ...><span ...>972</span></span> following</a>
    # So inner_text might be "972\nfollowing"
    
    def parse_count(text):
        try:
            # Remove commas and non-numeric chars except maybe 'k' or 'm' if needed, 
            # but usually for exact scraping we want the full number. 
            # Instagram might show "10K", which is hard to scroll to exact count.
            # Assuming exact count is visible or we scrape as much as possible.
            # For now, let's try to extract the first number.
            parts = text.split()
            for part in parts:
                part = part.replace(',', '')
                if part.isdigit():
                    return int(part)
            return 0
        except:
            return 0

    followers_count = parse_count(followers_text)
    following_count = parse_count(following_text)
    
    print(f"Detected: {followers_count} followers, {following_count} following.")
    return followers_count, following_count

from tqdm import tqdm

def scrape_list(page, user_name, list_type, target_count):
    # list_type is 'followers' or 'following'
    print(f"Scraping {list_type}...")
    
    # Click to open modal
    link_selector = f'a[href="/{user_name}/{list_type}/"]'
    page.click(link_selector)
    
    # Wait for modal
    modal_selector = 'div[role="dialog"]'
    page.wait_for_selector(modal_selector)
    
    collected_usernames = set()
    last_len = 0
    retries = 0
    
    # Find scrollable element dynamically to hover over it
    scrollable_handle = page.evaluate_handle(f'''
        () => {{
            const modal = document.querySelector('{modal_selector}');
            if (!modal) return null;
            
            const divs = modal.querySelectorAll('div');
            for (const div of divs) {{
                const style = window.getComputedStyle(div);
                if (style.overflowY === 'auto' || style.overflowY === 'scroll') {{
                    return div;
                }}
            }}
            return null;
        }}
    ''')

    # Ensure we are focused on the modal
    try:
        if scrollable_handle.as_element():
            scrollable_handle.hover()
        else:
            page.hover(modal_selector)
    except:
        pass

    with tqdm(total=target_count, desc=f"Scraping {list_type}", unit="user") as pbar:
        while len(collected_usernames) < target_count:
            # Extract usernames
            links = page.locator(f'{modal_selector} a[role="link"]').all()
            
            for link in links:
                href = link.get_attribute('href')
                if href and href != '/' and href.count('/') == 2:
                    username = href.strip('/').split('/')[-1]
                    if username != user_name:
                        if username not in collected_usernames:
                            collected_usernames.add(username)
                            pbar.update(1)
            
            current_len = len(collected_usernames)
            
            if current_len >= target_count:
                break
                
            if current_len == last_len:
                retries += 1
                if retries > 5:
                    print("\nNo new users found after scrolling. Stopping.")
                    break
            else:
                retries = 0
                last_len = current_len
            
            # Scroll logic using mouse wheel
            try:
                # Hover over the scrollable element to ensure we are scrolling the right area
                if scrollable_handle.as_element():
                    scrollable_handle.hover()
                elif links:
                    links[-1].hover()
                else:
                    page.hover(modal_selector)
                
                # Scroll down
                page.mouse.wheel(0, 3000)
                
            except Exception as e:
                print(f"\nError during scrolling: {e}")
                # Fallback
                page.keyboard.press("PageDown")
            
            random_sleep(1, 2)
            
            random_sleep(1, 2)
            
            random_sleep(1, 2)
    
    # Close modal
    try:
        page.click('button[type="button"] svg[aria-label="Close"]')
    except:
        # Click outside or press escape
        page.keyboard.press("Escape")
    
    random_sleep(1, 2)
    return list(collected_usernames)

def scrape_followers_and_following(page, user_name):
    followers_count, following_count = get_profile_counts(page, user_name)
    
    followers = scrape_list(page, user_name, "followers", followers_count)
    save_list("followers.txt", followers)
    
    # Refresh to be safe
    page.reload()
    page.wait_for_load_state("domcontentloaded")
    
    following = scrape_list(page, user_name, "following", following_count)
    save_list("following.txt", following)
    
    return followers, following
