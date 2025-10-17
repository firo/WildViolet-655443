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
            "/api/faq": "Get all FAQ data organized by category",
            "/api/faq/<category>": "Get FAQ data for a specific category"
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

@app.route('/api/faq/<categoria>', methods=['GET'])
def get_faq_by_category(categoria):
    """API endpoint to get FAQ data for a specific category"""
    # Valid categories
    valid_categories = ["teleriscaldamento", "acqua", "ambiente", "reti"]

    # Normalize category input
    categoria = categoria.lower().strip()

    # Validate category
    if categoria not in valid_categories:
        return jsonify({
            "error": "Invalid category",
            "message": f"Category '{categoria}' is not valid. Valid categories are: {', '.join(valid_categories)}",
            "valid_categories": valid_categories
        }), 404

    try:
        logger.info(f"Starting FAQ scraping for category: {categoria}...")
        faq_data = scrape_faq()

        # Return only the requested category
        category_data = faq_data.get(categoria, [])
        logger.info(f"Returning {len(category_data)} FAQs for category '{categoria}'")

        return jsonify({
            "categoria": categoria,
            "count": len(category_data),
            "faqs": category_data
        })
    except Exception as e:
        logger.error(f"Error scraping FAQ for category {categoria}: {str(e)}")
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
