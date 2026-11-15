# Layer 3: Multi-Agent AI Core (`agents/`)

## 1. Justification: Why an Agent and Not a Deterministic Script?
In our baseline evaluation ($N=219$ real-time reports), deterministic rules and single-pass LLM calls failed on two critical operational dimensions:
1. **Geocoding False Positives ("Spiderfy" Effect):** Standard geocoding APIs are overly permissive. When fed raw Hebrew emergency phrasing (e.g., *"כביש 4 סמוך למחלף גהה לכיוון דרום"*), Google Maps silently defaults to generic city or country centroids (`31.0461, 34.8516`), stacking dozens of unrelated accidents into false "Red" hotspots. A static script cannot judge whether a returned coordinate is a genuine junction or a generic fallback, nor can it iteratively rewrite Hebrew prepositions until a valid intersection is resolved.
2. **Cross-Source Information Blindspots:** **27.0% (59/219)** of initial emergency flashes omit medical injury severity (`'not specified'`). A deterministic script processes each row in isolation; only an autonomous agent can detect missing severity, query follow-up news articles published later, and perform semantic entity resolution across sources.

---

## 2. Agent Architecture & Decision Loop (`graph.py`)
We implemented a **2-Agent LangGraph StateGraph** with conditional routing and self-correction:
* **Node 1 — `spatial_resolver_agent`:** Evaluates extracted locations. If Google Maps returns `None` or triggers the Israel centroid guardrail, the agent rewrites the Hebrew location string (removing directional noise and isolating highway/junction entities) and re-queries `advanced_geocoding_tool` up to **3 retries**.
* **Node 2 — `context_enricher_agent`:** Triggered whenever `accident_severity == 'not specified'`. Queries `cross_source_news_search` to retrieve follow-up articles within a matching spatial-temporal window and updates severity without hallucinating.
* **Node 3 — `spatial_cluster_check`:** Executes `spatial_density_analyzer` (PostGIS `ST_DWithin` 500m / 90-day window) to classify the incident under our Traffic Light Risk Indicator (Red $\ge 3$, Orange $= 2$, Green $= 1$).

---

## 3. Agent Tools (`tools.py`)
1. **`advanced_geocoding_tool(cleaned_location: str)`:** Queries Google Maps Geocoding API and enforces coordinate validation against known country/city centroid fallbacks.
2. **`cross_source_news_search(location: str, incident_date: str)`:** Searches ingested news feeds/database records for matching incidents on the same date and corridor to resolve missing injury severity.
3. **`spatial_density_analyzer(lat: float, lon: float, published_date: str)`:** Runs a leak-free historical lookback query (`published_date - 90 days`, 500m radius) in Neon PostgreSQL/PostGIS to flag `suspected_infrastructure_hazard`.

---

## 4. Guardrails & Deterministic Fallback
* **Semantic Traffic Gate (`is_traffic_accident`):** Filters out protests, security incidents, and non-traffic medical emergencies prior to spatial processing.
* **Centroid Rejection Guardrail:** Explicitly nullifies `31.0461, 34.8516` fallback coordinates so generic guesses never pollute spatial clusters.
* **Max-Retry Circuit Breaker (`max_retries = 3`):** If the agent cannot resolve a valid coordinate after 3 self-correction attempts (e.g., *"תאונה בכביש 6"* without an interchange), the graph routes to `fallback_node`, preserves the safe baseline JSON, and flags `agent_status = "REQUIRES_MANUAL_REVIEW"`. **The end-to-end pipeline never crashes even if the agent layer fails.**
