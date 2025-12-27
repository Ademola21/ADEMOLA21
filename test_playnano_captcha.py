"""
Test PlayNano CAPTCHA solver directly
"""
import time
import cv2
import numpy as np
import base64
import io
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import random

def extract_image_from_background(driver, selector):
    """Extract image from CSS background-image property"""
    element = driver.find_element(By.CSS_SELECTOR, selector)
    bg_image_style = element.value_of_css_property('background-image')
    
    print(f"  Background style for {selector}: {bg_image_style[:100]}...")
    
    if 'data:image' in bg_image_style:
        base64_str = bg_image_style.split('base64,')[1].rstrip(')"')
        image_data = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to BGR
        img_array = np.array(image)
        if len(img_array.shape) == 2:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
        elif img_array.shape[2] == 4:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
        elif img_array.shape[2] == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        print(f"  Extracted image shape: {img_array.shape}")
        return img_array
    else:
        raise Exception(f"No base64 image in background-image")

# Setup
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)

try:
    print("Navigating to CAPTCHA page...")
    driver.get("https://playnano.online/watch-and-learn/nano/captcha")
    time.sleep(2)
    
    print("\nClicking checkbox...")
    checkbox = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".scaptcha-anchor-checkbox"))
    )
    checkbox.click()
    time.sleep(2)
    
    print("\nExtracting background image...")
    try:
        background = extract_image_from_background(driver, ".scaptcha-card-background")
    except Exception as e:
        print(f"ERROR extracting background: {e}")
        print("\nLet me check what elements exist:")
        elements = driver.find_elements(By.CSS_SELECTOR, "[class*='scaptcha']")
        for el in elements:
            print(f"  - {el.get_attribute('class')}")
        driver.quit()
        exit(1)
    
    print("\nExtracting puzzle piece...")
    piece = extract_image_from_background(driver, ".scaptcha-card-slider-puzzle")
    
    print("\nDetecting gap...")
    from sliderSolverFinal import find_gap_with_template_matching
    gap_x, _ = find_gap_with_template_matching(background, piece, verbose=False)
    print(f"Gap found at: {gap_x}px")
    
    print("\nGetting slider elements...")
    puzzle_piece_elem = driver.find_element(By.CSS_SELECTOR, ".scaptcha-card-slider-puzzle")
    piece_left = puzzle_piece_elem.value_of_css_property('left')
    offset = int(piece_left.replace('px', ''))
    print(f"Piece offset: {offset}px")
    
    img_width = background.shape[1]
    slider_track = driver.find_element(By.CSS_SELECTOR, ".scaptcha-card-slider-track")
    track_width = slider_track.size['width']
    slider_handle = driver.find_element(By.CSS_SELECTOR, ".scaptcha-card-slider-control")
    handle_width = slider_handle.size['width']
    piece_width = piece.shape[1]
    
    print(f"Image width: {img_width}px, Piece width: {piece_width}px")
    print(f"Track width: {track_width}px, Handle width: {handle_width}px")
    
    scale_ratio = (track_width - handle_width) / (img_width - piece_width)
    drag_distance = int((gap_x - offset) * scale_ratio)
    
    print(f"Scale ratio: {scale_ratio:.3f}")
    print(f"Drag distance: {drag_distance}px")
    
    print("\nPerforming drag...")
    slider = driver.find_element(By.CSS_SELECTOR, ".scaptcha-card-slider-control")
    action = ActionChains(driver)
    action.click_and_hold(slider).perform()
    time.sleep(0.2)
    
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
    
    print("\nWaiting for verification...")
    time.sleep(5)
    
    print("\nDone! Browser will stay open for 15 seconds...")
    time.sleep(15)
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    time.sleep(15)
finally:
    driver.quit()
