import undetected_chromedriver as uc
import random
import time
import os

USER_AGENTS = [
    # Pixel 7 (Android 13, Chrome)
    # "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    # # iPhone 14 Pro (iOS 16, Safari)
    # "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    # # Samsung Galaxy S22 (Android 12, Chrome)
    # "Mozilla/5.0 (Linux; Android 12; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

PROXIES = [
    # Example: 'http://username:password@proxy_ip:proxy_port',
    # Add your proxies here if needed
]

def get_random_proxy():
    if PROXIES:
        return random.choice(PROXIES)
    return None

def setup_mobile_driver():
    options = uc.ChromeOptions()
    user_agent = random.choice(USER_AGENTS)
    options.add_argument(f"--user-agent={user_agent}")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless=new")  # Use headless mode

    # Start with desktop window size
    options.add_argument("--window-size=720,900")

    # Add proxy if available
    proxy = get_random_proxy()
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')

    driver = uc.Chrome(options=options)

    # Wait for driver to stabilize
    random_delay()

    # Open any page (example: Amazon)
    driver.get("https://www.amazon.in")
    random_delay()

    # Now switch to mobile size (simulate phone)
    width = random.choice([720])
    height = random.choice([740, 780, 800, 844, 915, 932])
    driver.set_window_size(width, height)

    # Wait a bit before scroll
    random_delay()

    # Scroll one full viewport (simulate user action)
    driver.execute_script("window.scrollBy(0, window.innerHeight);")
    random_delay()

      # Scroll fully to the right (X-axis)
    # driver.execute_script("window.scrollTo(document.body.scrollWidth, 0);")
    driver.execute_script("window.scrollTo(500, 0);")
    random_delay()

    # Save screenshot
    screenshot_path = os.path.abspath("screenshot.png")
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot saved to: {screenshot_path}")

    return driver  # keep driver running if further actions are needed

def random_delay(min_sec=1.2, max_sec=2.7):
    time.sleep(random.uniform(min_sec, max_sec))


# Example run
if __name__ == "__main__":
    driver = setup_mobile_driver()
    # Keep driver open if needed for further actions
    time.sleep(2)
    driver.quit()
