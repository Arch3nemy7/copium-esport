import json
import logging
from typing import Tuple
import pyautogui
import pytesseract
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import pygetwindow as gw
import time
import re
from fuzzywuzzy import fuzz
from concurrent.futures import ThreadPoolExecutor

with open('config/config.json', 'r') as f:
    config = json.load(f)
    
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

pytesseract.pytesseract.tesseract_cmd = config['tesseract_path']

def activate_chrome() -> bool:
    try:
        chrome_windows = gw.getWindowsWithTitle('Google Chrome')
        if chrome_windows:
            chrome_windows[0].activate()
            return True
        else:
            logger.warning("Chrome window not found.")
            return False
    except Exception as e:
        logger.error(f"Error activating Chrome: {e}")
        return False

def preprocess_image(image: Image.Image) -> Image.Image:
    try:
        grayscale_image = ImageOps.grayscale(image)
        enhanced_image = ImageEnhance.Contrast(grayscale_image).enhance(2)
        sharpened_image = enhanced_image.filter(ImageFilter.EDGE_ENHANCE_MORE)
        binary_image = sharpened_image.point(lambda x: 0 if x < 128 else 255, '1')
        return binary_image
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        return image

def apply_corrections(text):
    return config['corrections'].get(text, text)

def capture_and_ocr(region: Tuple[int, int, int, int], ocr_config: str = None) -> str:
    try:
        screenshot = pyautogui.screenshot(region=region)
        preprocessed_image = preprocess_image(screenshot)
        text = pytesseract.image_to_string(preprocessed_image, config=ocr_config)
        
        text = re.sub(r'\n+', ' ', text).strip()
        disinfected_text = re.sub(r'[^A-Za-z0-9]', '', text)
        corrected_text = apply_corrections(disinfected_text)
        logger.info(f"Recognized Text: {corrected_text}")
        return corrected_text
    except Exception as e:
        logger.error(f"Error in capture_and_ocr: {e}")
        return ""

def determine_answer_type(question_text):
    question_text = question_text.lower()
    
    if any(keyword in question_text.lower() for keyword in ["jumlah", "ke", "durasi"]):
        return "number"

    if re.search(r'\b(\d+|satuan|minggu|bulan)\b', question_text):
        return "number"
    
    return "text"

def ocr_task(region, answer_type):
    custom_config = config['ocr_config']['number_answer'] if answer_type == "number" else config['ocr_config']['text_answer']
    return capture_and_ocr(region, ocr_config=custom_config)

def automate_based_on_ocr(question_text, answer_texts, answer_coords):
    correct_answer = config['qa_pairs'].get(question_text, None)
    
    if correct_answer:
        for i, answer_text in enumerate(answer_texts):
            if fuzz.partial_ratio(correct_answer.lower(), answer_text.lower()) > 69:
                pyautogui.click(answer_coords[i])
                pyautogui.click(answer_coords[i])
                print(f"Clicked on answer {i+1}: {correct_answer}")
                return
    print("No matching answer found.")

def process_chapter():
    for i in range(4):
        print(f"Processing Question { i + 1 }...")
        
        question_text = capture_and_ocr(tuple(config['question_regions'][i]), ocr_config=config['ocr_config']['question'])
        
        answer_type = determine_answer_type(question_text)
        
        with ThreadPoolExecutor() as executor:
            answer_texts = list(executor.map(lambda r: ocr_task(tuple(r), answer_type), config['answer_regions'][i]))
        
        automate_based_on_ocr(question_text, answer_texts, config['answer_coords'][i])

def main():
    if not activate_chrome():
        return

    while True:
        try:
            pyautogui.press('f')
            time.sleep(config['timing']['initial_wait'])

            for click in config['initial_clicks']:
                time.sleep(config['timing']['cautious_wait_long'])
                pyautogui.click(*click)
            time.sleep(config['timing']['chapter_wait'])

            for chapter in range(3):
                print(f"Processing Chapter { chapter + 1 }...")
                process_chapter()

                pyautogui.click(*config['next_chapter_click'])
                pyautogui.click(*config['next_chapter_click'])
                time.sleep(config['timing']['next_chapter_wait'])

                if chapter == 2:
                    time.sleep(config['timing']['final_wait'])
                    for coord in config['final_clicks']:
                        pyautogui.click(*coord)
                        pyautogui.click(*coord)
                        time.sleep(config['timing']['final_click_wait'])

                    time.sleep(config['timing']['initial_wait'])
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(config['timing']['error_wait'])

if __name__ == "__main__":
    main()
