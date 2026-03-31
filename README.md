# Trade Opportunities API

A production-ready **FastAPI** service that analyzes Indian market sectors and returns **AI-generated trade opportunity reports**.

The system integrates **Google Gemini (LLM)** with **real-time web data** and includes **caching, rate limiting, and graceful fallback handling** to ensure reliability.

---

##  Features

| Feature             | Details                            |
| ------------------- | ---------------------------------- |
| **Core endpoint**   | `GET /analyze/{sector}`            |
| **AI analysis**     | Google Gemini (markdown output)    |
| **Web data**        | Wikipedia-based context enrichment |
| **Authentication**  | API key via header or query        |
| **Rate limiting**   | Per-key request limits             |
| **Caching**         | TTL cache (30 mins)                |
| **Fallback system** | Structured response if AI fails    |
| **Error handling**  | Clean + production-ready           |
| **Docs**            | Swagger UI (`/docs`)               |

---

##  How It Works

1. User requests a sector:

   ```
   /analyze/technology
   ```

2. System:

   * Fetches web data (Wikipedia)
   * Builds a structured prompt
   * Calls **Gemini API**

3. Response:

   * Returns **AI-generated markdown report**
   * Falls back to structured template if AI fails

---

##  Quick Start

### 1. Clone the project

```bash
git clone <your-repo-url>
cd trade_opportunities_api
```

---

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure environment variables

Create `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3-flash-preview

API_KEYS=appscrip-key-2024,reviewer-key-5678
```

 Get Gemini API key: https://aistudio.google.com/app/apikey

---

### 5. Run the server

```bash
python run.py
```

OR

```bash
uvicorn app.main:app --reload
```

---

### 6. Open API docs

```text
http://localhost:8000/docs
```

---

##  Authentication

Use API key:

### Option 1 (Query param)

```
/analyze/technology?api_key=appscrip-key-2024
```

### Option 2 (Header)

```
X-API-Key: appscrip-key-2024
```

---

##  Main Endpoint

### `GET /analyze/{sector}`

Analyze a sector and return trade insights.

---

### Example Request

```bash
curl "http://localhost:8000/analyze/technology?api_key=appscrip-key-2024"
```

---

### Example Response

```json
{
  "metadata": {
    "sector": "technology",
    "generated_at": "2026-03-31T10:13:26Z",
    "data_sources": ["Wikipedia + AI"],
    "cached": false
  },
  "summary": "AI-generated analysis for technology",
  "report": "# Sector Analysis: technology\n\n## Overview\nIndia’s technology sector...",
  "opportunities": [],
  "market_metrics": {}
}
```

---

##  Fallback System

If Gemini fails (quota / API error):

* System returns **structured fallback report**
* API never crashes
* Response remains usable

---

##  Caching

* Results cached for **30 minutes**
* Prevents repeated AI calls
* Improves performance

---

##  Rate Limiting

* Default: **5 requests per minute per API key**
* Prevents abuse

---

##  Testing (Swagger)

1. Open `/docs`
2. Click **Authorize**
3. Enter:

   ```
   appscrip-key-2024
   ```
4. Run:

   ```
   /analyze/technology
   ```

---

##  Project Structure

```
app/
├── main.py
├── core/
│   ├── config.py
│   └── security.py
├── middleware/
│   └── rate_limiter.py
├── routers/
│   └── analyze.py
├── services/
│   ├── ai_analysis.py
│   ├── web_search.py
│   └── cache.py
```

---

##  Design Highlights

* Async FastAPI architecture
* Clean separation of concerns
* External API resilience (fallback + cooldown)
* Prompt optimization for cost efficiency
* Production-style logging & error handling

---

##  Notes

* Gemini free tier has **quota limits**
* Fallback ensures system still works
* Markdown output is intentional (LLM-native format)

---

##  Conclusion

This API demonstrates:

* Real-world AI integration
* Backend system design
* Performance optimization
* Fault-tolerant architecture
