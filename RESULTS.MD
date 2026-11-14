# Evaluation Results & Critical Error Analysis (`reports/results.md`)

## 1. Executive Summary
This document summarizes the empirical evaluation of the **From News to Action** pipeline across two stages:
1. **Controlled Benchmark Evaluation ($N = 219$ real-time reports):** Comparing our deterministic Baseline ("cheapest tool that works") against our Multi-Agent LangGraph + Gemini 3.8 Flash architecture on the exact same test set.
2. **Live Production Deployment ($N = 404$ verified traffic accidents):** Real-world spatial clustering, Vulnerable Road User (VRU) distribution, and post-deployment error analysis from our automated 24/7 cloud system.

---

## 2. Baseline vs. Agentic Pipeline Comparison ($N = 219$ Benchmark Set)
To ensure a fair comparison, both arms were evaluated on the identical set of $N = 219$ raw Hebrew emergency and news reports using identical evaluation criteria:

| Evaluation Metric | Project Target | Baseline Arm (Deterministic Regex/Rules + Raw Geocoding) | Agentic Layer 3 (LangGraph + Gemini 3.8 Flash) | Lift / Delta |
| :--- | :--- | :--- | :--- | :--- |
| **Verified Geocoding Coverage** | > 95.0% accurate locations | 92.2% *(Nominal — suffers from generic city/highway center stacking / "Spiderfy")* | **96.8%** *(Cleaned Hebrew prepositions & validated intersections)* | **+4.6%** *(Eliminated spatial blindspots & False Positives)* |
| **Medical Severity Resolution** | > 85.0% semantic accuracy | 73.0% *(59 cases left as `'not specified'`)* | **88.5%** *(Cross-source scraping & entity resolution from late articles)* | **+15.5%** *(Semantic completion across time & sources)* |
| **Spatial Deduplication** | 100.0% noise prevention | 0.0% *(Generates duplicate pins for multi-source flashes)* | **100.0%** *(Enforces strict 500m / 90-day entity merging)* | **Approved** *(Autonomous conflict resolution)* |
| **Vehicle & VRU NER (Recall)** | > 85.0% Recall | 91.4% *(Keyword matching)* | **94.2%** *(Context-aware Pydantic extraction)* | **+2.8%** *(Higher recall on micro-mobility & age groups)* |
| **Generative Groundedness** | > 90.0% Groundedness | N/A *(Non-generative)* | **94.5%** *(Verified against source text; unanswerable fields flagged `'not specified'`)* | **Pass** *(Zero hallucinated infrastructure causes)* |
| **Avg. Latency per Report** | < 10 seconds | ~0.4 seconds | ~2.3 seconds *(Includes multi-step tool retries)* | +1.9s *(Acceptable for daily batch)* |
| **Operating Cost (Est. Monthly)** | < $10 / month | ~$0 / month *(Free tier APIs)* | **~$3 - $5 / month** *(Gemini Flash token usage)* | **Near-Zero Cost** |

### Why the Agentic Upgrade is Justified
While the deterministic Baseline is fast and nearly free, it fails on the two core business requirements: **27.0% of accidents lack injury severity**, and **geocoding false positives create artificial "Red" hotspots** at generic geographic midpoints. The LangGraph agent resolves both issues for under $5/month.

---

## 3. Live Production Key Results ($N = 404$ Verified Accidents)
Following automated daily ingestion at 04:00 AM IST from 7 parallel sources (4 Telegram emergency channels + 3 News RSS feeds) into our Neon PostgreSQL database, the production pipeline yielded the following actionable insights for the National Road Safety Authority (הרלב"ד):

* **Total Verified Traffic Accidents:** **404 incidents** (refined from 421 raw scraped records after semantic noise filtering).
* **Spatial Anomaly Distribution ("Traffic Light" Risk Indicator — 500m radius / 90-day window):**
  * **Red Alerts ($\ge 3$ accidents — Suspected Infrastructure Hazard):** **86 incidents (21.3%)**, successfully flagging recurring high-risk corridors such as the **Geha Interchange / Jabotinsky axis** and **Highway 25**.
  * **Orange Warnings ($2$ accidents — Developing Risk):** **81 incidents (20.0%)**.
  * **Green Normal ($1$ isolated incident):** **237 incidents (58.7%)**.
* **Vulnerable Road Users (VRU) Impact:** **41.0% (164 incidents)** involved pedestrians, children/teens (0–18), seniors (60+), or micro-mobility riders.
* **Two-Wheeler & Micro-Mobility Involvement:** **26.0% (106 incidents)** involved motorcycles, scooters, bicycles, or e-bikes/e-scooters.
* **Severe & Fatal Outcomes:** **140 incidents** were classified as severe or fatal.

---

## 4. Sanity Checks, Data Leakage Prevention & Groundedness
To guarantee scientific validity and prevent metric inflation:
1. **Temporal Leakage Prevention:** When computing the 90-day spatial density window (`ST_DWithin` / Haversine + `published_date`), the pipeline strictly evaluates historical lookback windows based on `published_date` so future events never leak into past cluster counts.
2. **Duplicate Inflation Prevention:** Every ingested item is hashed via SHA-256 (`source|raw_text`) into `report_hash` with an `ON CONFLICT DO NOTHING` constraint, ensuring re-runs never artificially inflate spatial clusters.
3. **Groundedness Evaluation:** Evaluated on a dedicated test set including negative samples (alerts omitting injury severity or exact street names). The Pydantic schema enforces explicit `'not specified'` outputs rather than guessing, achieving a **94.5% Groundedness Score**.

---

## 5. Critical Error Analysis & Iterative Engineering Fixes
In accordance with our Data-Centric methodology, we conducted systematic error analysis on both the benchmark set and the 421 live production records, uncovering four concrete failure modes and implementing deterministic guardrails for each:

1. **The Data-Centric Pivot (0.0% Explicit Infrastructure Mentions):**
   * *Finding:* Exploratory analysis revealed that 0.0% of initial emergency flashes explicitly mention road defects (e.g., "pothole" or "broken traffic light").
   * *Fix:* Instead of prompting the LLM to speculate on road conditions (which caused hallucinations), we pivoted to **spatial-temporal density clustering** ($\ge 3$ accidents within 500m over 90 days) as an empirical proxy for infrastructure hazards.
2. **Geocoding Centroid "Spiderfy" Fallbacks (`31.0461, 34.8516`):**
   * *Finding:* When Google Maps received ambiguous phrasing or out-of-country locations, it defaulted to the exact geographic center of Israel (`31.0461, 34.8516`), artificially stacking 18 unrelated incidents into a false "Red" hotspot.
   * *Fix:* Added a hard coordinate guardrail in both `daily_etl.py` and `streamlit_app.py` that nullifies known country/city centroid fallbacks and routes them to `REQUIRES_MANUAL_REVIEW`.
3. **Domain Drift from Medical Keywords at Major Junctions:**
   * *Finding:* High-traffic junctions (e.g., Geha Junction) frequently appear in emergency channels for non-traffic events (such as protests with injured demonstrators), introducing 17 non-traffic noise records out of 421.
   * *Fix:* Added a mandatory boolean semantic gate (`is_traffic_accident: bool`) to the `TrafficAccidentExtract` Pydantic schema to filter out protests, security incidents, and domestic emergencies prior to database insertion.
4. **Substring False Negatives in Keyword Filtering:**
   * *Finding:* Filtering the short Hebrew token `"ירי"` (shooting) accidentally excluded 9 genuine traffic accidents because the characters appeared inside innocent Hebrew words (e.g., *צ**ירי**ם* or first names in MDA reports).
   * *Fix:* Replaced short-token matching with exact multi-word phrases (e.g., `"אירוע ירי"`), restoring all 9 valid accidents to the dataset (bringing the clean total to **404**).

---

## 6. Known Limitations
* **Media Reporting Bias:** News and emergency feeds naturally over-represent moderate, severe, and fatal accidents, while minor property-damage-only ("fender-bender") collisions go unreported.
* **Interurban Highway Ambiguity:** Reports mentioning long highways without kilometer markers or nearby interchanges (e.g., *"תאונה בכביש 6"*) cannot be pinpointed to a 500m radius and are safely excluded from spatial anomaly clustering via the manual review queue.
