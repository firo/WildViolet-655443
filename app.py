import os
import logging
from flask import Flask, jsonify
from scraper import scrape_faq

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    """Home endpoint with API information"""
    return jsonify({
        "message": "Gruppo Iren FAQ Scraper API",
        "endpoints": {
            "/api/faq": "Get all FAQ data organized by category"
        },
        "categories": ["teleriscaldamento", "acqua", "ambiente", "reti"]
    })

@app.route('/api/faq', methods=['GET'])
def get_faq():
    """API endpoint to get all FAQ data"""
    try:
        logger.info("Starting FAQ scraping...")
        faq_data = scrape_faq()
        logger.info(f"Successfully scraped FAQ data. Categories: {list(faq_data.keys())}")
        return jsonify(faq_data)
    except Exception as e:
        logger.error(f"Error scraping FAQ: {str(e)}")
        return jsonify({
            "error": "Failed to scrape FAQ data",
            "message": str(e)
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
