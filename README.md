# Instalign

A lightweight Instagram companion that scans your followers and following lists, highlights mismatches, and lets you quickly follow back or unfollow selected accounts.

## Requirements

- Python 3.7+
- [Playwright](https://playwright.dev/python/) for browser automation.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd instalign
   ```

2. **Set up a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install pytest-playwright
   playwright install
   ```

## Usage

Run the script using Python. On the first run, you will be prompted to log in. Your session will be saved to `session.json` for future use so you don't have to log in every time.

### 1. Standard Run (Scan & Actions)
Scans your profile, identifies users who don't follow you back and users you don't follow back, and then prompts you for actions.
```bash
python main.py
```
Run with `--delete-session` to delete the session.json file after running.
*Note: If `session.json` does not exist, you will be asked for your Instagram username and password.*

### 2. Scan Only
Only scans your profile and saves the lists to the `information/` directory without prompting for any follow/unfollow actions.
```bash
python main.py --scan-only
```

### 3. Use Existing Lists
Skip the scraping/scanning phase and use the lists already saved in the `information/` folder (e.g., from a previous run). Useful if you want to perform actions without rescanning.
```bash
python main.py --use-lists
```

### 4. No Headless Login
Run the script in a visible browser window (useful in case of 2FA).
```bash
python main.py --no-headless-login
```

### Automatic vs Manual Actions
When performing actions (Unfollow or Follow Back), you will be presented with three options:
1. **Automatic**: The bot performs the action for all users in the list automatically.
2. **Manual** (Recommended): Opens a browser window for each user one by one, allowing you to verify and perform the action yourself.
3. **Skip**: Skips the current action.

## Caveats & Safety

- **Rate Limits**: Instagram has strict rate limits. If you follow/unfollow too many people too quickly, your account may be temporarily blocked from performing these actions.
  - The script includes random delays to mimic human behavior, but use the **Automatic** mode with caution, especially for large lists.
- **Session Security**: Your session cookies are stored in `session.json`. Keep this file secure and **do not share it**. It acts as your credentials.
- **"Action Blocked"**: If you see "Action Blocked" errors or if the script fails to find buttons, pause usage for a few hours or days.
- **Two-Factor Authentication**: The current login implementation handles basic password login. If you have 2FA enabled, login manually during the initial headed login phase or disable 2FA temporarily (not recommended).
