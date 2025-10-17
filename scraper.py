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

        # Use JavaScript to expand all accordion items at once
        # This avoids stale element references
        expand_script = """
        var buttons = document.querySelectorAll('button[data-bs-toggle="collapse"]');
        console.log('Found ' + buttons.length + ' accordion buttons');
        buttons.forEach(function(btn) {
            try {
                if (btn.getAttribute('aria-expanded') !== 'true') {
                    btn.click();
                }
            } catch(e) {
                console.log('Error clicking button:', e);
            }
        });
        return buttons.length;
        """

        num_expanded = driver.execute_script(expand_script)
        logger.info(f"Attempted to expand {num_expanded} accordion items")

        # Wait for accordions to expand
        time.sleep(3)

        # Now parse the fully expanded page with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find accordion items - common Bootstrap structure
        accordion_items = soup.find_all(['div', 'section'], class_=lambda x: x and ('accordion' in x.lower() or 'faq' in x.lower()))
        logger.info(f"Found {len(accordion_items)} accordion containers")

        # Try finding individual FAQ items
        # Look for Bootstrap accordion structure
        faq_items = soup.find_all('div', class_=lambda x: x and 'accordion-item' in x)

        if not faq_items:
            # Try alternative structure
            faq_items = soup.find_all('div', class_=lambda x: x and 'collapse' in x)
            logger.info(f"Found {len(faq_items)} collapsible items")
        else:
            logger.info(f"Found {len(faq_items)} accordion items")

        processed_count = 0

        # Process each FAQ item
        for item in faq_items:
            try:
                # Find the question - usually in a button or header
                question_elem = item.find_previous('button') or item.find_previous(['h2', 'h3', 'h4', 'h5'])

                if not question_elem:
                    # Try finding within parent
                    parent = item.find_parent('div', class_=lambda x: x and 'accordion-item' in x if x else False)
                    if parent:
                        question_elem = parent.find('button')

                if not question_elem:
                    continue

                question_text = question_elem.get_text(strip=True)

                # Get the answer from the collapse div
                answer_text = item.get_text(strip=True)

                # Skip if no valid content
                if not question_text or not answer_text or len(answer_text) < 10:
                    continue

                # Remove the question from answer if it's included
                if answer_text.startswith(question_text):
                    answer_text = answer_text[len(question_text):].strip()

                # Determine category by looking at parent sections
                category = "acqua"  # Default

                # Look for category indicators in parent elements
                parent_section = item.find_parent(['section', 'div'], id=True)
                if parent_section:
                    section_id = parent_section.get('id', '').lower()
                    section_class = ' '.join(parent_section.get('class', [])).lower()
                    section_text = parent_section.get_text().lower()

                    combined_text = f"{section_id} {section_class}"

                    if 'teleriscaldamento' in combined_text or 'teleriscaldamento' in section_text[:200]:
                        category = "teleriscaldamento"
                    elif 'ambiente' in combined_text or 'ambiente' in section_text[:200]:
                        category = "ambiente"
                    elif 'reti' in combined_text or 'rete' in combined_text:
                        category = "reti"
                    elif 'acqua' in combined_text or 'acqua' in section_text[:200]:
                        category = "acqua"

                faq_item = {
                    "domanda": question_text,
                    "risposta": answer_text
                }

                faq_data[category].append(faq_item)
                processed_count += 1

                if processed_count <= 5:  # Log first few for debugging
                    logger.info(f"Extracted FAQ: {question_text[:60]}... -> {category}")

            except Exception as e:
                logger.warning(f"Error processing FAQ item: {str(e)}")
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
