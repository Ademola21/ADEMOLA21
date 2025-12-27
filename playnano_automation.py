"""
PlayNano Automated CAPTCHA Solver
Integrates Slider CAPTCHA and reCAPTCHA v2 solvers
"""
import time
import cv2
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import our CAPTCHA solvers
from sliderSolverFinal import solve_slider_captcha, extract_image
from recaptchaSolver import solve_recaptcha

# Configuration
CONFIG = {
    "url": "https://playnano.online/watch-and-learn/nano",
    "test_wallet": "nano_3test1234567890abcdefghijklmnopqrstuvwxyz123456",  # Change this
    "max_countdown_wait": 180,  # 3 minutes max per countdown
    "block_videos": True,
    "headless": False,
    "verbose": True
}

def block_videos(driver):
    """Block video elements to save bandwidth"""
    try:
        script = """
        // Hide and disable all video and iframe elements
        document.querySelectorAll('video, iframe[src*="youtube"], iframe[src*="vimeo"]').forEach(el => {
            el.style.display = 'none';
            el.style.visibility = 'hidden';
            el.src = '';
            el.remove();
        });
        
        // Block video auto-loading
        document.querySelectorAll('source').forEach(el => {
            el.src = '';
            el.remove();
        });
        
        console.log('Videos blocked successfully');
        """
        driver.execute_script(script)
        if CONFIG["verbose"]:
            print("  [+] Videos blocked")
    except Exception as e:
        print(f"  [!] Warning: Could not block videos: {e}")

def wait_for_countdown_and_click(driver, page_num, max_wait=180):
    """Wait for countdown to finish and click Next Video button"""
    if CONFIG["verbose"]:
        print(f"\n[Page {page_num}/5] Waiting for countdown...")
    
    try:
        # Find the Next Video button (button.watch-next-btn)
        button = driver.find_element(By.CSS_SELECTOR, "button.watch-next-btn")
        
        # Wait for button to become enabled (disabled attribute removed)
        start_time = time.time()
        while time.time() - start_time < max_wait:
            if not button.get_attribute("disabled"):
                # Button is enabled!
                if CONFIG["verbose"]:
                    print(f"  [+] Countdown finished, clicking button...")
                break
            time.sleep(1)  # Check every second
        else:
            # Timeout
            raise TimeoutException(f"Button still disabled after {max_wait}s")
        
        # Scroll into view and click
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        time.sleep(0.5)
        button.click()
        time.sleep(2)
        
        # Block videos on new page
        if CONFIG["block_videos"]:
            block_videos(driver)
        
        return True
        
    except NoSuchElementException:
        print(f"  [X] Could not find Next Video button on page {page_num}")
        return False
    except TimeoutException as e:
        print(f"  [X] Timeout: {e}")
        return False
    except Exception as e:
        print(f"  [X] Error on page {page_num}: {e}")
        return False

def detect_captcha_type(driver):
    """Detect which type of CAPTCHA is present"""
    if CONFIG["verbose"]:
        print("\n[CAPTCHA Detection] Checking type...")
    
    time.sleep(2)  # Give page time to load
    
    try:
        # Check for Slider CAPTCHA (scaptcha uses anchor checkbox)
        if driver.find_elements(By.CSS_SELECTOR, ".scaptcha-anchor-checkbox") or \
           driver.find_elements(By.CSS_SELECTOR, ".scaptcha-card-checkbox") or \
           driver.find_elements(By.CSS_SELECTOR, ".scaptcha-container"):
            if CONFIG["verbose"]:
                print("  [+] Detected: Slider CAPTCHA")
            return "slider"
        
        # Check for reCAPTCHA v2
        if driver.find_elements(By.CSS_SELECTOR, ".g-recaptcha") or \
           driver.find_elements(By.CSS_SELECTOR, "iframe[src*='recaptcha']"):
            if CONFIG["verbose"]:
                print("  [+] Detected: reCAPTCHA v2")
            return "recaptcha_v2"
        
        print("  [!] Unknown CAPTCHA type")
        return "unknown"
        
    except Exception as e:
        print(f"  [X] Error detecting CAPTCHA: {e}")
        return "unknown"

def solve_captcha(driver, captcha_type):
    """Solve the detected CAPTCHA"""
    if CONFIG["verbose"]:
        print(f"\n[CAPTCHA Solver] Solving {captcha_type}...")
    
    try:
        if captcha_type == "slider":
            # Use our slider solver
            result = solve_slider_captcha_on_current_page(driver)
            return result
            
        elif captcha_type == "recaptcha_v2":
            # Use reCAPTCHA v2 solver
            result = solve_recaptcha(driver, verbose=CONFIG["verbose"])
            return result
            
        else:
            print("  [X] Cannot solve unknown CAPTCHA type")
            return {"success": False, "error": "Unknown CAPTCHA type"}
            
    except Exception as e:
        print(f"  [X] Error solving CAPTCHA: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

def extract_image_from_background(driver, selector):
    """Extract image from CSS background-image property (for PlayNano CAPTCHA)"""
    import base64
    import io
    from PIL import Image
    import numpy as np
    
    element = driver.find_element(By.CSS_SELECTOR, selector)
    bg_image_style = element.value_of_css_property('background-image')
    
    # Extract base64 data from url("data:image/png;base64,...")
    if 'data:image' in bg_image_style:
        # Remove url(" and ")
        base64_str = bg_image_style.split('base64,')[1].rstrip(')"')
        
        # Decode base64 to image
        image_data = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to BGR (OpenCV format)
        img_array = np.array(image)
        if len(img_array.shape) == 2:  # Grayscale
            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
        elif img_array.shape[2] == 4:  # RGBA
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
        elif img_array.shape[2] == 3:  # RGB
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        return img_array
    else:
        raise Exception(f"No base64 image found in background-image style")

def solve_slider_captcha_on_current_page(driver):
    """Solve slider CAPTCHA on the current page"""
    try:
        # Click checkbox to trigger CAPTCHA
        print("[Slider] Clicking checkbox...")
        wait = WebDriverWait(driver, 10)
        
        # Try both possible selectors
        checkbox = None
        try:
            checkbox = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".scaptcha-anchor-checkbox")
            ))
        except:
            checkbox = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".scaptcha-card-checkbox")
            ))
        
        checkbox.click()
        time.sleep(1)
        
        # Extract images (from CSS background-image for PlayNano)
        print("[Slider] Extracting images...")
        background = extract_image_from_background(driver, ".scaptcha-card-background")
        piece = extract_image_from_background(driver, ".scaptcha-card-slider-puzzle")
        
        # Detect gap using template matching
        from sliderSolverFinal import find_gap_with_template_matching
        gap_x, _ = find_gap_with_template_matching(background, piece, verbose=False)
        print(f"[Slider] Gap detected at: {gap_x}px")
        
        # Get CSS offset and calculate drag
        puzzle_piece_elem = driver.find_element(By.CSS_SELECTOR, ".scaptcha-card-slider-puzzle")
        piece_left = puzzle_piece_elem.value_of_css_property('left')
        offset = int(piece_left.replace('px', ''))
        
        # Calculate scale ratio
        img_width = background.shape[1]
        slider_track = driver.find_element(By.CSS_SELECTOR, ".scaptcha-card-slider-track")
        track_width = slider_track.size['width']
        slider_handle = driver.find_element(By.CSS_SELECTOR, ".scaptcha-card-slider-control")
        handle_width = slider_handle.size['width']
        piece_width = piece.shape[1]
        
        scale_ratio = (track_width - handle_width) / (img_width - piece_width)
        drag_distance = int((gap_x - offset) * scale_ratio)
        
        print(f"[Slider] Dragging {drag_distance}px...")
        
        # Perform drag
        from selenium.webdriver.common.action_chains import ActionChains
        import random
        
        slider = driver.find_element(By.CSS_SELECTOR, ".scaptcha-card-slider-control")
        action = ActionChains(driver)
        action.click_and_hold(slider).perform()
        time.sleep(0.2)
        
        # Smooth drag
        steps = 30
        duration = 0.8
        current_x = 0.0
        
        for i in range(steps):
            t = (i + 1) / steps
            ease_t = 1 - (1 - t) * (1 - t)
            target_x = drag_distance * ease_t
            delta_x = round(target_x - current_x)
            
            if delta_x != 0:
                action.move_by_offset(delta_x, random.randint(-1, 1)).perform()
                current_x += delta_x
            time.sleep(duration / steps)
        
        remaining = drag_distance - int(current_x)
        if remaining != 0:
            action.move_by_offset(remaining, 0).perform()
        
        action.release().perform()
        
        # Check success
        time.sleep(3)
        solved = False
        for _ in range(20):
            try:
                puzzle_card = driver.find_element(By.CSS_SELECTOR, ".scaptcha-card-container")
                if not puzzle_card.is_displayed():
                    solved = True
                    break
            except:
                solved = True
                break
            time.sleep(0.5)
        
        if solved:
            print("[Slider] [+] SUCCESS!")
        else:
            print("[Slider] [X] FAILED")
        
        return {"success": solved}
        
    except Exception as e:
        print(f"[Slider] [X] Error: {e}")
        return {"success": False, "error": str(e)}

def submit_wallet(driver, wallet_address):
    """Submit wallet address after successful CAPTCHA"""
    if CONFIG["verbose"]:
        print(f"\n[Wallet Submission] Entering address...")
    
    try:
        # Find wallet input field
        selectors = [
            "input[name='wallet']",
            "input[type='text']",
            "#wallet",
            "input[placeholder*='address']",
            "input[placeholder*='wallet']"
        ]
        
        wallet_input = None
        for selector in selectors:
            try:
                wallet_input = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except:
                continue
        
        if wallet_input is None:
            raise NoSuchElementException("Could not find wallet input field")
        
        # Clear and enter wallet address
        wallet_input.clear()
        wallet_input.send_keys(wallet_address)
        
        if CONFIG["verbose"]:
            print(f"  [+] Entered wallet: {wallet_address[:20]}...")
        
        # Find and click submit button
        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "//button[contains(text(), 'Submit')]",
            "//button[contains(text(), 'Claim')]"
        ]
        
        submit_button = None
        for selector in submit_selectors:
            try:
                if selector.startswith("//"):
                    submit_button = driver.find_element(By.XPATH, selector)
                else:
                    submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except:
                continue
        
        if submit_button:
            submit_button.click()
            if CONFIG["verbose"]:
                print("  [+] Submitted!")
            return True
        else:
            print("  [!] Could not find submit button")
            return False
            
    except Exception as e:
        print(f"  [X] Error submitting wallet: {e}")
        return False

def run_automation():
    """Main automation workflow"""
    print("=" * 70)
    print("PLAYNANO AUTOMATED CAPTCHA SOLVER")
    print("=" * 70)
    print(f"URL: {CONFIG['url']}")
    print(f"Wallet: {CONFIG['test_wallet'][:20]}...")
    print(f"Video Blocking: {'Enabled' if CONFIG['block_videos'] else 'Disabled'}")
    print("=" * 70)
    
    start_time = time.time()
    
    # Setup Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    if CONFIG["headless"]:
        options.add_argument('--headless')
    
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    
    try:
        # Step 1: Navigate to page
        print("\n[1] Loading PlayNano page...")
        driver.get(CONFIG["url"])
        time.sleep(3)
        
        # Step 2: Click Start Learning (scroll into view first)
        print("\n[2] Clicking 'Start Learning' button...")
        start_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.watch-next-btn"))
        )
        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", start_button)
        time.sleep(1)
        # Wait for it to be clickable
        start_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.watch-next-btn"))
        )
        start_button.click()
        time.sleep(2)
        
        # Block videos on first page
        if CONFIG["block_videos"]:
            block_videos(driver)
        
        # Step 3: Navigate through 5 video pages
        print("\n[3] Navigating through video pages...")
        for page_num in range(1, 6):
            success = wait_for_countdown_and_click(driver, page_num, CONFIG["max_countdown_wait"])
            if not success:
                print(f"\n[X] Failed on page {page_num}/5")
                return
        
        print("\n[+] Completed all 5 video pages!")
        
        # Step 4: Detect CAPTCHA
        captcha_type = detect_captcha_type(driver)
        
        if captcha_type == "unknown":
            print("\n[X] Could not detect CAPTCHA type - aborting")
            return
        
        # Step 5: Solve CAPTCHA
        result = solve_captcha(driver, captcha_type)
        
        # Step 6: Submit wallet only if successful
        if result.get("success"):
            print("\n[+] CAPTCHA SOLVED SUCCESSFULLY!")
            submit_wallet(driver, CONFIG["test_wallet"])
        else:
            print("\n[X] CAPTCHA FAILED - Skipping wallet submission")
        
        # Results
        elapsed = time.time() - start_time
        print("\n" + "=" * 70)
        print("FINAL RESULTS")
        print("=" * 70)
        print(f"CAPTCHA Type: {captcha_type}")
        print(f"CAPTCHA Status: {'[+] SOLVED' if result.get('success') else '[X] FAILED'}")
        print(f"Total Time: {elapsed:.2f}s")
        print("=" * 70)
        
        # Keep browser open for 10 seconds
        print("\nBrowser will close in 10 seconds...")
        time.sleep(10)
        
    except Exception as e:
        print(f"\n[X] ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        driver.quit()

if __name__ == "__main__":
    run_automation()
