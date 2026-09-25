# Project Charter: From_News_to_Action [CHARTER_E_V1.md]

> **Note:** The content of this project charter is subjected to dynamic adjustments based on project progress, data findings, and milestone outcomes.

## Project Name
**From News to Action: A Data-Centric Agentic AI Pipeline for Real-Time Traffic Infrastructure Risk Detection**

---

### 1. Problem & Target User
* **Target User:** Road Safety Analyst / Data Analyst / Budget Manager at the National Road Safety Authority (NRSA / הרלב"ד) or the Ministry of Transport.
* **Quantified Pain Point:** The analyst loses **3 to 6 months** waiting for processed, official data from the Central Bureau of Statistics (CBS / למ"ס) and the police. This lag creates critical blindspots and delays the identification and mitigation of high-risk infrastructure hazards (e.g., potholes, inadequate lighting, or dangerous traffic layouts). This delay leads to an estimated **15% increase in recurrent accidents** at unaddressed hazardous locations.

---

### 2. Success Metrics & Evaluation
* **Hazard Response Latency:** Reduce the time to identify infrastructure hazards and accident-contributing factors from **90 days** (CBS publication average) to **under 24 hours** from initial media publication.
* **Data Extraction Quality (Precision & Recall):** Achieve at least **85% Precision and Recall** in structured Named Entity Recognition (Structured NER) from unstructured Hebrew news texts on a validated evaluation dataset (Eval-Set).
* **Groundedness Score:** Maintain a Groundedness Score of **at least 90%** using a dedicated evaluation framework to prevent spatial or situational hallucinations regarding accident locations and causes.

---

### 3. Data Sources & Fallback Plan
* **Primary Data Source:** **1,500 real-time text reports** ingested from official Telegram channels (MADA, United Hatzalah, Fire and Rescue Services, ZAKA) and online news flashes (ynet, Hamal). Tested and validated via Python APIs (`Telethon` / `BeautifulSoup`).
* **Fallback Plan (In One Sentence):** If live monitoring streams are blocked, the system will immediately pivot to processing a static historical dataset of 2,000 scraped accident news articles from ynet and CBS covering the past 12 months, stored in a shared CSV/Google Drive repository.

---

### 4. System Architecture Diagram

Below is the system architecture divided into 4 core functional layers:

```mermaid
flowchart TD
    subgraph L1 ["LAYER 1: DATA INGESTION"]
        A1["Sources: Hamal / Telegram / ynet / Ihud Hazala / Zaka / Fire and Rescue Services"] --> A2["Python Ingestion Script"]
    end

    subgraph L2 ["LAYER 2: LLM EXTRACTION & STRUCTURING (DCAI Engine)"]
        B1["Raw Text Stream"] --> B2["LLM: GPT-4o-mini / Llama 3.3 + Pydantic JSON Schema"]
        B2 --> B3["Structured Extraction: severity, vehicle_types, human/infra factors"]
    end

    subgraph L3 ["LAYER 3: AGENTIC AI CORE, GEOCODING & CONFLICT RESOLUTION"]
        C1["Verbal Location"] --> C2["OpenStreetMap API Tool (Lat, Lon Conversion)"]
        C2 --> C3["Spatial Deduplication Engine: Radius 500m + Time Window 1h"]
        C3 --> C4["Agent Reasoning & Guardrails Engine"]
    end

    subgraph L4 ["LAYER 4: STORAGE & INSIGHTS"]
        D1["PostgreSQL + PostGIS Database"] --> D2["Streamlit / PowerBI Live Risk Heatmap Dashboard"]
    end

    L1 --> L2
    L2 --> L3
    L3 --> L4
   ```

### 5. Agent Specification
* **What does the agent decide that standard code cannot?**
  The agent autonomously executes **Spatial Conflict Resolution & Contextual Enrichment**. When handling parallel or conflicting media reports regarding the same incident (e.g., a ynet article reporting an "accident on Route 4 near Geha" vs. a Telegram update specifying "accident near Givat Shmuel Interchange"), deterministic code fails or generates duplicate entries. The agent applies contextual reasoning, cross-references temporal windows and spatial radii, and resolves the exact coordinates and incident severity.
* **Agent Tools:**
  1. `Geocoding_Tool`: Interfaces with OpenStreetMap / Nominatim API to convert verbal Hebrew location descriptions into precise latitude/longitude coordinates.
  2. `Spatial_Deduplication_Tool`: Executes spatial queries against PostgreSQL/PostGIS to detect existing records within a 500-meter radius and a 1-hour time window.
  3. `Weather_API_Tool`: Fetches environmental, lighting, and weather conditions at the verified location and time of the incident.
* **Fallback & Guardrails:**
  If the agent exceeds 3 self-correction iterations (Max Retries) or detects an external API failure, a **Deterministic Guardrail** preserves the baseline extracted JSON schema, tags the database entry as `Requires_Manual_Review`, and continues pipeline execution. **The core data pipeline functions fully and delivers structured output even without the agentic layer.**

---

### 6. Risks & Scope Cut
* **Risk 1 (Location Hallucinations in LLM):** The model generates non-existent coordinates or addresses.
  * *Mitigation:* Enforce strict output validation using Pydantic Schemas and mandatory verification against an external geocoding API.
* **Risk 2 (API Blocking / Scraping Anti-Bot Measures):** Access restrictions on Telegram or HTML structural changes on news platforms.
  * *Mitigation:* Automatic fallback to processing a pre-collected static dataset of 2,000 scraped accident articles stored in `data/raw/`.
* **Risk 3 (API Cost Overruns & High Latency):** Excessive API calls to high-cost LLM endpoints.
  * *Mitigation:* Deployment of fast, lightweight models (Llama-3.3-70B via Groq / GPT-4o-mini) and capping self-correction retries to a maximum of 2 iterations.
* **Scope Cut Statement:** *"If only two weeks remain before final submission, we will drop the Streamlit dashboard and weather data enrichment, delivering a fully operational pipeline that outputs an agent-verified PostgreSQL database / CSV file."*

---

### 7. Milestones & Team Roles

#### Team Roles & Responsibilities
> **Note:** Team role allocations are **dynamic and will adapt flexibly** according to development velocity, workload distribution, and emerging technical priorities across project components.

**Core Project Domains & Shared Leadership Responsibilities:**
1. **Data Ingestion & Pipeline:** Development of collection scripts (Telegram API / Scraping) and data ingestion pipelines.
2. **Agentic Architecture & Tools:** Agent design (LangGraph), implementation of the self-correction loop, and integration of external tools (Geocoding / DB Search).
3. **Guardrails & Fallbacks:** Implementation of deterministic fallback mechanisms and error-handling guardrails.
4. **Prompt Engineering & Structured Schema:** Prompt optimization and enforcement of Pydantic JSON schemas.
5. **Evaluation Set & Benchmarking:** Curation of the test evaluation set (Eval-Set), measuring Precision/Recall, and evaluating Groundedness scores.
6. **Baseline Engine:** Construction of the non-agentic baseline system for performance comparison.
7. **Database & Storage Management:** Setup and maintenance of the spatial database (PostgreSQL + PostGIS).
8. **Product, Documentation & Dashboard:** Authorship of the Project Charter, central repository README, and development of the Streamlit dashboard.
  

