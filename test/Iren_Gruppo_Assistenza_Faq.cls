/**
 * @description Salesforce Apex class to invoke Gruppo Iren FAQ Scraper API
 * @author Firo
 * @date 2025-10-17
 *
 * This class provides invocable methods to retrieve FAQ data from the Heroku-hosted
 * Gruppo Iren FAQ scraper API. Can be used in Flow Builder, Process Builder,
 * and Apex code.
 *
 * SETUP REQUIRED:
 * 1. Add Remote Site Setting:
 *    - Name: IrenFaqAPI
 *    - URL: https://sunrise-vibes-eb1a0-ec988ab80bde.herokuapp.com
 *    - Active: true
 *
 * USAGE IN FLOW:
 * - Action: Get FAQ by Category
 * - Input: categoria (acqua/ambiente/reti/teleriscaldamento)
 * - Output: List of Faq objects
 */
public with sharing class Iren_Gruppo_Assistenza_Faq {

    // API Base URL
    private static final String API_BASE_URL = 'https://sunrise-vibes-eb1a0-ec988ab80bde.herokuapp.com';
    private static final Integer TIMEOUT_MS = 120000; // 120 seconds
    private static final List<String> VALID_CATEGORIES = new List<String>{
        'acqua', 'ambiente', 'reti', 'teleriscaldamento'
    };

    /**
     * @description Invocable method to get FAQs by category for use in Flow Builder
     * @param requests List of FaqRequest objects containing categoria
     * @return List<FaqResponse> containing the FAQ data
     */
    @InvocableMethod(
        label='Cerco nelle FAQ di Assistenza del sito di Gruppo Iren',
        description='Questo servizio Apex interroga le FAQ Assistenza Gruppo Iren.',
        category='Iren Assistenza'
    )
    public static List<FaqResponse> getFaqsByCategory(List<FaqRequest> requests) {
        List<FaqResponse> responses = new List<FaqResponse>();

        for (FaqRequest request : requests) {
            FaqResponse response = new FaqResponse();

            try {
                // Validate category
                String categoria = request.categoria != null ?
                    request.categoria.toLowerCase().trim() : null;

                if (String.isBlank(categoria)) {
                    throw new IrenFaqException('Categoria is required');
                }

                if (!VALID_CATEGORIES.contains(categoria)) {
                    throw new IrenFaqException(
                        'Invalid categoria: ' + categoria +
                        '. Valid values are: ' + String.join(VALID_CATEGORIES, ', ')
                    );
                }

                // Make HTTP callout
                HttpRequest req = new HttpRequest();
                req.setEndpoint(API_BASE_URL + '/api/faq/' + categoria);
                req.setMethod('GET');
                req.setTimeout(TIMEOUT_MS);
                req.setHeader('Content-Type', 'application/json');

                Http http = new Http();
                HttpResponse res = http.send(req);

                // Handle response
                if (res.getStatusCode() == 200) {
                    // Parse JSON response
                    Map<String, Object> jsonResponse =
                        (Map<String, Object>) JSON.deserializeUntyped(res.getBody());

                    response.success = true;
                    response.categoria = (String) jsonResponse.get('categoria');
                    response.count = (Integer) jsonResponse.get('count');
                    response.faqs = new List<Faq>();

                    List<Object> faqsList = (List<Object>) jsonResponse.get('faqs');
                    for (Object faqObj : faqsList) {
                        Map<String, Object> faqMap = (Map<String, Object>) faqObj;
                        Faq faq = new Faq();
                        faq.domanda = (String) faqMap.get('domanda');
                        faq.risposta = (String) faqMap.get('risposta');
                        response.faqs.add(faq);
                    }

                    response.message = 'Successfully retrieved ' + response.count + ' FAQs';

                } else if (res.getStatusCode() == 404) {
                    response.success = false;
                    response.message = 'Category not found: ' + categoria;
                    response.errorCode = 'NOT_FOUND';

                } else {
                    response.success = false;
                    response.message = 'HTTP Error ' + res.getStatusCode() + ': ' + res.getStatus();
                    response.errorCode = 'HTTP_ERROR';
                }

            } catch (CalloutException e) {
                response.success = false;
                response.message = 'Callout error: ' + e.getMessage();
                response.errorCode = 'CALLOUT_ERROR';
                System.debug(LoggingLevel.ERROR, 'Callout Exception: ' + e.getMessage());

            } catch (IrenFaqException e) {
                response.success = false;
                response.message = e.getMessage();
                response.errorCode = 'VALIDATION_ERROR';
                System.debug(LoggingLevel.ERROR, 'Validation Exception: ' + e.getMessage());

            } catch (Exception e) {
                response.success = false;
                response.message = 'Unexpected error: ' + e.getMessage();
                response.errorCode = 'UNKNOWN_ERROR';
                System.debug(LoggingLevel.ERROR, 'Exception: ' + e.getMessage() + '\n' + e.getStackTraceString());
            }

            responses.add(response);
        }

        return responses;
    }

    /**
     * @description Get all FAQs (non-invocable, for direct Apex usage)
     * @return Map<String, List<Faq>> containing all categories and their FAQs
     */
    public static Map<String, List<Faq>> getAllFaqs() {
        Map<String, List<Faq>> allFaqs = new Map<String, List<Faq>>();

        try {
            HttpRequest req = new HttpRequest();
            req.setEndpoint(API_BASE_URL + '/api/faq');
            req.setMethod('GET');
            req.setTimeout(TIMEOUT_MS);
            req.setHeader('Content-Type', 'application/json');

            Http http = new Http();
            HttpResponse res = http.send(req);

            if (res.getStatusCode() == 200) {
                Map<String, Object> jsonResponse =
                    (Map<String, Object>) JSON.deserializeUntyped(res.getBody());

                for (String categoria : jsonResponse.keySet()) {
                    List<Faq> faqsList = new List<Faq>();
                    List<Object> faqsArray = (List<Object>) jsonResponse.get(categoria);

                    for (Object faqObj : faqsArray) {
                        Map<String, Object> faqMap = (Map<String, Object>) faqObj;
                        Faq faq = new Faq();
                        faq.domanda = (String) faqMap.get('domanda');
                        faq.risposta = (String) faqMap.get('risposta');
                        faqsList.add(faq);
                    }

                    allFaqs.put(categoria, faqsList);
                }
            } else {
                throw new IrenFaqException('HTTP Error ' + res.getStatusCode());
            }

        } catch (Exception e) {
            System.debug(LoggingLevel.ERROR, 'Error getting all FAQs: ' + e.getMessage());
            throw e;
        }

        return allFaqs;
    }

    // ==================== WRAPPER CLASSES ====================

    /**
     * @description Input wrapper for invocable method
     */
    public class FaqRequest {
        @InvocableVariable(
            label='Categoria',
            description='Category to filter FAQs (acqua, ambiente, reti, teleriscaldamento)',
            required=true
        )
        public String categoria;
    }

    /**
     * @description Output wrapper for invocable method
     */
    public class FaqResponse {
        @InvocableVariable(label='Success', description='Whether the request was successful')
        public Boolean success;

        @InvocableVariable(label='Categoria', description='The category requested')
        public String categoria;

        @InvocableVariable(label='Count', description='Number of FAQs returned')
        public Integer count;

        @InvocableVariable(label='FAQs', description='List of FAQ objects')
        public List<Faq> faqs;

        @InvocableVariable(label='Message', description='Success or error message')
        public String message;

        @InvocableVariable(label='Error Code', description='Error code if failed')
        public String errorCode;

        public FaqResponse() {
            this.success = false;
            this.count = 0;
            this.faqs = new List<Faq>();
        }
    }

    /**
     * @description FAQ data wrapper
     */
    public class Faq {
        @InvocableVariable(label='Domanda', description='The FAQ question')
        public String domanda;

        @InvocableVariable(label='Risposta', description='The FAQ answer')
        public String risposta;
    }

    /**
     * @description Custom exception for Iren FAQ operations
     */
    public class IrenFaqException extends Exception {}
}
