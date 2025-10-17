public with sharing class Iren_Gruppo_Assistenza_Faq {
    private static final String API_BASE_URL = 'https://sunrise-vibes-eb1a0-ec988ab80bde.herokuapp.com';
    private static final Integer TIMEOUT_MS = 120000;
    private static final List<String> VALID_CATEGORIES = new List<String>{'acqua', 'ambiente', 'reti', 'teleriscaldamento'};

    @InvocableMethod(label='Cerco FAQ Gruppo Iren', description='Interroga le FAQ Assistenza Gruppo Iren', category='Iren Assistenza')
    public static List<FaqResponse> getFaqsByCategory(List<FaqRequest> requests) {
        List<FaqResponse> responses = new List<FaqResponse>();
        for (FaqRequest request : requests) {
            FaqResponse response = new FaqResponse();
            try {
                String categoria = request.categoria != null ? request.categoria.toLowerCase().trim() : null;
                if (String.isBlank(categoria)) {
                    throw new IrenFaqException('Categoria is required');
                }
                if (!VALID_CATEGORIES.contains(categoria)) {
                    throw new IrenFaqException('Invalid categoria: ' + categoria + '. Valid values are: ' + String.join(VALID_CATEGORIES, ', '));
                }
                HttpRequest req = new HttpRequest();
                req.setEndpoint(API_BASE_URL + '/api/faq/' + categoria);
                req.setMethod('GET');
                req.setTimeout(TIMEOUT_MS);
                req.setHeader('Content-Type', 'application/json');
                Http http = new Http();
                HttpResponse res = http.send(req);
                if (res.getStatusCode() == 200) {
                    Map<String, Object> jsonResponse = (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
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
            } catch (IrenFaqException e) {
                response.success = false;
                response.message = e.getMessage();
                response.errorCode = 'VALIDATION_ERROR';
            } catch (Exception e) {
                response.success = false;
                response.message = 'Unexpected error: ' + e.getMessage();
                response.errorCode = 'UNKNOWN_ERROR';
            }
            responses.add(response);
        }
        return responses;
    }

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
                Map<String, Object> jsonResponse = (Map<String, Object>) JSON.deserializeUntyped(res.getBody());
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
            throw e;
        }
        return allFaqs;
    }

    public class FaqRequest {
        @InvocableVariable(label='Categoria', description='acqua ambiente reti teleriscaldamento', required=true)
        public String categoria;
    }

    public class FaqResponse {
        @InvocableVariable(label='Success', description='Request successful')
        public Boolean success;
        @InvocableVariable(label='Categoria', description='Category requested')
        public String categoria;
        @InvocableVariable(label='Count', description='Number of FAQs')
        public Integer count;
        @InvocableVariable(label='FAQs', description='FAQ list')
        public List<Faq> faqs;
        @InvocableVariable(label='Message', description='Status message')
        public String message;
        @InvocableVariable(label='Error Code', description='Error code')
        public String errorCode;
        public FaqResponse() {
            this.success = false;
            this.count = 0;
            this.faqs = new List<Faq>();
        }
    }

    public class Faq {
        @InvocableVariable(label='Domanda', description='FAQ question')
        public String domanda;
        @InvocableVariable(label='Risposta', description='FAQ answer')
        public String risposta;
    }

    public class IrenFaqException extends Exception {}
}
