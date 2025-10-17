import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

FAQ_URL = "https://www.gruppoiren.it/it/assistenza/faq.html"

def get_chrome_driver():
    """Configure and return Chrome driver for Heroku"""
    chrome_options = Options()

    # Essential options for Heroku
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    driver = webdriver.Chrome(options=chrome_options)
    return driver

def scrape_faq():
    """
    Scrape FAQ data from Gruppo Iren website.
    Returns a dictionary with categories as keys and list of Q&A objects as values.
    """
    driver = None
    try:
        logger.info(f"Initializing Chrome driver...")
        driver = get_chrome_driver()

        logger.info(f"Loading FAQ page: {FAQ_URL}")
        driver.get(FAQ_URL)

        # Wait for page to load
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Give the page extra time to fully render
        time.sleep(3)

        logger.info("Page loaded, starting to extract FAQ data...")

        # Initialize result structure
        faq_data = {
            "teleriscaldamento": [],
            "acqua": [],
            "ambiente": [],
            "reti": []
        }

        # Try to find all FAQ items (questions)
        # The structure might vary, so we'll try multiple selectors
        faq_elements = driver.find_elements(By.CSS_SELECTOR, ".accordion-item, .faq-item, [class*='faq'], [class*='accordion']")

        if not faq_elements:
            logger.warning("No FAQ elements found with common selectors, trying alternative approach...")
            # Try to find clickable elements that might be questions
            faq_elements = driver.find_elements(By.CSS_SELECTOR, "[role='button'], .btn, button")

        logger.info(f"Found {len(faq_elements)} potential FAQ elements")

        # Get the full page source for parsing
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Try to find FAQ sections by category
        # Look for sections or divs that might contain category information
        for category_name in faq_data.keys():
            logger.info(f"Searching for category: {category_name}")

            # Try to find elements that might contain this category
            category_elements = driver.find_elements(By.XPATH,
                f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{category_name.lower()}')]")

            if category_elements:
                logger.info(f"Found {len(category_elements)} elements for category {category_name}")

        # Try a more general approach: find all clickable FAQ items
        clickable_elements = driver.find_elements(By.CSS_SELECTOR,
            "button[data-bs-toggle], [data-toggle], .accordion-button, [role='button']")

        logger.info(f"Found {len(clickable_elements)} clickable elements")

        processed_questions = set()

        for idx, element in enumerate(clickable_elements[:50]):  # Limit to first 50 to avoid timeout
            try:
                # Get question text before clicking
                question_text = element.text.strip()

                if not question_text or question_text in processed_questions:
                    continue

                processed_questions.add(question_text)

                # Scroll to element
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.5)

                # Click to reveal answer
                try:
                    element.click()
                    time.sleep(1)
                except:
                    # Try JavaScript click if regular click fails
                    driver.execute_script("arguments[0].click();", element)
                    time.sleep(1)

                # Find the answer - look for nearby expanded content
                try:
                    # Try multiple selectors for answer content
                    answer_element = driver.find_element(By.XPATH,
                        "./following-sibling::*[contains(@class, 'collapse') or contains(@class, 'answer') or contains(@class, 'content')]")
                    answer_text = answer_element.text.strip()
                except:
                    # Try finding within parent
                    try:
                        parent = element.find_element(By.XPATH, "./..")
                        answer_element = parent.find_element(By.CSS_SELECTOR,
                            ".collapse.show, .answer, .faq-answer, [class*='answer']")
                        answer_text = answer_element.text.strip()
                    except:
                        answer_text = ""

                if answer_text and answer_text != question_text:
                    # Try to determine category from surrounding context
                    category = "acqua"  # Default category

                    try:
                        # Look for category indicators in parent elements
                        parent_text = element.find_element(By.XPATH, "./ancestor::*[3]").text.lower()

                        if "teleriscaldamento" in parent_text:
                            category = "teleriscaldamento"
                        elif "ambiente" in parent_text:
                            category = "ambiente"
                        elif "reti" in parent_text or "rete" in parent_text:
                            category = "reti"
                        elif "acqua" in parent_text:
                            category = "acqua"
                    except:
                        pass

                    faq_item = {
                        "domanda": question_text,
                        "risposta": answer_text
                    }

                    faq_data[category].append(faq_item)
                    logger.info(f"Extracted FAQ {idx + 1}: {question_text[:50]}... -> {category}")

            except Exception as e:
                logger.warning(f"Error processing element {idx}: {str(e)}")
                continue

        # Count total FAQs extracted
        total_faqs = sum(len(v) for v in faq_data.values())
        logger.info(f"Successfully extracted {total_faqs} FAQs across all categories")

        for category, items in faq_data.items():
            logger.info(f"  - {category}: {len(items)} FAQs")

        return faq_data

    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        raise

    finally:
        if driver:
            logger.info("Closing Chrome driver...")
            driver.quit()
