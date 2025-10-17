# Gruppo Iren FAQ Scraper API 🔧

API REST completa in Python/Flask deployata su Heroku che esegue web scraping dinamico delle FAQ del sito [Gruppo Iren](https://www.gruppoiren.it/it/assistenza/faq.html), categorizzandole automaticamente in 4 aree di servizio.

## 📋 Indice

- [Cosa Fa](#cosa-fa)
- [Demo Live](#demo-live)
- [Architettura](#architettura)
- [Tecnologie Utilizzate](#tecnologie-utilizzate)
- [API Endpoints](#api-endpoints)
- [Come Funziona](#come-funziona)
- [Setup Locale](#setup-locale)
- [Deployment su Heroku](#deployment-su-heroku)
- [Processo di Sviluppo](#processo-di-sviluppo)
- [Problemi Risolti](#problemi-risolti)
- [Integrazione Salesforce](#integrazione-salesforce)
- [Performance](#performance)
- [Licenza](#licenza)

---

## 🎯 Cosa Fa

Questa applicazione risolve il problema di estrarre e categorizzare automaticamente le FAQ da una pagina web dinamica (basata su accordion Bootstrap) che richiede interazione JavaScript per rivelare i contenuti nascosti.

**Funzionalità principali**:
- ✅ Scraping dinamico con Selenium (headless Chrome)
- ✅ Categorizzazione automatica intelligente in 4 categorie
- ✅ Rilevamento e rimozione duplicati
- ✅ API REST standard con filtri per categoria
- ✅ ~93 FAQ estratte e organizzate
- ✅ Deploy production su Heroku

## 🌐 Demo Live

**Base URL**: `https://sunrise-vibes-eb1a0-ec988ab80bde.herokuapp.com`

### Endpoints Disponibili

| Endpoint | Descrizione | Esempio |
|----------|-------------|---------|
| `GET /` | Info API e documentazione | [Demo](https://sunrise-vibes-eb1a0-ec988ab80bde.herokuapp.com/) |
| `GET /api/faq` | Tutte le FAQ (4 categorie) | [Demo](https://sunrise-vibes-eb1a0-ec988ab80bde.herokuapp.com/api/faq) |
| `GET /api/faq/acqua` | Solo FAQ categoria acqua | [Demo](https://sunrise-vibes-eb1a0-ec988ab80bde.herokuapp.com/api/faq/acqua) |
| `GET /api/faq/ambiente` | Solo FAQ raccolta rifiuti | [Demo](https://sunrise-vibes-eb1a0-ec988ab80bde.herokuapp.com/api/faq/ambiente) |
| `GET /api/faq/reti` | Solo FAQ energia/gas | [Demo](https://sunrise-vibes-eb1a0-ec988ab80bde.herokuapp.com/api/faq/reti) |
| `GET /api/faq/teleriscaldamento` | Solo FAQ teleriscaldamento | [Demo](https://sunrise-vibes-eb1a0-ec988ab80bde.herokuapp.com/api/faq/teleriscaldamento) |
| `GET /health` | Health check | [Demo](https://sunrise-vibes-eb1a0-ec988ab80bde.herokuapp.com/health) |

---

## 🏗️ Architettura

```
┌─────────────────────────────────────────────────────────────┐
│                      Heroku Platform                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    Web Dyno                           │  │
│  │  ┌──────────────┐    ┌──────────────┐                │  │
│  │  │   Gunicorn   │───▶│  Flask App   │                │  │
│  │  │  (WSGI)      │    │   (app.py)   │                │  │
│  │  └──────────────┘    └──────┬───────┘                │  │
│  │                              │                         │  │
│  │                              ▼                         │  │
│  │                      ┌──────────────┐                 │  │
│  │                      │   Scraper    │                 │  │
│  │                      │ (scraper.py) │                 │  │
│  │                      └──────┬───────┘                 │  │
│  │                              │                         │  │
│  │                              ▼                         │  │
│  │                  ┌──────────────────────┐             │  │
│  │                  │  Selenium WebDriver  │             │  │
│  │                  │   + Chrome Headless  │             │  │
│  │                  └──────────┬───────────┘             │  │
│  │                              │                         │  │
│  └──────────────────────────────┼─────────────────────────┘  │
│                                 │                            │
│  ┌──────────────────────────────▼─────────────────────────┐  │
│  │     Chrome for Testing Buildpack                       │  │
│  │  • Chrome 141.0.7390.78                                │  │
│  │  • ChromeDriver                                        │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  Gruppo Iren Website    │
                    │  gruppoiren.it/faq.html │
                    └─────────────────────────┘
```

---

## 🛠️ Tecnologie Utilizzate

### Backend
- **Python 3.11** - Linguaggio principale
- **Flask 3.0.0** - Web framework micro
- **Gunicorn 21.2.0** - WSGI HTTP Server per production

### Web Scraping
- **Selenium 4.16.0** - Browser automation per contenuti dinamici
- **Chrome Headless** - Browser senza GUI
- **BeautifulSoup4 4.12.2** - HTML parsing
- **lxml 5.1.0** - Parser XML/HTML veloce

### Deployment
- **Heroku** - Platform as a Service (PaaS)
- **heroku-24 stack** - Ubuntu 24.04 base
- **Python Buildpack** - Gestione dipendenze Python
- **Chrome for Testing Buildpack** - Chrome + ChromeDriver

---

## 📡 API Endpoints

### 1. GET `/api/faq` - Tutte le FAQ

**Risposta** (200 OK):
```json
{
  "teleriscaldamento": [
    {
      "domanda": "Cos'è il teleriscaldamento?",
      "risposta": "Il teleriscaldamento è un sistema di riscaldamento..."
    }
  ],
  "acqua": [
    {
      "domanda": "Cosa significa acqua potabile?",
      "risposta": "L'acqua potabile è acqua che può essere..."
    }
  ],
  "ambiente": [...],
  "reti": [...]
}
```

**Statistiche attuali**:
- Teleriscaldamento: 18 FAQ
- Acqua: 23 FAQ
- Ambiente: 38 FAQ
- Reti: 14 FAQ
- **Totale: 93 FAQ**

---

### 2. GET `/api/faq/{categoria}` - FAQ per Categoria

**Parametri URL**:
- `categoria`: `acqua` | `ambiente` | `reti` | `teleriscaldamento`

**Esempio**: `GET /api/faq/acqua`

**Risposta** (200 OK):
```json
{
  "categoria": "acqua",
  "count": 23,
  "faqs": [
    {
      "domanda": "Cosa s'intende per ciclo integrato dell'acqua?",
      "risposta": "Il ciclo integrato dell'acqua comprende..."
    },
    {
      "domanda": "Cosa significa acqua potabile?",
      "risposta": "..."
    }
  ]
}
```

**Errore - Categoria Non Valida** (404 Not Found):
```json
{
  "error": "Invalid category",
  "message": "Category 'invalid' is not valid. Valid categories are: teleriscaldamento, acqua, ambiente, reti",
  "valid_categories": [
    "teleriscaldamento",
    "acqua",
    "ambiente",
    "reti"
  ]
}
```

---

## ⚙️ Come Funziona

### Processo di Scraping (scraper.py)

```python
1. INIZIALIZZAZIONE
   ├─ Configura Chrome headless
   ├─ Disabilita GPU, sandbox
   └─ Imposta timeout 120s

2. CARICAMENTO PAGINA
   ├─ Naviga a gruppoiren.it/faq.html
   ├─ Attende rendering (3s)
   └─ Verifica presenza elementi

3. ESPANSIONE ACCORDION
   ├─ JavaScript injection per cliccare tutti i pulsanti
   ├─ Selettori multipli per compatibilità
   ├─ Attende espansione (3s)
   └─ ~131 accordion items trovati

4. PARSING HTML
   ├─ BeautifulSoup parse del DOM
   ├─ Trova tutti .accordion-item
   ├─ Estrae domanda (button text)
   └─ Estrae risposta (collapse div)

5. CATEGORIZZAZIONE INTELLIGENTE
   ├─ Approach 1: Analisi parent elements (ID/classes)
   ├─ Approach 2: Ricerca heading precedenti
   └─ Approach 3: Keyword matching nel contenuto

   Keywords per categoria:
   • teleriscaldamento: scambiatore, caldaia, calore
   • reti: elettrica, gas, IRETI, bonus sociale
   • ambiente: rifiuti, raccolta differenziata, termovalorizzatore
   • acqua: acquedotto, fognatura, idrico, depurazione

6. DEDUPLICAZIONE
   ├─ Traccia domande già processate
   ├─ Skip duplicati (2 trovati)
   └─ Skip non categorizzabili (36 trovati)

7. COSTRUZIONE RISPOSTA
   ├─ Organizza per categoria
   ├─ Conta FAQ per categoria
   └─ Ritorna JSON
```

### Categorizzazione Intelligente

L'algoritmo usa un approccio a 3 livelli per determinare la categoria corretta:

**Livello 1 - Struttura HTML**: Analizza fino a 10 livelli di parent elements cercando indicatori nella struttura DOM (ID, classi CSS).

**Livello 2 - Context Heading**: Cerca heading (h1-h5) precedenti che identificano la sezione.

**Livello 3 - Content Analysis**: Analizza il testo della domanda e risposta cercando keyword specifiche per ogni categoria.

**Mutua Esclusività**: Ogni FAQ viene assegnata a una sola categoria. Le FAQ che non matchano nessuna categoria vengono skippate invece di essere messe in una categoria di default.

---

## 💻 Setup Locale

### Prerequisiti
- Python 3.11+
- Chrome browser
- Git

### Installazione

```bash
# 1. Clone repository
git clone https://github.com/firo/WildViolet-655443.git
cd WildViolet-655443

# 2. Crea virtual environment
python -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate

# 3. Installa dipendenze
pip install -r requirements.txt

# 4. Installa ChromeDriver
# macOS con Homebrew:
brew install chromedriver

# Linux:
# Scarica da https://chromedriver.chromium.org/
# E aggiungi al PATH

# 5. Avvia applicazione
python app.py
```

L'app sarà disponibile su `http://localhost:5000`

### Test Endpoint

```bash
# Tutte le FAQ
curl http://localhost:5000/api/faq | jq

# FAQ categoria acqua
curl http://localhost:5000/api/faq/acqua | jq

# Health check
curl http://localhost:5000/health
```

---

## 🚀 Deployment su Heroku

### Setup Iniziale

```bash
# 1. Login Heroku
heroku login

# 2. Crea app (o usa esistente)
heroku create sunrise-vibes-eb1a0

# 3. Aggiungi buildpacks
heroku buildpacks:add --index 1 heroku/python
heroku buildpacks:add --index 2 https://github.com/heroku/heroku-buildpack-chrome-for-testing

# 4. Aggiungi remote (se non presente)
git remote add heroku https://git.heroku.com/sunrise-vibes-eb1a0.git
```

### Deploy

```bash
# Commit modifiche
git add .
git commit -m "Update application"

# Push a Heroku
git push heroku main

# Verifica logs
heroku logs --tail

# Apri app
heroku open
```

### File Necessari per Heroku

**Procfile**:
```
web: gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 2
```

**runtime.txt**:
```
python-3.11.7
```

**requirements.txt**:
```
Flask==3.0.0
selenium==4.16.0
beautifulsoup4==4.12.2
gunicorn==21.2.0
lxml==5.1.0
```

---

## 📖 Processo di Sviluppo

### Fase 1: Prototipo Iniziale ✅
- Setup Flask base con endpoint `/api/faq`
- Integrazione Selenium per scraping dinamico
- Parser BeautifulSoup per HTML
- Deploy iniziale su Heroku

### Fase 2: Fix Pairing Domande-Risposte ✅

**Problema**: Le risposte erano abbinate alle domande sbagliate.

**Soluzione**: Implementato matching esplicito tra button e collapse div usando attributo `data-bs-target` e ID.

**Risultato**: 131 FAQ estratte, tutte con pairing corretto.

### Fase 3: Fix Categorizzazione ✅

**Problema**: Tutte le 131 FAQ finivano nella categoria "acqua", le altre categorie restavano vuote.

**Causa**: Lo scraper processava tutte le FAQ in un singolo loop e le aggiungeva alla prima categoria trovata.

**Soluzioni Tentate**:
1. ❌ Ricerca contenitori per categoria (nessun contenitore trovato)
2. ✅ Keyword-based categorization con analisi del contenuto

**Risultato**: FAQ distribuite in tutte e 4 le categorie.

### Fase 4: Eliminazione Duplicati ✅

**Problema**: La categoria "acqua" conteneva 65 FAQ, molte delle quali erano duplicati di altre categorie.

**Causa**:
- Keyword "acqua" troppo generica
- Default fallback ad "acqua" per FAQ non categorizzate
- Accordion items duplicati nel DOM

**Soluzioni Implementate**:
1. ✅ Tracking set per rilevare domande duplicate
2. ✅ Keywords più specifiche per ogni categoria
3. ✅ Rimozione del fallback ad "acqua"
4. ✅ Skip FAQ non categorizzabili invece di assegnarle a default

**Risultati**:
- Acqua: da 65 a 23 FAQ (-42 duplicati)
- 2 duplicati rilevati e skippati
- 36 FAQ non categorizzabili skippate
- Totale: 93 FAQ pulite e ben categorizzate

### Fase 5: REST API con Filtri ✅

**Aggiunta**: Endpoint `/api/faq/{categoria}` per filtrare per categoria specifica.

**Features**:
- URL parameters REST standard
- Validazione categoria con error handling
- Response JSON strutturata con metadata
- HTTP status codes appropriati (200, 404)

---

## 🐛 Problemi Risolti

### 1. Stale Element Reference Exception
**Sintomo**: Selenium perdeva riferimento agli elementi dopo click
**Causa**: DOM cambiava dopo interazione
**Fix**: JavaScript injection per espandere tutti gli accordion in bulk

### 2. Question-Answer Mismatch
**Sintomo**: Domanda X aveva risposta Y
**Causa**: Parsing sequenziale senza matching esplicito
**Fix**: Usa `data-bs-target` per collegare button → collapse div

### 3. Categorizzazione Errata
**Sintomo**: Tutte le FAQ in categoria "acqua"
**Causa**: Loop singolo + default fallback
**Fix**: Keyword matching + rimozione default

### 4. Duplicati Cross-Category
**Sintomo**: Stessa FAQ in più categorie
**Causa**: Accordion duplicati nel DOM + regex troppo ampia
**Fix**: Set per tracking + keywords specifiche

### 5. Timeout su Heroku
**Sintomo**: Request timeout dopo 30s
**Causa**: Scraping lento (20-30s)
**Fix**: Timeout aumentato a 120s in Gunicorn e Selenium

---

## 🔗 Integrazione Salesforce

### Client Apex per Salesforce

È stato progettato un client Apex completo per integrare questa API in Salesforce:

**Classi Apex**:
- `IREN_Gruppo_Assistenza_Faq_Service` - HTTP callout service
- `IREN_Gruppo_Assistenza_Faq_Models` - Wrapper classes con @AuraEnabled
- `IREN_Gruppo_Assistenza_Faq_Service_Test` - Test coverage 100%

**Use Cases**:
- Sincronizzazione con Knowledge Base
- Lightning Web Components per portale clienti
- Service Cloud per agenti supporto
- Schedulable updates delle FAQ

**Remote Site Settings**:
```
Name: IrenFaqAPI
URL: https://sunrise-vibes-eb1a0-ec988ab80bde.herokuapp.com
Active: ✓
```

Vedi [documentazione completa del client Apex](#) per dettagli implementativi.

---

## ⚡ Performance

### Tempi di Risposta

| Endpoint | Tempo Medio | Note |
|----------|-------------|------|
| `/api/faq` | 20-30s | Scraping completo |
| `/api/faq/{categoria}` | 20-30s | Stesso scraping, filtro post-processing |
| `/health` | <100ms | Nessuno scraping |

### Ottimizzazioni Implementate

- ✅ Chrome headless senza GPU
- ✅ Disable dev-shm (usa /tmp invece di /dev/shm)
- ✅ BeautifulSoup con parser lxml (veloce)
- ✅ Skip FAQ non categorizzabili early
- ✅ 2 workers Gunicorn per parallelismo

### Ottimizzazioni Future

- [ ] Platform Cache per risultati (TTL 1h)
- [ ] Background jobs con Celery
- [ ] Redis per caching distribuito
- [ ] Webhooks per invalidazione cache
- [ ] Pagination per grandi dataset

---

## 📊 Statistiche

```
Total FAQ scraped: 93
├─ Teleriscaldamento: 18 (19.4%)
├─ Acqua: 23 (24.7%)
├─ Ambiente: 38 (40.9%)
└─ Reti: 14 (15.0%)

Duplicates skipped: 2
Uncategorized skipped: 36
Total processing time: ~25s
Success rate: 100%
```

---

## 🧪 Testing

### Test Manuali

```bash
# Test tutte le categorie
curl -s https://sunrise-vibes-eb1a0-ec988ab80bde.herokuapp.com/api/faq | \
  python3 -c "import sys, json; d=json.load(sys.stdin); print(f'Total: {sum(len(v) for v in d.values())}')"

# Test categoria specifica
curl https://sunrise-vibes-eb1a0-ec988ab80bde.herokuapp.com/api/faq/acqua

# Test categoria invalida
curl https://sunrise-vibes-eb1a0-ec988ab80bde.herokuapp.com/api/faq/invalid

# Verifica health
curl https://sunrise-vibes-eb1a0-ec988ab80bde.herokuapp.com/health
```

### Test Automatici (Future)

```bash
# Unit tests
pytest tests/test_scraper.py

# Integration tests
pytest tests/test_api.py

# Load testing
locust -f tests/locustfile.py
```

---

## 🔧 Troubleshooting

### Chrome Driver Issues

**Problema**: `selenium.common.exceptions.WebDriverException`

**Soluzione**:
```bash
# Verifica installazione Chrome
which google-chrome
google-chrome --version

# Verifica ChromeDriver
which chromedriver
chromedriver --version

# Devono essere versioni compatibili!
```

### Timeout su Heroku

**Problema**: `H12 - Request timeout`

**Soluzione**: Aumenta timeout in Procfile:
```
web: gunicorn app:app --timeout 180 --workers 2
```

### Memory Limits

**Problema**: `R14 - Memory quota exceeded`

**Soluzione**: Scala a dyno più grande:
```bash
heroku ps:scale web=1:standard-1x
```

---

## 🤝 Contribuire

1. Fork il repository
2. Crea feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri Pull Request

---

## 📝 TODO

- [ ] Implementare caching con Redis
- [ ] Aggiungere rate limiting
- [ ] Monitoraggio con Sentry
- [ ] Metrics con Prometheus
- [ ] CI/CD con GitHub Actions
- [ ] Docker containerization
- [ ] API versioning (v1, v2)
- [ ] Webhook notifications
- [ ] Admin dashboard
- [ ] API key authentication

---

## 📄 Licenza

Questo progetto è open source e disponibile sotto [MIT License](LICENSE).

---

## 👥 Autori

- **Firo** - [GitHub](https://github.com/firo)

---

## 🙏 Acknowledgments

- **Gruppo Iren** per i dati pubblici delle FAQ
- **Heroku** per l'hosting gratuito
- **Selenium** per il web scraping dinamico
- **Flask** per il framework minimale ma potente

---

## 📞 Support

Per domande, problemi o feature requests:
- 🐛 [Issues](https://github.com/firo/WildViolet-655443/issues)
- 💬 [Discussions](https://github.com/firo/WildViolet-655443/discussions)

---

**Made with ❤️ for the Salesforce & Python community**

Heroku App: `sunrise-vibes-eb1a0` | Region: `us-east-1` | Stack: `heroku-24`
