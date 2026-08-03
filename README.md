# Smart Shop Assistant

An AI-powered e-commerce assistant combining a **product recommendation engine** and **customer review sentiment analysis**, and a RAG-based chatbot, exposed through a REST API and a business-facing admin dashboard.

Built as a portfolio project to demonstrate applied ML/AI skills, full-stack development, and the ability to translate technical AI concepts into business insights.

---

## What it does

- **Recommends similar products** to customers based on product category, using cosine similarity over product embeddings (PyTorch).
- **Analyzes customer review sentiment** in Portuguese text using a pretrained multilingual transformer model (Hugging Face), independent of the star rating the customer gave.
- **Surfaces business insights** by comparing star ratings against sentiment scores per category — revealing discrepancies invisible to a raw ratings dashboard (see [Key Finding](#key-finding) below).
- Answers natural-language questions about customer reviews through a Retrieval-Augmented Generation (RAG) chatbot — semantic search over review embeddings (FAISS) combined with an LLM (Groq/Llama 3.3) to generate grounded answers.
- Serves all of the above through a FastAPI REST API, covered by an automated PyTest suite that runs on every push via GitHub Actions CI.
- Provides a Django admin dashboard for non-technical business users to browse products and category insights with search, filter, and sort.
- Provides a Next.js/React frontend — an interactive category "ledger" with a custom gap-meter visualization showing the star-vs-sentiment divergence per category at a glance.

---

## Key finding

While exploring the data, star ratings and sentiment analysis of review text told two different stories for the same category:

| Category | Avg. star rating | Avg. sentiment score (from review text) |
|---|---|---|
| `office_furniture` | 3.49 / 5 | **2.56 / 5** |

Customers rate office furniture moderately in stars, but the *language* they use in written reviews is significantly more negative — a signal invisible if you only look at star ratings. This kind of discrepancy is exactly the type of insight a business would want surfaced automatically rather than discovered by manually reading thousands of reviews.

---

## Tech stack

| Layer | Technology |
|---|---|
| Data processing | Python, Pandas |
| Recommendation engine | PyTorch (cosine similarity over one-hot category embeddings) |
| Sentiment analysis | Hugging Face Transformers (`nlptown/bert-base-multilingual-uncased-sentiment`) |
| RAG chatbot |	Sentence-Transformers (embeddings), FAISS (vector search), Groq API (Llama 3.3 70B)
| API | FastAPI, Uvicorn, Pydantic |
| Admin dashboard | Django, Django Admin |
| Testing / CI	| PyTest, GitHub Actions
| Frontend | Next.js, React, Tailwind CSS |
| Data | [Olist Brazilian E-Commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle) |
| Version control | Git / GitHub |

---

## Project structure

```
smart-shop-assistant/
├── ml/
│   ├── data/                  # CSV datasets (gitignored — see setup below)
│   └── notebooks/
│       └── 01_data_exploration.ipynb   # data cleaning, EDA, model + RAG index building
├── api/
│   ├── main.py                 # FastAPI app: recommendations, insights, chat endpoints
│   ├── test_main.py            # PyTest suite
│   ├── data/                   # processed data + FAISS index used by the API
│   └── test_data/              # small fixture dataset used only in CI
├── dashboard/
│   ├── manage.py
│   ├── config/                 # Django project settings
│   └── shop/                   # Django app: models, admin, data loader
│       ├── models.py
│       ├── admin.py
│       └── management/commands/load_data.py
├── frontend/                   # Next.js app — category ledger UI
├── .github/workflows/tests.yml # CI: runs PyTest on every push
├── requirements.txt
└── README.md
```

---

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/recommendations/{product_id}?top_n=5` | Returns top N products similar to the given product |
| `GET` | `/insights/categories` | Returns star rating + sentiment score for all product categories, sorted by sentiment |
| `GET` | `/insights/categories/{category_name}` | Returns detailed insight for a single category |
| `POST`|	`/chat	Accepts {"question": "..."}` | retrieves the 5 most relevant reviews via FAISS, and returns an LLM-generated answer grounded in them
---

## How it works

### 1. Data cleaning & exploration
The Olist dataset (orders, products, reviews) is loaded and cleaned in a Jupyter notebook. Products missing a translated category name (~1.9%) are dropped. Category names are translated from Portuguese to English via a lookup table.

### 2. Recommendation engine
Each product's category is one-hot encoded into a vector. Product vectors are converted to PyTorch tensors, and cosine similarity is computed between a target product and all others to find the closest matches — an explicit tie-breaking fix ensures a product is never recommended to itself even when multiple products share identical similarity scores.

### 3. Sentiment analysis
Review text (Portuguese) is passed through a pretrained multilingual BERT model fine-tuned for 1–5 star sentiment classification. Results are compared against the actual star rating given by the customer to surface discrepancies.

### 4. RAG chatbot

A sample of customer reviews is embedded with a multilingual sentence-transformer model and indexed with FAISS. At query time, the user's question is embedded and matched against this index to retrieve the 5 most semantically relevant reviews. These are injected as context into a prompt sent to an LLM (Groq, Llama 3.3 70B), which generates an answer grounded only in the retrieved reviews rather than relying on general knowledge.

### 5. API layer

All models are loaded once at server startup (not per-request) and served via FastAPI, following REST conventions with path parameters, query parameters, and proper HTTP error handling. Data paths are configurable via a DATA_DIR environment variable, allowing the same code to run against full local data or a small fixture dataset in CI.

### 6. Testing & CI

A PyTest suite covers the health check, recommendation lookups (including 404 handling for unknown products/categories), and the insights endpoints. GitHub Actions runs this suite automatically on every push to main, using a small committed fixture dataset so tests don't depend on the full (gitignored) data pipeline.

### 7. Admin dashboard

Django models mirror the processed CSV outputs. A custom management command (load_data) bulk-loads the data into SQLite. Django's built-in admin interface provides search, filtering, and sorting with zero custom frontend code.

### 8. Frontend

A Next.js single-page interface displays every category as a card in a "ledger," each with a custom-built gap-meter visualization plotting the star rating and sentiment score on a shared scale — making the star/sentiment divergence (the project's key finding) visible at a glance, not just in a table. Clicking a category opens a modal with full detail, fetched live from the FastAPI backend.
---

## Setup & installation

### Prerequisites
- Python 3.10+
- Node.js 18+ (for the frontend)
- The [Olist dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) downloaded and extracted to `ml/data/`
- A free Groq API key (for the chatbot endpoint)

### 1. Clone and set up the environment
```bash
git clone https://github.com/MariaGenova36/smart-shop-assistant
cd smart-shop-assistant
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Add your Groq API key

Create a .env file in the project root:

GROQ_API_KEY=your-key-here

### 3. Run the data pipeline
Open and run all cells in `ml/notebooks/01_data_exploration.ipynb`. This cleans the data, builds the recommendation and sentiment models, and exports the processed CSV files that the API and dashboard depend on.

> Note: the full sentiment analysis pass over ~41,000 reviews takes approximately 15–20 minutes depending on the user's CPU.

Copy the processed files into the API's data folder:

```bash
mkdir -p api/data
cp ml/data/products_clean.csv ml/data/category_ratings_summary.csv ml/data/category_sentiment_summary.csv ml/data/review_embeddings.index ml/data/rag_reviews.csv api/data/
```

### 3. Run the API
```bash
cd api
uvicorn main:app --reload
```
API available at `http://localhost:8000`.

### 4. Run the admin dashboard
```bash
cd dashboard
python manage.py migrate
python manage.py createsuperuser
python manage.py load_data
python manage.py runserver 8001
```
Dashboard available at `http://localhost:8001/admin`.

### 5. Run the tests
```bash
cd api
python -m pytest
```

### 6. Run the admin dashboard
```bash
cd dashboard
python manage.py migrate
python manage.py createsuperuser
python manage.py load_data
python manage.py runserver 8001
```
Dashboard available at http://localhost:8001/admin.

### 7. Run the frontend
```bash
cd frontend
npm install
npm run dev
```
Available at http://localhost:3000. Requires the API (step 4) to be running, with CORS enabled for localhost:3000.
---
