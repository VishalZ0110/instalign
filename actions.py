from utils import log_action, random_sleep

def process_actions(page, user_name, action_type, target_users):
    # action_type: 'unfollow' or 'follow_back'

    list_name = "following" if action_type == "unfollow" else "followers"
    print(f"Starting {action_type} process for {len(target_users)} users...")
    
    # Open the relevant modal
    # For unfollowing, we look in 'following' list
    # For follow back, we look in 'followers' list (to find them and follow back? 
    # Actually, to follow back, we can just go to their profile or search them. 
    # But the plan says: "Open the followers modal. Search username... Click the follow button".
    # This implies we are looking for them in our followers list to follow them back.
    
    link_selector = f'a[href="/{user_name}/{list_name}/"]'
    page.click(link_selector)
    
    modal_selector = 'div[role="dialog"]'
    page.wait_for_selector(modal_selector)
    
    search_input = 'input[placeholder="Search"]'
    page.wait_for_selector(search_input)
    
    processed_count = 0
    
    for target_user in target_users:
        print(f"Processing {target_user}...")
        
        # Search for user
        page.fill(search_input, target_user)
        random_sleep(1, 2)
        
        # Wait for results
        # The result should show the user. We need to find the specific row for this user.
        # The row usually contains the username text.
        
        # We can look for a link with the username
        user_link_selector = f'{modal_selector} a[href="/{target_user}/"]'
        
        try:
            page.wait_for_selector(user_link_selector, timeout=5000)
        except:
            print(f"User {target_user} not found in search results.")
            log_action(f"{action_type}_failed.txt", target_user)
            # Clear search
            page.fill(search_input, "")
            continue
            
        # Find the button next to the user
        # We need to traverse up from the link to the row container, then find the button.
        # Or we can use Playwright's layout selectors.
        
        # Assuming the button is in the same row.
        # We can find the button inside the row that contains the user link.
        # <div ... has user link ...> <button> ... </button> </div>
        
        # Let's try to locate the button relative to the user link
        # The structure is roughly: Row -> [User Info (Link), Button]
        
        if action_type == "unfollow":
            # Click "Following" button
            try:
                
                button = page.locator(f'{modal_selector} button').filter(has_text="Following").first
                button.click()
                
                # Confirm unfollow
                # Wait for confirmation modal
                page.wait_for_selector('button:has-text("Unfollow")')
                page.click('button:has-text("Unfollow")')
                
                log_action("unfollowed.txt", target_user)
                print(f"Unfollowed {target_user}")
                
            except Exception as e:
                print(f"Failed to unfollow {target_user}: {e}")
                log_action("unfollow_failed.txt", target_user)

        elif action_type == "follow_back":
            # Click "Follow" button
            try:
                button = page.locator(f'{modal_selector} button').filter(has_text="Follow").first
                # Ensure it's not "Following" or "Requested"
                # "Follow" usually means we are not following.
                
                button.click()
                
                log_action("followed.txt", target_user)
                print(f"Followed {target_user}")
                
            except Exception as e:
                print(f"Failed to follow {target_user}: {e}")
                log_action("follow_failed.txt", target_user)
        
        # Clear search
        page.fill(search_input, "")
        random_sleep(2, 4)
        
        processed_count += 1
        # Optional: break if limit reached (handled in main)
    
    # Close modal
    try:
        page.click('button[type="button"] svg[aria-label="Close"]')
    except:
        page.keyboard.press("Escape")
