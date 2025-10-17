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

        # Find all accordion buttons (questions)
        buttons = soup.find_all('button', attrs={'data-bs-toggle': 'collapse'})
        logger.info(f"Found {len(buttons)} FAQ buttons")

        processed_count = 0

        # Process each button and its associated collapse div
        for button in buttons:
            try:
                # Get the question text from the button
                question_text = button.get_text(strip=True)

                if not question_text or len(question_text) < 5:
                    continue

                # Find the associated collapse div using aria-controls or data-bs-target
                target_id = button.get('data-bs-target') or button.get('aria-controls')

                if target_id:
                    # Remove the # if present
                    target_id = target_id.lstrip('#')

                    # Find the collapse div by ID
                    collapse_div = soup.find('div', id=target_id)

                    if collapse_div:
                        # Get the answer text from the collapse div
                        answer_text = collapse_div.get_text(strip=True)

                        # Skip if no valid content
                        if not answer_text or len(answer_text) < 10:
                            continue

                        # Clean up the answer - sometimes it contains the question
                        if answer_text.startswith(question_text):
                            answer_text = answer_text[len(question_text):].strip()

                        # Determine category by looking at parent sections
                        category = "acqua"  # Default

                        # Look for category indicators in parent elements
                        parent_section = button.find_parent(['section', 'div'], id=True)
                        if not parent_section:
                            parent_section = collapse_div.find_parent(['section', 'div'], id=True)

                        if parent_section:
                            section_id = parent_section.get('id', '').lower()
                            section_class = ' '.join(parent_section.get('class', [])).lower()

                            combined_text = f"{section_id} {section_class}"

                            if 'teleriscaldamento' in combined_text:
                                category = "teleriscaldamento"
                            elif 'ambiente' in combined_text:
                                category = "ambiente"
                            elif 'reti' in combined_text or 'rete' in combined_text:
                                category = "reti"
                            elif 'acqua' in combined_text:
                                category = "acqua"

                        # If still no category found, look in the surrounding text
                        if category == "acqua":
                            # Get the parent accordion container
                            accordion_parent = button.find_parent('div', class_=lambda x: x and 'accordion' in x.lower() if x else False)
                            if accordion_parent:
                                # Look for a header or title near this accordion
                                prev_heading = accordion_parent.find_previous(['h1', 'h2', 'h3', 'h4'])
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

                        faq_item = {
                            "domanda": question_text,
                            "risposta": answer_text
                        }

                        faq_data[category].append(faq_item)
                        processed_count += 1

                        if processed_count <= 5:  # Log first few for debugging
                            logger.info(f"Extracted FAQ {processed_count}: {question_text[:60]}... -> {category}")

            except Exception as e:
                logger.warning(f"Error processing FAQ button: {str(e)}")
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
