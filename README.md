# AI Smart Travel Planning Assistant

A travel assistant built with **Agentic AI** and **Agentic RAG** concepts. You ask a travel question in plain English, a **Router Agent** decides which specialised agent should answer, and answers are backed by travel guide PDFs that the system searches (RAG).

It runs fully offline, with no API keys, and can be used from the **terminal** or from a **web page on localhost**.

---

## Features

- **Router Agent**: reads your question and sends it to the right worker agent
- **Itinerary Agent**: builds a day-by-day plan from the travel guides
- **Comparison Agent**: compares two or more destinations
- **Budget Agent**: estimates total trip cost with a category breakdown
- **Weather Agent**: returns a simulated seasonal weather result
- **Q&A Agent (Agentic RAG)**: searches the PDFs and shows the best matching passages with the source file and relevance score
- **Tool calling**: the weather and budget tools are logged to the console as `[TOOL CALL]`
- **Two interfaces**: command line and a simple web chat page

Supported destinations: **Paris, Goa, Tokyo, Manali**

---

## How it works

```
User question
      |
      v
 RouterAgent  -- keyword-based intent detection
      |
      +-- ItineraryAgent  --+
      +-- ComparisonAgent --+--> VectorStore (RAG over PDFs)
      +-- QAAgent ----------+
      +-- BudgetAgent  ----> BudgetEstimatorTool
      +-- WeatherAgent ----> WeatherTool
```

**RAG pipeline** (`rag_engine.py`):
1. Load travel guide PDFs from `data/pdfs/`
2. Split the text into overlapping chunks (120 words, 30-word overlap)
3. Build a TF-IDF index over all chunks
4. For a query, return the top matching chunks using cosine similarity, together with their source PDF

---

## Project structure

```
.
|-- app.py              # Web interface (Flask), runs on localhost:5000
|-- main.py             # Command-line interface (demo + interactive mode)
|-- agents.py           # RouterAgent and the 5 worker agents
|-- rag_engine.py       # PDF loading, chunking, TF-IDF search
|-- tools.py            # WeatherTool and BudgetEstimatorTool
|-- make_pdfs.py        # Generates the sample travel guide PDFs
|-- requirements.txt
`-- data/
    `-- pdfs/           # Generated travel guide PDFs
```

---

## Getting started

### 1. Requirements
- Python 3.9 or newer

### 2. Clone the repository
```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
cd YOUR-REPO-NAME
```

### 3. Create and activate a virtual environment
```bash
python -m venv venv
```
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Generate the travel guide PDFs
```bash
python make_pdfs.py
```
This creates four PDFs in `data/pdfs/`.

### 6. Run it

**Web interface (localhost):**
```bash
python app.py
```
Then open **http://localhost:5000** in your browser.

**Command line, demo mode** (runs 6 sample questions):
```bash
python main.py
```

**Command line, interactive chat:**
```bash
python main.py --interactive
```

---

## Example questions

| Question | Handled by |
|---|---|
| `Plan a 4 day itinerary for Goa` | ItineraryAgent |
| `Compare Paris and Tokyo` | ComparisonAgent |
| `Estimate a budget trip to Manali for 5 days for 2 people` | BudgetAgent |
| `What is the weather like in Tokyo in April?` | WeatherAgent |
| `What documents do I need before traveling to Paris?` | QAAgent |

Example budget result for the Manali question:

```
Budget Estimate for Manali (budget tier, 5 days, 2 traveler(s)):
  Estimated Total: $650
  Breakdown -> stay: $227.5, food: $162.5, transport: $130.0, activities: $130.0
```

---

## Screenshots

_Add screenshots of the web interface and terminal output here._

<!-- ![Web interface](screenshots/web.png) -->

---

## Known limitations

This is a learning and demo project. Be aware that:

- **Routing is rule-based.** The Router uses keyword matching, not a language model. For example, any question containing the word "cost" goes to the Budget Agent.
- **Search is keyword-based.** TF-IDF matches words, not meaning, so it is not true semantic search.
- **Weather is simulated.** Temperatures are random values within a seasonal range, not a real forecast.
- **Only four destinations are supported.** Unrecognised places such as "Japan" or "Delhi" fall back to Goa instead of showing an error.
- **Budget figures are hard-coded** per destination in `agents.py` and are not read from the PDFs.
- **Seasons assume the Northern Hemisphere.**

---

## Possible improvements

- Replace TF-IDF with embeddings (for example `sentence-transformers` with FAISS or Chroma)
- Use an LLM for routing and tool selection, and to write answers from retrieved text
- Connect a real weather API
- Read budget data from the retrieved documents
- Show a clear message for unsupported destinations
- Split PDFs by section heading instead of fixed word counts
- Add conversation memory and export of itineraries as PDF

---

## Tech stack

- Python
- [pypdf](https://pypi.org/project/pypdf/): PDF text extraction
- [scikit-learn](https://scikit-learn.org/): TF-IDF and cosine similarity
- [ReportLab](https://www.reportlab.com/): sample PDF generation
- [Flask](https://flask.palletsprojects.com/): local web interface

---

## License

Add a license of your choice (for example MIT) or remove this section.
