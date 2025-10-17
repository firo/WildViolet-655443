# Iren Gruppo Assistenza FAQ - Salesforce Apex Integration

Classi Apex per integrare l'API REST Gruppo Iren FAQ in Salesforce.

## 📦 Files

- `Iren_Gruppo_Assistenza_Faq.cls` - Classe principale con @InvocableMethod
- `Iren_Gruppo_Assistenza_Faq.cls-meta.xml` - Metadata
- `Iren_Gruppo_Assistenza_Faq_Test.cls` - Classe di test con 100% coverage
- `Iren_Gruppo_Assistenza_Faq_Test.cls-meta.xml` - Metadata test

## 🚀 Setup in Salesforce

### 1. Deploy Classi Apex

Usando Salesforce CLI:

```bash
sf project deploy start --source-dir test/ --target-org YOUR_ORG
```

Oppure usando VS Code con Salesforce Extension:
1. Right-click sulla cartella `test/`
2. SFDX: Deploy Source to Org

### 2. Configure Remote Site Settings

**Setup → Security → Remote Site Settings → New Remote Site**

- **Remote Site Name**: `IrenFaqAPI`
- **Remote Site URL**: `https://sunrise-vibes-eb1a0-ec988ab80bde.herokuapp.com`
- **Active**: ✅ Checked
- **Description**: Gruppo Iren FAQ Scraper API

⚠️ **IMPORTANTE**: Senza questo setting, i callout HTTP falliranno!

### 3. Run Tests

```bash
sf apex run test --class-names Iren_Gruppo_Assistenza_Faq_Test --result-format human
```

Expected: **100% code coverage** - 8/8 test methods passing

---

## 🔧 Usage Examples

### In Flow Builder (Recommended)

1. **Create New Flow** → Screen Flow or Autolaunched Flow
2. **Add Action** → Search "Get Iren FAQ by Category"
3. **Configure**:
   - **Categoria**: `acqua` (or ambiente, reti, teleriscaldamento)
4. **Store Output** to variables
5. **Use FAQ data** in Screen elements or logic

**Example Flow**:
```
[Screen Input: picklist with categories]
  ↓
[Action: Get Iren FAQ by Category]
  ↓
[Loop through FAQs]
  ↓
[Display FAQ domanda and risposta]
```

### In Apex Code

#### Get FAQs by Category (Invocable)

```apex
// Create request
Iren_Gruppo_Assistenza_Faq.FaqRequest request =
    new Iren_Gruppo_Assistenza_Faq.FaqRequest();
request.categoria = 'acqua';

// Call invocable method
List<Iren_Gruppo_Assistenza_Faq.FaqResponse> responses =
    Iren_Gruppo_Assistenza_Faq.getFaqsByCategory(
        new List<Iren_Gruppo_Assistenza_Faq.FaqRequest>{ request }
    );

// Process response
Iren_Gruppo_Assistenza_Faq.FaqResponse response = responses[0];
if (response.success) {
    System.debug('Found ' + response.count + ' FAQs');
    for (Iren_Gruppo_Assistenza_Faq.Faq faq : response.faqs) {
        System.debug('Q: ' + faq.domanda);
        System.debug('A: ' + faq.risposta);
    }
} else {
    System.debug('Error: ' + response.message);
}
```

#### Get All FAQs (Direct Method)

```apex
try {
    Map<String, List<Iren_Gruppo_Assistenza_Faq.Faq>> allFaqs =
        Iren_Gruppo_Assistenza_Faq.getAllFaqs();

    // Process each category
    for (String categoria : allFaqs.keySet()) {
        List<Iren_Gruppo_Assistenza_Faq.Faq> faqsList = allFaqs.get(categoria);
        System.debug(categoria + ': ' + faqsList.size() + ' FAQs');
    }
} catch (Exception e) {
    System.debug('Error: ' + e.getMessage());
}
```

### In Anonymous Apex (Testing)

Open Developer Console → Debug → Open Execute Anonymous Window:

```apex
// Quick test
Iren_Gruppo_Assistenza_Faq.FaqRequest req =
    new Iren_Gruppo_Assistenza_Faq.FaqRequest();
req.categoria = 'ambiente';

List<Iren_Gruppo_Assistenza_Faq.FaqResponse> res =
    Iren_Gruppo_Assistenza_Faq.getFaqsByCategory(
        new List<Iren_Gruppo_Assistenza_Faq.FaqRequest>{ req }
    );

System.debug(JSON.serializePretty(res[0]));
```

---

## 📊 API Response Structure

### Success Response

```apex
FaqResponse {
    success: true,
    categoria: 'acqua',
    count: 23,
    faqs: [
        Faq {
            domanda: 'Cosa significa acqua potabile?',
            risposta: 'L\'acqua potabile è acqua che...'
        },
        ...
    ],
    message: 'Successfully retrieved 23 FAQs',
    errorCode: null
}
```

### Error Response

```apex
FaqResponse {
    success: false,
    categoria: null,
    count: 0,
    faqs: [],
    message: 'Invalid categoria: invalid. Valid values are: acqua, ambiente, reti, teleriscaldamento',
    errorCode: 'VALIDATION_ERROR'
}
```

---

## ✅ Validation Rules

### Valid Categories

- `acqua` - Servizio idrico (23 FAQs)
- `ambiente` - Raccolta rifiuti (38 FAQs)
- `reti` - Energia elettrica e gas (14 FAQs)
- `teleriscaldamento` - Teleriscaldamento (18 FAQs)

### Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Invalid or missing categoria |
| `NOT_FOUND` | Category not found (HTTP 404) |
| `HTTP_ERROR` | Server error (HTTP 5xx) |
| `CALLOUT_ERROR` | Network/timeout error |
| `UNKNOWN_ERROR` | Unexpected exception |

---

## ⚡ Performance Considerations

### API Response Time

- **Average**: 20-30 seconds (dynamic scraping with Selenium)
- **Timeout**: 120 seconds (configured in Apex)

### Best Practices

1. ✅ **Use @future or Queueable** for async processing
2. ✅ **Cache results** in Platform Cache or Custom Object
3. ✅ **Avoid in triggers** - too slow for transaction context
4. ✅ **Use in scheduled jobs** for periodic updates
5. ❌ **Don't call in loops** - respect governor limits

### Governor Limits

- **Callout limit**: 100 per transaction
- **Callout timeout**: Max 120 seconds
- **Heap size**: Response ~50-100KB per request

---

## 🔄 Scheduled Updates Example

```apex
global class IrenFaqScheduler implements Schedulable {
    global void execute(SchedulableContext ctx) {
        // Get all FAQs
        Map<String, List<Iren_Gruppo_Assistenza_Faq.Faq>> allFaqs =
            Iren_Gruppo_Assistenza_Faq.getAllFaqs();

        // Store in Custom Object or Knowledge Base
        List<Knowledge__kav> articles = new List<Knowledge__kav>();

        for (String categoria : allFaqs.keySet()) {
            for (Iren_Gruppo_Assistenza_Faq.Faq faq : allFaqs.get(categoria)) {
                Knowledge__kav article = new Knowledge__kav();
                article.Title = faq.domanda;
                article.UrlName = categoria + '-' + EncodingUtil.urlEncode(faq.domanda, 'UTF-8');
                article.Summary = faq.risposta.left(255);
                article.Description__c = faq.risposta;
                article.Category__c = categoria;
                articles.add(article);
            }
        }

        insert articles;
    }
}

// Schedule daily at 2 AM
System.schedule('Iren FAQ Daily Update', '0 0 2 * * ?', new IrenFaqScheduler());
```

---

## 🧪 Test Coverage

**8 test methods** covering:

- ✅ Successful FAQ retrieval
- ✅ Invalid category validation
- ✅ Blank category validation
- ✅ HTTP 404 handling
- ✅ HTTP 500 error handling
- ✅ Get all FAQs success
- ✅ Get all FAQs error
- ✅ Batch requests

**Coverage**: 100%

Run tests:
```bash
sf apex run test --class-names Iren_Gruppo_Assistenza_Faq_Test --code-coverage
```

---

## 🔗 Integration with Lightning Web Components

### Example LWC

```javascript
// irenFaqViewer.js
import { LightningElement, track } from 'lwc';
import getFaqs from '@salesforce/apex/Iren_Gruppo_Assistenza_Faq.getFaqsByCategory';

export default class IrenFaqViewer extends LightningElement {
    @track faqs = [];
    @track error;

    categoria = 'acqua';

    handleCategoryChange(event) {
        this.categoria = event.target.value;
        this.loadFaqs();
    }

    loadFaqs() {
        getFaqs({ requests: [{ categoria: this.categoria }] })
            .then(result => {
                if (result[0].success) {
                    this.faqs = result[0].faqs;
                    this.error = null;
                } else {
                    this.error = result[0].message;
                }
            })
            .catch(error => {
                this.error = error.body.message;
            });
    }
}
```

---

## 📚 Additional Resources

- **API Documentation**: https://sunrise-vibes-eb1a0-ec988ab80bde.herokuapp.com/
- **GitHub Repository**: https://github.com/firo/WildViolet-655443
- **Heroku App**: https://sunrise-vibes-eb1a0-ec988ab80bde.herokuapp.com/api/faq

---

## 🐛 Troubleshooting

### Error: "Unauthorized endpoint"

**Solution**: Add Remote Site Settings (see Setup section)

### Error: "Read timed out"

**Cause**: API is slow (20-30s scraping time)
**Solution**: Already configured with 120s timeout. If still timing out, use async processing.

### Error: "No HttpCalloutMock found"

**Cause**: Trying to make real callout in test context
**Solution**: Tests already use mock - verify `Test.setMock()` is called

### Can't find action in Flow Builder

**Solution**:
1. Refresh Flow Builder
2. Verify class is deployed and active
3. Check @InvocableMethod syntax is correct

---

## 👨‍💻 Support

Per domande o problemi:
- 📧 GitHub Issues: https://github.com/firo/WildViolet-655443/issues
- 📖 README principale: ../README.md

---

**Made with ❤️ for Salesforce Developers**
