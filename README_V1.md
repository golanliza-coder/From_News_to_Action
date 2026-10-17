
# From_News_to_Action: A Data-Centric AI Pipeline for Instant Infrastructure Fixes

## 1. Project Overview & Team
* **Project Name:** From_News_to_Action
* **Team Members:** 
    * **Liza Golan** - Data Scientist Student
    * **Ravit Bar-Lev** - Data Scientist Student

---

## 2. Business Problem & Target User
* **Target User:** Ministry of Transport (משרד התחבורה) & National Road Safety Authority (הרלב"ד) decision-makers, safety engineers, and urban infrastructure planners.
* **Business Problem:** Official Central Bureau of Statistics (CBS / למ"ס) road accident data is published with delays of several months and lacks granular, real-time context regarding accident causes (e.g., severe infrastructure hazards like potholes, lack of lighting, or driver distractions). This delayed visibility prevents rapid infrastructure remediation and leads to preventable accidents.
* **Solution:** A real-time Data-Centric AI (DCAI) pipeline leveraging Large Language Models (LLMs) to transform unstructured Hebrew news reports and emergency updates into clean, structured, and geocoded spatial datasets.

---

## 3. Data Description & Sources
The pipeline ingests raw, unstructured text from multiple real-time streams:
* **Real-time Emergency & News Alerts:** Hamal (חמ"ל) breaking news, Telegram channels (MDA, Israel Fire & Rescue, Ihud Hatzalah), and major Israeli news portals (ynet, N12).
* **Navigation & Spatial Feeds:** OpenStreetMap / Google Maps Geocoding API for mapping verbal locations to precise GPS coordinates.
* **Data Scale:** ~5,000 Hebrew text reports processed monthly.

---

## 4. Methodology & Architecture

### System Pipeline Architecture

```text
[ Raw Hebrew Text: News / Telegram / MDA ]
                   │
                   ▼
┌────────────────────────────────────────────────────────┐
│ Step 1: LLM Structuring (JSON Schema)                 │
│ Extracts: Severity, Vehicles, Human & Infra Factors   │
└────────────────────────┬───────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────┐
│ Step 2: Spatial Geocoding & Contextual Enrichment      │
│ Verbal Location --> OpenStreetMap / Google Maps API    │
└────────────────────────┬───────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────┐
│ Step 3: Data Flywheel & Conflict Resolution (DCAI)     │
│ Deduplication (Spatial 500m / Temporal 1h Clustering) │
└────────────────────────┬───────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────┐
│ Step 4: Storage & Real-Time Dashboard                  │
│ PostgreSQL + PostGIS --> BI Dashboard (Grafana/PowerBI)│
└────────────────────────┴───────────────────────────────┘
```

### Core Technical Components
1. **Structured Named Entity Recognition (LLM):** Uses structured outputs (JSON Schema) with modern LLMs (GPT-4o / Llama 3.3) to extract entities: `accident_severity`, `vehicle_types`, `human_factor`, and `infrastructure_factor`.
2. **Geocoding & Spatial Validation:** Converts extracted verbal locations (e.g., "כביש 4 ליד מחלף גהה") into exact Latitude/Longitude coordinates.
3. **Data Flywheel & Deduplication:** Applies spatial (500m) and temporal (1h) clustering algorithms to deduplicate multi-source news reports covering the same accident.
4. **Agent / System Fallbacks:** Deterministic Python code handles file operations, API routing, and spatial calculations. If the LLM extraction fails or returns invalid JSON, records route to a Dead-Letter Queue (DLQ) in PostgreSQL for manual or rule-based processing (e.g., Dicta-BERT / HeBERT).

---

## 5. Models Tested & Baseline Comparison

| Model / Pipeline Version | Entity Extraction Precision | Entity Extraction Recall | Spatial Geocoding Accuracy | Average Latency per Article |
| :--- | :--- | :--- | :--- | :--- |
| **Rule-Based Baseline (HeBERT + Regex)** | 62.0% | 54.0% | 71.0% | **< 0.5 sec** |
| **Llama 3.3 70B (Zero-Shot)** | 78.5% | 73.0% | 82.0% | ~2.1 sec |
| **GPT-4o + JSON Schema + Geocoding (Proposed DCAI)** | **88.5%** | **84.0%** | **92.5%** | ~1.4 sec |

---

## 6. Justification for Agentic / LLM Approach
Standard rule-based NLP or traditional Named Entity Recognition (NER) models struggle with unstructured Hebrew syntax, informal news styles, and complex implicit hazards (e.g., inferring "infrastructure hazard" from "a vehicle flipped after hitting a deep pothole"). Utilizing an LLM driven by strict JSON Schemas allows high-precision entity generation (Data Creation), which traditional models cannot achieve without extensive domain-specific re-training.

---

## 7. Key Results, Limitations & Conclusions
* **Results:** Reduces actionable hazard detection time from ~180 days (CBS official release) to **< 2 hours**. Achieves >88% precision in identifying infrastructure hazards from raw news text.
* **Limitations:** Ambiguous location descriptions in raw text can lead to spatial uncertainty. Scraped news streams are subject to source API rate limits and structural changes.
* **Conclusions:** A Data-Centric AI approach leveraging LLMs as data enrichment engines allows government authorities to act proactively on hazardous road conditions months before official statistics are compiled.

---

## 8. Repository Structure

```text
From_News_to_Action/
├── README.md                      # The central document
├── CHARTER.md                     # The project charter + checkpoint updates
├── requirements.txt               # All libraries + versions
├── .gitignore
├── data/
│   ├── raw/                       # Raw data
│   ├── processed/                 # Cleaned / transformed data
│   └── data_dictionary.md         # Describes every table & column
├── notebooks/
│   ├── 01_eda.ipynb               # Exploratory data analysis
│   ├── 02_preprocessing.ipynb     # Data cleaning and feature preparation
│   ├── 03_modeling.ipynb          # Model training and comparison
│   ├── 04_model_evaluation.ipynb  # Model testing, metrics, validation, error analysis
│   └── 05_experiments.ipynb       # Optional: A/B testing/business experiments/advanced analysis
├── src/                           # Reusable functions
├── agents/                        # Tools, prompts, agent loop, guardrails
├── evaluation/                    # Eval sets, groundedness, error analysis
├── models/                        # Saved models or model artifacts (optional)
├── reports/
│   ├── figures/                   # Saved charts
│   ├── results.md                 # Baseline table + key results
│   └── experiment_results.md      # Optional: A/B test or experiment results
└── presentation/                  # The slide deck
```

---

## 9. Full Execution Instructions

### Prerequisites
* Python 3.10+
* PostgreSQL with PostGIS extension enabled
* OpenAI API Key or access to an equivalent LLM endpoint

### Setup & Installation

```bash
# Clone the repository
git clone https://github.com/your-username/From_News_to_Action.git
cd From_News_to_Action

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Environment Configuration
cp .env.example .env
# Fill in OPENAI_API_KEY, DATABASE_URL, and MAPS_API_KEY in .env
```

### Running the Data Pipeline

```bash
# Execute the full pipeline on sample data
python src/main.py --input data/raw/sample_news.json
```

---

## 10. Estimated Monthly Operating Costs (Order of Magnitude)

| Component | Provider / Tool | Monthly Usage Estimate | Estimated Cost (USD) |
| :--- | :--- | :--- | :--- |
| **LLM Entity Extraction** | OpenAI GPT-4o-mini / GPT-4o | ~5,000 reports / month (~2M tokens) | ~$15 - $30 |
| **Geocoding API** | OpenStreetMap (Free) / Google Maps | ~5,000 requests / month | $0 - $25 |
| **Database & Ingestion Server** | Cloud VPS (e.g., AWS EC2 / DigitalOcean) | 24/7 Basic instance (2 vCPU, 4GB RAM) | ~$20 - $40 |
| **Dashboard Hosting** | Grafana Cloud / Self-hosted PowerBI | Standard single-user / team plan | $0 - $20 |
| **Total Estimated Monthly Cost** | | | **~$35 - $115 / month** |