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

        # Find all accordion items first
        all_accordion_items = soup.find_all('div', class_=lambda x: x and 'accordion-item' in x if x else False)
        logger.info(f"Found {len(all_accordion_items)} total accordion items on page")

        # Try to find tab buttons or category buttons that might indicate sections
        tab_buttons = soup.find_all(['button', 'a'], class_=lambda x: x and ('tab' in x.lower() or 'nav' in x.lower()) if x else False)
        logger.info(f"Found {len(tab_buttons)} potential tab/navigation buttons")

        # Process each accordion item and determine its category
        for idx, item in enumerate(all_accordion_items):
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

                    # Determine category using multiple approaches
                    category = None

                    # Approach 1: Look at all parent elements for category indicators
                    current = item
                    for _ in range(10):  # Check up to 10 levels up
                        parent = current.find_parent()
                        if not parent:
                            break

                        # Check parent's ID and classes
                        parent_id = parent.get('id', '').lower()
                        parent_classes = ' '.join(parent.get('class', [])).lower()
                        combined = f"{parent_id} {parent_classes}"

                        if 'teleriscaldamento' in combined or 'teleris' in combined:
                            category = "teleriscaldamento"
                            break
                        elif 'ambiente' in combined or 'environment' in combined:
                            category = "ambiente"
                            break
                        elif 'reti' in combined or 'rete' in combined or 'network' in combined:
                            category = "reti"
                            break
                        elif 'acqua' in combined or 'water' in combined:
                            category = "acqua"
                            break

                        current = parent

                    # Approach 2: Look for nearby headings
                    if not category:
                        prev_heading = item.find_previous(['h1', 'h2', 'h3', 'h4', 'h5'])
                        if prev_heading:
                            heading_text = prev_heading.get_text().lower()
                            if 'teleriscaldamento' in heading_text:
                                category = "teleriscaldamento"
                            elif 'ambiente' in heading_text:
                                category = "ambiente"
                            elif 'reti' in heading_text or 'rete' in heading_text:
                                category = "reti"
                            elif 'acqua' in heading_text:
                                category = "acqua"

                    # Approach 3: Look at question/answer content for keywords
                    if not category:
                        combined_text = (question_text + " " + answer_text).lower()
                        if any(word in combined_text for word in ['teleriscaldamento', 'calore', 'scambiatore', 'caldaia']):
                            category = "teleriscaldamento"
                        elif any(word in combined_text for word in ['rifiuti', 'raccolta', 'differenziata', 'termovalorizzatore']):
                            category = "ambiente"
                        elif any(word in combined_text for word in ['elettrica', 'elettrico', 'distribuzione energia', 'rete elettrica', 'ireti']):
                            category = "reti"
                        elif any(word in combined_text for word in ['acqua', 'acquedotto', 'fognatura', 'idrico']):
                            category = "acqua"

                    # Default to acqua if still no category found
                    if not category:
                        category = "acqua"

                    faq_item = {
                        "domanda": question_text,
                        "risposta": answer_text
                    }

                    # Add to the determined category
                    faq_data[category].append(faq_item)
                    total_extracted += 1

                    if total_extracted <= 10:  # Log first 10 overall
                        logger.info(f"FAQ {total_extracted} -> {category}: {question_text[:50]}...")

            except Exception as e:
                logger.warning(f"Error processing accordion item {idx}: {str(e)}")
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
