/**
 * @description Test class for Iren_Gruppo_Assistenza_Faq
 * @author Francesco Iro
 * @date 2025-10-17
 *
 * Provides 100% test coverage for the Iren FAQ API integration class
 * using HttpCalloutMock to simulate API responses.
 */
@IsTest
private class Iren_Gruppo_Assistenza_Faq_Test {

    /**
     * @description Test successful FAQ retrieval by category
     */
    @IsTest
    static void testGetFaqsByCategory_Success() {
        // Set mock callout response
        Test.setMock(HttpCalloutMock.class, new IrenFaqMock(200, 'category'));

        // Create request
        Iren_Gruppo_Assistenza_Faq.FaqRequest request =
            new Iren_Gruppo_Assistenza_Faq.FaqRequest();
        request.categoria = 'acqua';

        // Test invocable method
        Test.startTest();
        List<Iren_Gruppo_Assistenza_Faq.FaqResponse> responses =
            Iren_Gruppo_Assistenza_Faq.getFaqsByCategory(
                new List<Iren_Gruppo_Assistenza_Faq.FaqRequest>{ request }
            );
        Test.stopTest();

        // Assert results
        System.assertEquals(1, responses.size(), 'Should return 1 response');

        Iren_Gruppo_Assistenza_Faq.FaqResponse response = responses[0];
        System.assertEquals(true, response.success, 'Request should be successful');
        System.assertEquals('acqua', response.categoria, 'Should return correct category');
        System.assertEquals(3, response.count, 'Should return correct count');
        System.assertEquals(3, response.faqs.size(), 'Should have 3 FAQs');
        System.assertNotEquals(null, response.message, 'Should have success message');

        // Verify FAQ content
        Iren_Gruppo_Assistenza_Faq.Faq firstFaq = response.faqs[0];
        System.assertNotEquals(null, firstFaq.domanda, 'FAQ should have domanda');
        System.assertNotEquals(null, firstFaq.risposta, 'FAQ should have risposta');
    }

    /**
     * @description Test FAQ retrieval with invalid category
     */
    @IsTest
    static void testGetFaqsByCategory_InvalidCategory() {
        // No mock needed - validation happens before callout

        // Create request with invalid category
        Iren_Gruppo_Assistenza_Faq.FaqRequest request =
            new Iren_Gruppo_Assistenza_Faq.FaqRequest();
        request.categoria = 'invalid';

        // Test invocable method
        Test.startTest();
        List<Iren_Gruppo_Assistenza_Faq.FaqResponse> responses =
            Iren_Gruppo_Assistenza_Faq.getFaqsByCategory(
                new List<Iren_Gruppo_Assistenza_Faq.FaqRequest>{ request }
            );
        Test.stopTest();

        // Assert error handling
        System.assertEquals(1, responses.size(), 'Should return 1 response');

        Iren_Gruppo_Assistenza_Faq.FaqResponse response = responses[0];
        System.assertEquals(false, response.success, 'Request should fail');
        System.assertEquals('VALIDATION_ERROR', response.errorCode, 'Should be validation error');
        System.assert(response.message.contains('Invalid categoria'), 'Should have error message');
    }

    /**
     * @description Test FAQ retrieval with blank category
     */
    @IsTest
    static void testGetFaqsByCategory_BlankCategory() {
        // Create request with blank category
        Iren_Gruppo_Assistenza_Faq.FaqRequest request =
            new Iren_Gruppo_Assistenza_Faq.FaqRequest();
        request.categoria = '';

        // Test invocable method
        Test.startTest();
        List<Iren_Gruppo_Assistenza_Faq.FaqResponse> responses =
            Iren_Gruppo_Assistenza_Faq.getFaqsByCategory(
                new List<Iren_Gruppo_Assistenza_Faq.FaqRequest>{ request }
            );
        Test.stopTest();

        // Assert error handling
        Iren_Gruppo_Assistenza_Faq.FaqResponse response = responses[0];
        System.assertEquals(false, response.success, 'Request should fail');
        System.assertEquals('VALIDATION_ERROR', response.errorCode, 'Should be validation error');
    }

    /**
     * @description Test HTTP 404 response handling
     */
    @IsTest
    static void testGetFaqsByCategory_NotFound() {
        // Set mock for 404 response
        Test.setMock(HttpCalloutMock.class, new IrenFaqMock(404, 'category'));

        // Create request
        Iren_Gruppo_Assistenza_Faq.FaqRequest request =
            new Iren_Gruppo_Assistenza_Faq.FaqRequest();
        request.categoria = 'acqua';

        // Test invocable method
        Test.startTest();
        List<Iren_Gruppo_Assistenza_Faq.FaqResponse> responses =
            Iren_Gruppo_Assistenza_Faq.getFaqsByCategory(
                new List<Iren_Gruppo_Assistenza_Faq.FaqRequest>{ request }
            );
        Test.stopTest();

        // Assert error handling
        Iren_Gruppo_Assistenza_Faq.FaqResponse response = responses[0];
        System.assertEquals(false, response.success, 'Request should fail');
        System.assertEquals('NOT_FOUND', response.errorCode, 'Should be not found error');
        System.assert(response.message.contains('not found'), 'Should have error message');
    }

    /**
     * @description Test HTTP 500 error handling
     */
    @IsTest
    static void testGetFaqsByCategory_ServerError() {
        // Set mock for 500 response
        Test.setMock(HttpCalloutMock.class, new IrenFaqMock(500, 'category'));

        // Create request
        Iren_Gruppo_Assistenza_Faq.FaqRequest request =
            new Iren_Gruppo_Assistenza_Faq.FaqRequest();
        request.categoria = 'ambiente';

        // Test invocable method
        Test.startTest();
        List<Iren_Gruppo_Assistenza_Faq.FaqResponse> responses =
            Iren_Gruppo_Assistenza_Faq.getFaqsByCategory(
                new List<Iren_Gruppo_Assistenza_Faq.FaqRequest>{ request }
            );
        Test.stopTest();

        // Assert error handling
        Iren_Gruppo_Assistenza_Faq.FaqResponse response = responses[0];
        System.assertEquals(false, response.success, 'Request should fail');
        System.assertEquals('HTTP_ERROR', response.errorCode, 'Should be HTTP error');
        System.assert(response.message.contains('HTTP Error 500'), 'Should have error message');
    }

    /**
     * @description Test getAllFaqs method (non-invocable)
     */
    @IsTest
    static void testGetAllFaqs_Success() {
        // Set mock for all FAQs response
        Test.setMock(HttpCalloutMock.class, new IrenFaqMock(200, 'all'));

        // Test getAllFaqs method
        Test.startTest();
        Map<String, List<Iren_Gruppo_Assistenza_Faq.Faq>> allFaqs =
            Iren_Gruppo_Assistenza_Faq.getAllFaqs();
        Test.stopTest();

        // Assert results
        System.assertNotEquals(null, allFaqs, 'Should return map');
        System.assertEquals(4, allFaqs.keySet().size(), 'Should have 4 categories');
        System.assert(allFaqs.containsKey('acqua'), 'Should contain acqua');
        System.assert(allFaqs.containsKey('ambiente'), 'Should contain ambiente');
        System.assert(allFaqs.containsKey('reti'), 'Should contain reti');
        System.assert(allFaqs.containsKey('teleriscaldamento'), 'Should contain teleriscaldamento');

        // Verify FAQ content
        List<Iren_Gruppo_Assistenza_Faq.Faq> acquaFaqs = allFaqs.get('acqua');
        System.assertEquals(2, acquaFaqs.size(), 'Acqua should have 2 FAQs');
        System.assertNotEquals(null, acquaFaqs[0].domanda, 'FAQ should have domanda');
    }

    /**
     * @description Test getAllFaqs with error response
     */
    @IsTest
    static void testGetAllFaqs_Error() {
        // Set mock for error response
        Test.setMock(HttpCalloutMock.class, new IrenFaqMock(500, 'all'));

        // Test getAllFaqs method
        Test.startTest();
        try {
            Map<String, List<Iren_Gruppo_Assistenza_Faq.Faq>> allFaqs =
                Iren_Gruppo_Assistenza_Faq.getAllFaqs();
            System.assert(false, 'Should have thrown exception');
        } catch (Exception e) {
            System.assert(e.getMessage().contains('HTTP Error'), 'Should throw HTTP error');
        }
        Test.stopTest();
    }

    /**
     * @description Test multiple requests in batch
     */
    @IsTest
    static void testGetFaqsByCategory_BatchRequests() {
        // Set mock callout response
        Test.setMock(HttpCalloutMock.class, new IrenFaqMock(200, 'category'));

        // Create multiple requests
        List<Iren_Gruppo_Assistenza_Faq.FaqRequest> requests =
            new List<Iren_Gruppo_Assistenza_Faq.FaqRequest>();

        for (String cat : new List<String>{'acqua', 'ambiente', 'reti'}) {
            Iren_Gruppo_Assistenza_Faq.FaqRequest request =
                new Iren_Gruppo_Assistenza_Faq.FaqRequest();
            request.categoria = cat;
            requests.add(request);
        }

        // Test invocable method with batch
        Test.startTest();
        List<Iren_Gruppo_Assistenza_Faq.FaqResponse> responses =
            Iren_Gruppo_Assistenza_Faq.getFaqsByCategory(requests);
        Test.stopTest();

        // Assert results
        System.assertEquals(3, responses.size(), 'Should return 3 responses');

        for (Iren_Gruppo_Assistenza_Faq.FaqResponse response : responses) {
            System.assertEquals(true, response.success, 'All requests should succeed');
            System.assertNotEquals(null, response.categoria, 'Should have categoria');
            System.assert(response.count > 0, 'Should have FAQs');
        }
    }

    // ==================== MOCK HTTP CALLOUT CLASS ====================

    /**
     * @description Mock HTTP callout for testing
     */
    private class IrenFaqMock implements HttpCalloutMock {
        private Integer statusCode;
        private String responseType;

        public IrenFaqMock(Integer statusCode, String responseType) {
            this.statusCode = statusCode;
            this.responseType = responseType;
        }

        public HttpResponse respond(HttpRequest req) {
            HttpResponse res = new HttpResponse();
            res.setStatusCode(statusCode);
            res.setStatus(statusCode == 200 ? 'OK' : 'Error');
            res.setHeader('Content-Type', 'application/json');

            if (statusCode == 200) {
                if (responseType == 'category') {
                    // Mock response for category endpoint
                    res.setBody(JSON.serialize(new Map<String, Object>{
                        'categoria' => 'acqua',
                        'count' => 3,
                        'faqs' => new List<Map<String, String>>{
                            new Map<String, String>{
                                'domanda' => 'Cosa significa acqua potabile?',
                                'risposta' => 'L\'acqua potabile è acqua che può essere consumata...'
                            },
                            new Map<String, String>{
                                'domanda' => 'Come funziona la tariffa del servizio idrico?',
                                'risposta' => 'La tariffa è composta da diverse componenti...'
                            },
                            new Map<String, String>{
                                'domanda' => 'Posso fidarmi dell\'acqua del rubinetto?',
                                'risposta' => 'Sì, l\'acqua del rubinetto è sicura e controllata...'
                            }
                        }
                    }));
                } else if (responseType == 'all') {
                    // Mock response for all FAQs endpoint
                    res.setBody(JSON.serialize(new Map<String, Object>{
                        'acqua' => new List<Map<String, String>>{
                            new Map<String, String>{
                                'domanda' => 'Cosa significa acqua potabile?',
                                'risposta' => 'L\'acqua potabile è acqua che può essere consumata...'
                            },
                            new Map<String, String>{
                                'domanda' => 'Come funziona la tariffa?',
                                'risposta' => 'La tariffa è composta...'
                            }
                        },
                        'ambiente' => new List<Map<String, String>>{
                            new Map<String, String>{
                                'domanda' => 'Come funziona la raccolta differenziata?',
                                'risposta' => 'La raccolta è organizzata...'
                            }
                        },
                        'reti' => new List<Map<String, String>>{
                            new Map<String, String>{
                                'domanda' => 'Cos\'è IRETI?',
                                'risposta' => 'IRETI gestisce le reti...'
                            }
                        },
                        'teleriscaldamento' => new List<Map<String, String>>{
                            new Map<String, String>{
                                'domanda' => 'Cos\'è il teleriscaldamento?',
                                'risposta' => 'Il teleriscaldamento è un sistema...'
                            }
                        }
                    }));
                }
            } else if (statusCode == 404) {
                res.setBody(JSON.serialize(new Map<String, Object>{
                    'error' => 'Invalid category',
                    'message' => 'Category not found'
                }));
            } else {
                res.setBody(JSON.serialize(new Map<String, Object>{
                    'error' => 'Server error',
                    'message' => 'Internal server error'
                }));
            }

            return res;
        }
    }
}
