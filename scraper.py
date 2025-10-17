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

        # Use JavaScript to expand all accordion items at once - try multiple selectors
        # This avoids stale element references
        expand_script = """
        var selectors = [
            'button[data-bs-toggle="collapse"]',
            'button[data-toggle="collapse"]',
            '[data-bs-toggle="collapse"]',
            '[data-toggle="collapse"]',
            '.accordion-button',
            'button[aria-expanded]'
        ];
        var totalExpanded = 0;

        selectors.forEach(function(selector) {
            var elements = document.querySelectorAll(selector);
            console.log('Selector ' + selector + ' found ' + elements.length + ' elements');
            elements.forEach(function(btn) {
                try {
                    if (btn.getAttribute('aria-expanded') !== 'true') {
                        btn.click();
                        totalExpanded++;
                    }
                } catch(e) {
                    console.log('Error clicking element:', e);
                }
            });
        });

        return totalExpanded;
        """

        num_expanded = driver.execute_script(expand_script)
        logger.info(f"Attempted to expand {num_expanded} accordion items")

        # Wait for accordions to expand
        time.sleep(3)

        # Now parse the fully expanded page with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        total_extracted = 0

        # OUTER LOOP: Process each category separately
        for category_name in faq_data.keys():
            logger.info(f"Processing category: {category_name}")

            # Find the section/container for this specific category
            # Try multiple strategies to find the category container
            category_container = None

            # Strategy 1: Look for element with ID containing category name
            category_container = soup.find(id=lambda x: x and category_name.lower() in x.lower() if x else False)

            # Strategy 2: Look for section with data attribute containing category
            if not category_container:
                category_container = soup.find(attrs={'data-category': lambda x: x and category_name.lower() in x.lower() if x else False})

            # Strategy 3: Look for heading containing category name, then get parent container
            if not category_container:
                heading = soup.find(['h1', 'h2', 'h3', 'h4', 'h5'],
                                   string=lambda x: x and category_name.lower() in x.lower() if x else False)
                if heading:
                    # Get the parent container after the heading
                    category_container = heading.find_next(['div', 'section'],
                                                          class_=lambda x: x and ('accordion' in x.lower() or 'faq' in x.lower()) if x else False)

            # Strategy 4: Look for div with class containing category name
            if not category_container:
                category_container = soup.find('div', class_=lambda x: x and category_name.lower() in x.lower() if x else False)

            if not category_container:
                logger.warning(f"Could not find container for category: {category_name}")
                continue

            logger.info(f"Found container for {category_name}")

            # INNER LOOP: Find all accordion items within this category container
            accordion_items = category_container.find_all('div',
                                                          class_=lambda x: x and 'accordion-item' in x if x else False,
                                                          recursive=True)

            logger.info(f"Found {len(accordion_items)} accordion items in {category_name} category")

            # Process each accordion item within this category
            for idx, item in enumerate(accordion_items):
                try:
                    # Find the button/header within this accordion item
                    button = item.find('button') or item.find(['h2', 'h3', 'h4', 'h5'])

                    if not button:
                        continue

                    question_text = button.get_text(strip=True)

                    if not question_text or len(question_text) < 5:
                        continue

                    # Find the collapse div within this same accordion item
                    collapse_div = item.find('div',
                                            class_=lambda x: x and ('collapse' in x or 'accordion-collapse' in x) if x else False)

                    if not collapse_div:
                        # Try finding the next sibling
                        collapse_div = button.find_next_sibling('div')

                    if collapse_div:
                        # Get the answer text from the collapse div
                        answer_text = collapse_div.get_text(strip=True)

                        # Skip if no valid content
                        if not answer_text or len(answer_text) < 10:
                            continue

                        # Clean up the answer - remove the question if it's at the start
                        if answer_text.startswith(question_text):
                            answer_text = answer_text[len(question_text):].strip()

                        faq_item = {
                            "domanda": question_text,
                            "risposta": answer_text
                        }

                        # Add to the current category
                        faq_data[category_name].append(faq_item)
                        total_extracted += 1

                        if len(faq_data[category_name]) <= 3:  # Log first 3 for each category
                            logger.info(f"[{category_name}] FAQ {len(faq_data[category_name])}: {question_text[:50]}...")

                except Exception as e:
                    logger.warning(f"Error processing accordion item in {category_name}: {str(e)}")
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
