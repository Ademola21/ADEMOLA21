"""
Slider CAPTCHA Solver - Template Matching Approach
Uses the puzzle PIECE to find where it fits (most reliable method)
"""
import time
import base64
import cv2
import numpy as np
import re
import os
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random


def extract_image(driver, selector):
    """Extract image from background-image CSS"""
    element = driver.find_element(By.CSS_SELECTOR, selector)
    bg_image = element.value_of_css_property('background-image')
    match = re.search(r'data:image/png;base64,([^"\\)]+)', bg_image)
    if not match:
        raise Exception("No Base64 data found")
    img_data = base64.b64decode(match.group(1))
    img = Image.open(BytesIO(img_data))
    return np.array(img)


def find_gap_with_template_matching(background, piece, verbose=False):
    """
    Find gap position using template matching with Alpha Masking
    Handles transparent puzzle pieces correctly
    """
    # Ensure images are in correct format (OpenCV uses BGR)
    # PIL returns RGB/RGBA, so we convert if needed
    if background.shape[2] == 3:  # RGB
        bg_gray = cv2.cvtColor(background, cv2.COLOR_RGB2GRAY)
        bg_bgr = cv2.cvtColor(background, cv2.COLOR_RGB2BGR)
    elif background.shape[2] == 4: # RGBA
        bg_gray = cv2.cvtColor(background, cv2.COLOR_RGBA2GRAY)
        bg_bgr = cv2.cvtColor(background, cv2.COLOR_RGBA2BGR)
    
    # Handle Piece with Transparency
    if piece.shape[2] == 4:
        # Extract Alpha channel as mask
        piece_gray = cv2.cvtColor(piece, cv2.COLOR_RGBA2GRAY)
        piece_bgr = cv2.cvtColor(piece, cv2.COLOR_RGBA2BGR)
        mask = piece[:, :, 3]  # Alpha channel
    else:
        piece_gray = cv2.cvtColor(piece, cv2.COLOR_RGB2GRAY)
        piece_bgr = cv2.cvtColor(piece, cv2.COLOR_RGB2BGR)
        mask = None
    
    piece_h, piece_w = piece_gray.shape
    
    # Attempt 1: Edge-based matching (Canny)
    bg_edges = cv2.Canny(bg_gray, 50, 150)
    piece_edges = cv2.Canny(piece_gray, 50, 150)
    
    # Match edges
    res_edge = cv2.matchTemplate(bg_edges, piece_edges, cv2.TM_CCORR_NORMED)
    
    # Ignore the left edge to avoid matching the starting piece position
    res_edge[:, :50] = 0
    
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res_edge)
    gap_x = max_loc[0]
    
    if verbose:
        print(f"  Hole detected at: {gap_x}px")

    # Create debug visualization
    debug_img = cv2.cvtColor(bg_gray, cv2.COLOR_GRAY2BGR)
                  
    # Draw Gap (Green)
    cv2.rectangle(debug_img, (gap_x, max_loc[1]), 
                  (gap_x + piece_w, max_loc[1] + piece_h), 
                  (0, 255, 0), 2)

    cv2.putText(debug_img, f"Hole: {gap_x}px", (gap_x, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    return gap_x, debug_img


def solve_slider_captcha(url, verbose=True):
    """Solve slider CAPTCHA using template matching"""
    start_time = time.time()
    
    print("=" * 70)
    print("SLIDER CAPTCHA SOLVER - TEMPLATE MATCHING")
    print("v2.5 - Adaptive Fallback Enabled")
    print("=" * 70)
    print(f"URL: {url}\n")
    
    debug_dir = "debug_slider_working"
    os.makedirs(debug_dir, exist_ok=True)
    
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    
    try:
        # Load page
        print("[1] Loading page...")
        driver.get(url)
        time.sleep(2)
        
        # Click checkbox
        print("[2] Clicking checkbox...")
        wait = WebDriverWait(driver, 10)
        checkbox = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".scaptcha-anchor-checkbox")
        ))
        checkbox.click()
        time.sleep(3)
        
        # Extract puzzle image to get IMAGE width
        print("[3] Extracting images...")
        background = extract_image(driver, ".scaptcha-card-background")
        piece = extract_image(driver, ".scaptcha-card-slider-puzzle")
        img_width = background.shape[1] # Actual image width in pixels
        print(f"  Image Width: {img_width}px")
        
        # Get Slider Track Width from DOM
        try:
            slider_track = driver.find_element(By.CSS_SELECTOR, ".scaptcha-card-slider-track")
            track_width = slider_track.size['width']
            
            slider_handle = driver.find_element(By.CSS_SELECTOR, ".scaptcha-card-slider-control")
            handle_width = slider_handle.size['width']
            piece_width = piece.shape[1]
            
            print(f"  Slider Track Width: {track_width}px")
            print(f"  Handle Width: {handle_width}px, Piece Width: {piece_width}px")
            
            # Correct ratio: slider usable range / image usable range
            scale_ratio = (track_width - handle_width) / (img_width - piece_width)
            print(f"  Scale Ratio: ({track_width}-{handle_width})/({img_width}-{piece_width}) = {scale_ratio:.3f}")
        except Exception as e:
            print(f"  Could not detect slider width: {e}")
            # Adaptive Fallback
            if img_width < 280:
                print(f"  Small image detected ({img_width}px). Assuming 1.0 scaling.")
                scale_ratio = 1.0
            else:
                print(f"  Large image detected ({img_width}px). Using standard ratio 0.81.")
                scale_ratio = 0.81
        
        print(f"  Calculated Scale Ratio: {scale_ratio:.3f}")

        # Find where piece fits using template matching
        print("[4] Detecting gap...")
        gap_x, debug_img = find_gap_with_template_matching(background, piece, verbose=verbose)
        
        cv2.imwrite(f"{debug_dir}/match_result.png", debug_img)
        print(f"  Gap detected at: {gap_x}px")
        
        # Get the puzzle piece's initial position from CSS
        try:
            puzzle_piece_elem = driver.find_element(By.CSS_SELECTOR, ".scaptcha-card-slider-puzzle")
            piece_left_style = puzzle_piece_elem.value_of_css_property('left')
            # Parse the 'left' value (e.g., "5px" -> 5)
            piece_initial_x = int(piece_left_style.replace('px', ''))
            print(f"  Piece initial position: {piece_initial_x}px")
            
            # Adjust drag distance to account for piece initial position
            drag_distance_adjusted = gap_x - piece_initial_x
            print(f"  Adjusted drag distance: {drag_distance_adjusted}px (gap {gap_x}px - initial {piece_initial_x}px)")
        except Exception as e:
            print(f"  Could not get piece initial position: {e}")
            drag_distance_adjusted = gap_x
        
        # Apply Scaling - use precise ratio
        drag_distance = int(drag_distance_adjusted * scale_ratio)
        
        print(f"[5] Dragging {drag_distance}px to reach gap at {gap_x}px...")
        
        # Find slider and drag
        slider = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".scaptcha-card-slider-control")
        ))
        
        action = ActionChains(driver)
        action.click_and_hold(slider).perform()
        time.sleep(0.2)
        
        # Smooth drag with Easing (Ease-Out) and Float Accumulation for precision
        steps = 30
        duration = 0.8
        current_x = 0.0  # Use float for precision
        
        for i in range(steps):
            t = (i + 1) / steps
            ease_t = 1 - (1 - t) * (1 - t)
            
            # Target X for this step (Float)
            target_x = drag_distance * ease_t
            
            # Calculate Delta and round to nearest pixel
            delta_x = round(target_x - current_x)
            
            if delta_x != 0:
                action.move_by_offset(delta_x, random.randint(-1, 1)).perform()
                current_x += delta_x
                
            time.sleep(duration / steps)
        
        # Ensure we are at the exact end (final correction)
        remaining = drag_distance - int(current_x)
        if remaining != 0:
            action.move_by_offset(remaining, 0).perform()
        
        action.release().perform()
        
        # Wait for server to process the drag
        print("[6] Waiting for validation...")
        time.sleep(3)
        
        # Take screenshot AFTER drag
        driver.save_screenshot(f"{debug_dir}/after_drag.png")
        
        solved = False
        
        # Check if puzzle disappeared or checkbox verified (wait up to 10 seconds)
        for i in range(20):  # 20 * 0.5s = 10s max
            try:
                puzzle_card = driver.find_element(By.CSS_SELECTOR, ".scaptcha-card-container")
                if not puzzle_card.is_displayed():
                    solved = True
                    print("  ✓ Puzzle disappeared!")
                    break
            except:
                solved = True
                print("  ✓ Puzzle card removed!")
                break
                
            try:
                checkbox_class = checkbox.get_attribute('class')
                if 'verified' in checkbox_class or 'success' in checkbox_class:
                    solved = True
                    print("  ✓ Checkbox verified!")
                    break
            except:
                pass
                
            time.sleep(0.5)
        
        elapsed = time.time() - start_time
        
        # Wait before showing result to let any final animations complete
        time.sleep(2)
        
        print("\n" + "=" * 70)
        if solved:
            print(">>> SUCCESS! CAPTCHA SOLVED! <<<")
        else:
            print(">>> FAILED <<<")
        print(f"Gap: {gap_x}px | Dragged: {drag_distance}px | Time: {elapsed:.2f}s")
        print("=" * 70)
        
        print(f"\nCheck {debug_dir}/after_drag.png")
        print("Browser closing in 5 seconds...")
        time.sleep(5)
        
        return {
            "success": solved,
            "gap_x": gap_x,
            "drag_distance": drag_distance,
            "time_taken": round(elapsed, 2)
        }
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}
    finally:
        driver.quit()


if __name__ == "__main__":
    result = solve_slider_captcha("http://localhost:3000", verbose=True)
    print("\nFINAL RESULT:")
    print(result)
