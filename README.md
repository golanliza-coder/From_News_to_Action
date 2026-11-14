
# From News to Action: A Data-Centric Agentic AI Pipeline for Real-Time Traffic Infrastructure Risk Detection

## 1. Project Overview & Team
* **Project Name:** From News to Action
* **Team Members:** 
    * **Liza Golan** - Data Scientist Student
    * **Ravit Bar-Lev** - Data Scientist Student

---

## 2. Business Problem & Target User
* **Target User:** Budget CEOs, road safety analysts, and urban infrastructure planners at the National Road Safety Authority (הרלב"ד) and the Ministry of Transport (משרד התחבורה).
* **Business Problem:** Official Central Bureau of Statistics (CBS / למ"ס) and police road accident reports are published with a 1-to-3-month delay. This delay creates critical visibility "blindspots" that hinder timely infrastructure remediation. **Empirical analysis of 407 verified incidents accumulated in our live system reveals that 41% of accidents (187 incidents) occurred within recurring "Red" high-risk clusters ($\ge 3$ accidents within a 500-meter radius over 90 days)**—active hazard hotspots that could have been flagged in real time for engineering intervention months prior to official report releases.

Empirical analysis of 373 spatially verified incidents accumulated in our live system (after filtering generic country-center fallbacks) reveals that 41.0% of accidents (153 incidents) occurred within recurring "Red" high-risk clusters (≥ 3 accidents within a 500-meter radius over 90 days)—such as the Geha Interchange / Jabotinsky corridor and Highway 25.

* **Solution:** A 24/7 automated Data-Centric Agentic AI pipeline that ingests raw Hebrew news and emergency alerts within minutes of an incident, transforming unstructured text into clean, geocoded spatial datasets. The system proactively identifies spatial anomalies ("traffic light" risk indicators) and Vulnerable Road User (VRU) trends months before official reports are published.

---

## 3. Data Description & Sources
The pipeline automatically ingests and cross-references data from **7 live parallel streams** alongside official historical benchmarks:
* **Real-Time Operational Telegram Channels (4 Sources):** MDA (מד"א), United Hatzalah (איחוד הצלה), Israel Fire & Rescue (כבאות והצלה), and ZAKA (זק"א).
* **Major News RSS Feeds (3 Sources):** Ynet, Maariv (מעריב), and Israel Hayom (ישראל היום).
* **Spatial & Navigation APIs:** Google Maps Geocoding API for converting cleaned Hebrew location strings into precise GPS coordinates.
* **Ground Truth Validation:** Official historical road accident datasets (2024–2025) from Data.gov.il (CBS / למ"ס) used for comparative benchmarking and validating alerts on known "red roads".
* **Data Scale:** Evaluated on a verified benchmark set ($N=219$ real-time reports) and continuously accumulating daily incidents autonomously (**over 407 verified incidents** active in production).
---

## 4. Methodology & Architecture

### System Pipeline Architecture
```mermaid
flowchart TD
    subgraph L1 ["LAYER 1: AUTOMATED INGESTION (Every Day 04:00 AM)"]
        A1["7 Sources: Telegram Channels & News RSS Feeds"] --> A2["GitHub Actions Scheduling Job"]
        A2 --> A3["Python Scraper (Filtered for Yesterday's Data)"]
    end
    subgraph L2 ["LAYER 2: BASELINE INGESTION & DATA-CENTRIC PIVOT"]
        A3 --> B1["Raw Text Stream (accident_reports_raw.csv)"]
        B1 --> B2["Deterministic Baseline Engine (Pydantic Schema)"]
        B2 --> B3["Initial Entity Extraction: Involved Vehicles & Demographics (VRU)"]
    end
    subgraph L3 ["LAYER 3: MULTI-AGENT AI CORE (LangGraph Framework)"]
        B3 --> C1["Router / Node Decision Loop"]
        C1 --> C2["Agent A: The Spatial Resolver Agent<br>(Cleans Hebrew Texts + Google Maps Geocoding API)"]
        C1 --> C3["Agent B: The Context Enricher Agent<br>(Cross-Source Scraping of Late Depth Articles)"]
        C2 & C3 --> C4["Spatial Density Analyzer Tool<br>(ST_DWithin: Radius 500m / 90 Days Window)"]
    end
    subgraph L4 ["LAYER 4: CLOUD STORAGE & REAL-TIME INSIGHTS"]
        C4 --> D1["Hosted PostgreSQL + PostGIS Cloud Database (Neon.tech)"]
        D1 --> D2["Streamlit Community Cloud Live Dashboard (24/7 Active URL)"]
    end
    L1 --> L2
    L2 --> L3
    L3 --> L4
```

### Core Technical Components
1. **Automated Cloud Ingestion (Layer 1):** A daily GitHub Actions cron job (04:00 AM IST / 02:00 UTC) scrapes the previous day's reports from Telegram (via Telethon `StringSession`) and news RSS feeds, preventing duplicates via an MD5 `report_hash` UPSERT mechanism.
2. **Structured Entity Extraction (Layer 2):** Uses **Gemini (3.8 Flash)** with a strict **Pydantic JSON Schema** to extract `accident_severity`, `location_raw_text`, `involved_vehicles` (including micro-mobility), and Vulnerable Road Users (`VRU` demographics: children 0–18, seniors 60+, pedestrians) while maintaining a >90% Groundedness Score.
3. **Multi-Agent AI Core (Layer 3 - LangGraph):**
   * **Agent A (The Spatial Resolver):** Cleans complex Hebrew prepositions (e.g., "סמוך ל...", "לכיוון דרום") and iteratively queries `Advanced_Geocoding_Tool` (Google Maps API) to resolve generic city/highway center guesses ("Spiderfy" clusters) into exact intersections and interchanges.
   * **Agent B (The Context Enricher):** Detects missing medical severity ("לא מצוין") in initial emergency flashes, triggers `Cross_Source_Scraping_Tool` on late-breaking news articles, and performs Entity Resolution.
   * **Spatial Density Analyzer:** Executes PostGIS `ST_DWithin` queries (500m radius, 90-day window) to flag `suspected_infrastructure_hazard = True` when $\ge 3$ accidents cluster at the same spot.
4. **Deterministic Guardrails & Fallback:** If text ambiguity persists (Information Blindspot) or the agent exceeds 3 self-correction retries, the pipeline saves the baseline JSON and flags the record as `REQUIRES_MANUAL_REVIEW` without halting execution.

---

## 5. Models Tested & Baseline Comparison
Empirical evaluation on the verified test set (**$N=219$ real-time reports**), comparing the deterministic Baseline pipeline against the Gemini-powered Agentic Layer 3:

| Evaluation Metric | Project Target | Baseline Arm (Deterministic) | Agentic Layer 3 (LangGraph + Gemini) | Lift / Delta |
| :--- | :--- | :--- | :--- | :--- |
| **Verified Geocoding Coverage** | > 95% accurate locations | 92.2% *(Nominal - generic center stacking / Spiderfy)* | **96.8%** *(Cleaned & spatially distributed coordinates)* | **+4.6%** *(Eliminated spatial blindspots & False Positives)* |
| **Medical Severity Resolution** | > 85% semantic accuracy | 73.0% *(59 cases marked 'Not Specified')* | **88.5%** *(Live cross-source article enrichment)* | **+15.5%** *(Semantic completion from depth articles)* |
| **Spatial Deduplication** | 100% noise prevention | 0.0% *(Deterministic code generates duplicates)* | **100.0%** *(Strict 500m radius rule enforced)* | **Approved** *(Autonomous conflict resolution)* |
| **Vehicle & VRU NER (Recall)** | > 85% Recall | 91.4% *(Basic extraction)* | **94.2%** *(Enhanced semantic extraction)* | **+2.8%** *(Improved VRU & micro-mobility accuracy)* |

---

## 6. Justification for Agentic / LLM Approach
* **Data-Centric Pivot:** Exploratory analysis of raw emergency alerts revealed **0.0% explicit mentions** of infrastructure faults (e.g., "potholes" or "broken streetlights") in initial flash reports. Instead of forcing the LLM to hallucinate causes, we pivoted to detecting **spatial-temporal anomalies** ($\ge 3$ accidents within 500m over 90 days) as an empirical proxy for infrastructure hazards.
* **Solving Deterministic Geocoding False Positives:** Standard geocoding APIs are overly permissive—when given complex Hebrew phrasing, they silently default to the geographic center of Israel or a highway midpoint, creating massive overlapping map spirals ("Spiderfy"). The LangGraph agent autonomously detects these generic coordinates, rewrites the Hebrew query, and validates exact junctions.
* **Resolving Information Blindspots:** Initial MDA flashes often omit injury severity (27% missing in Baseline). Only an agentic loop capable of querying subsequent news articles can merge entities across time and sources.

---

## 7. Key Results, Limitations & Conclusions
* **Results:** Reduces hazard detection latency from 30–180 days (CBS reports) to **< 24 hours** (automated daily updates at 04:00 AM). Live Streamlit dashboard delivers 3 core executive KPIs: **Traffic Light Spatial Alerts** (Red $\ge 3$, Orange $= 2$, Green $= 1$), **Two-Wheeler/Micro-Mobility Share**, and **VRU Impact Rates**.
* **Limitations:** Media coverage inherently skews toward moderate-to-fatal accidents (minor fender-benders are rarely reported in news feeds). Highly ambiguous phrasing without kilometer markers can still result in minor spatial variance, which is mitigated via the `REQUIRES_MANUAL_REVIEW` queue.
* **Conclusions:** Combining a Data-Centric Pydantic schema with a multi-agent LangGraph architecture enables transportation authorities to transition from reactive historical analysis to proactive infrastructure intervention at near-zero operating cost.

## 8. Repository Structure
```text
From_News_to_Action/
├── README.md                      # Central project documentation
├── CHARTER.md                     # Updated Project Charter & final benchmark metrics
├── daily_etl.py                   # Standalone automated daily ingestion & agentic pipeline
├── streamlit_app.py               # 24/7 live interactive executive dashboard
├── requirements.txt               # Python dependencies (langgraph, google-genai, streamlit, etc.)
├── .github/
│   └── workflows/
│       └── daily_job.yml          # GitHub Actions cron schedule (04:00 AM IST daily)
├── data/
│   ├── raw/                       # Raw scraped samples (accident_reports_raw.csv)
│   ├── processed/                 # Baseline & Agentic benchmark outputs
│   └── data_dictionary.md         # Schema definitions for Neon PostgreSQL + PostGIS
├── notebooks/
│   ├── 01_eda.ipynb               # Exploratory data analysis on N=219 reports & CBS data
│   ├── 02_baseline_pipeline.ipynb # Deterministic baseline & Spiderfy error analysis
│   └── 03_agentic_eval.ipynb      # LangGraph agent evaluation & lift benchmarking
├── src/                           # Modular scraping, geocoding, and DB utilities
├── agents/                        # LangGraph nodes, routing logic, tools, and guardrails
├── reports/
│   ├── figures/                   # Coverage, severity, vehicle NER, and map screenshots
│   └── results.md                 # Detailed benchmark comparison & error analysis
└── presentation/                  # Final 10-slide executive presentation deck
```

---

## 9. Full Execution Instructions

### Prerequisites
* Python 3.10+
* Cloud PostgreSQL database with **PostGIS** enabled (hosted on **Neon.tech**)
* API Keys & Credentials: Gemini API, Google Maps Geocoding API, and Telegram API (`API_ID`, `API_HASH`, `SESSION_STRING`)

### Setup & Installation
```bash
# Clone the repository
git clone https://github.com
cd From_News_to_Action

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration
Configure the following 6 secrets in your local `.env` file (or in **GitHub Repository Secrets** & **Streamlit Cloud Secrets** for production):
```env
DATABASE_URL="postgresql://user:password@ep-xyz.neon.tech/neondb?sslmode=require"
GEMINI_API_KEY="your_gemini_api_key"
GOOGLE_MAPS_API_KEY="your_google_maps_api_key"
TELEGRAM_API_ID="your_telegram_api_id"
TELEGRAM_API_HASH="your_telegram_api_hash"
TELEGRAM_SESSION_STRING="your_telethon_string_session"
```

### Running the Pipeline & Dashboard
```bash
# Run the daily ETL & Agentic pipeline manually (ingests yesterday's incidents into Neon)
python daily_etl.py

# Launch the live Streamlit dashboard locally
streamlit run streamlit_app.py
```
*(In production, `.github/workflows/daily_job.yml` executes `daily_etl.py` automatically every day at 04:00 AM IST, and Streamlit Community Cloud serves the live dashboard 24/7.)*

---

## 10. Estimated Monthly Operating Costs (Order of Magnitude)
The entire production stack runs on a serverless cloud architecture with near-zero operational overhead:

| Component | Provider / Tool | Monthly Usage Estimate | Estimated Cost (USD) |
| :--- | :--- | :--- | :--- |
| **LLM Entity Extraction & Agents** | Google Gemini API (Gemini 3.8 Flash) | ~300–500 daily/monthly reports | **~$2 - $5 / month** |
| **Geocoding API** | Google Maps Geocoding API | Covered under monthly free tier credit | **$0 / month** |
| **Spatial Database** | Neon.tech (PostgreSQL + PostGIS) | Serverless Free Tier | **$0 / month** |
| **Scheduled Ingestion & Dashboard** | GitHub Actions & Streamlit Community Cloud | Daily 04:00 AM cron + 24/7 hosting | **$0 / month** |
| **Total Estimated Monthly Cost** | | | **< $5 / month** |
