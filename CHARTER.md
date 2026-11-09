# Project Charter: CHARTER.md

הערה: מסמך זה מעודכן לשלב סיום הפרויקט (נובמבר 2026) ומשקף את תוצאות האמת של ה-Pipeline האג'נטי והדשבורד הפעיל

## Project Name
**From News to Action: A Data-Centric Agentic AI Pipeline for Real-Time Traffic Infrastructure Risk Detection**

---
### 1. בעיה ומשתמש (Problem & Target User)
* **המשתמש:** מנכ"ל תקציבים ואנליסטים ברשות הלאומית לבטיחות בדרכים (הרלב"ד) ובמשרד התחבורה.
* **הכאב המכומת:** עיכוב של חודש עד חצי שנה בקבלת נתוני הלמ"ס והמשטרה הרשמיים יוצר "שטחים מתים" (Blindspots) ומעכב טיפול במפגעים קריטיים, מה שמוביל לעלייה של כ-15% בתאונות חוזרות ונשנות באותם מוקדים שלא טופלו בזמן.

**הערה:** "15% בתאונות חוזרות ונשנות" הוא נתון שנלקח ממאגר נתונים מרכזי של הלמ"ס

### הפיתרון: הפיכת זרם ידיעות חדשותיות ומבזקי חירום גולמיים בעברית (מבזקים המגיעים תוך דקות מהשטח) לנתונים מרחביים מובנים, מדויקים ופעילים בזמן אמת, המאפשרים זיהוי פרואקטיבי של אנומליות ומוקדי סיכון חודשים לפני הדוחות הרשמיים

---
### 2. מדד הצלחה (Success Metrics & Evaluation)

להלן תוצאות האמת האמפיריות של הפרויקט על סט הבדיקה המאומת (N=219 דיווחי אמת), המציגות את השדרוג הדרמטי של השכבה האג'נטית (Layer 3, מבוססת Gemini) לעומת צינור ה-Baseline הדטרמיניסטי:


<img width="946" height="562" alt="image" src="https://github.com/user-attachments/assets/abf0fb02-66d8-480a-ae63-903c2b7cc06b" />








---

### 3. דאטה + תוכנית ב' (Data Sources & Fallback) 
* **מקור נתונים ראשוני:** הנתונים מתבססים על צבירה של נתונים ב API 
מאתרי אונליין (מעריב, YNET, אמס, היום וחמ"ל) וטלגרם (מד"א, איחוד הצלה, כבאות והצלה).
* **תוכנית ב' :** במידה והניטור מאתרי אונליין שצויינו כמקור ראשון ייחסם נפנה לחלופות (כאן11,וואלה,C14). 
ואם גם אופציה זו תיחסם אזי נשקול שימוש במאגר היסטורי של תאונות המאוחסן בקובץ CSV/Google Drive משותף.

כמו כן במידה ומיקום התאונה יהיה ריק באמצעות geocoding (google map api) אזי נשתמש בטבלת מיקום בסיסית של כ30 אזורים גאוגרפיים.



---

### 4. תרשים ארכיטקטורה (System Architecture Diagram)

להלן ארכיטקטורת המערכת המחולקת ל-4 שכבות עיקריות:

```mermaid
flowchart TD
    subgraph BASELINE ["BASELINE"]
        BL1["Baseline Rules & Initial Heuristics"] --> BL2["Baseline Extraction & Comparison"]
    end

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
    BASELINE --> L2
    L2 --> L3
    L3 --> L4
  ```
    

### 5. הכיסא של הסוכן (Agent Specification)
* **מה הסוכן מחליט שקוד רגיל לא יכול?**
  הסוכן מנהל אוטונומית את **פתרון הסתירות המרחביות והשלמת הנתונים (Spatial Conflict Resolution & Contextual Enrichment)**. כשיש דיווחים מקבילים או סותרים על אותה תאונה (למשל: כתבה ב-ynet שמדווחת על "תאונה בכביש 4 ליד גהה" מול דיווח בטלגרם שמציין "תאונה ליד מחלף גבעת שמואל"), קוד דטרמיניסטי רגיל ייכשל או יקים כפילות. כלומר לאחר הצלבת הנתונים, הסוכן ממפה את השעה ואת המיקום הגאוגרפי של התאונה - מכריע מהו הנ"צ המדוייק. 
* **לאילו כלים יש לו גישה (Agent Tools)?**
  1. `Geocoding_Tool`: פנייה ל-OpenStreetMap / Nominatim API להמרת תיאור מילולי בעברית לקואורדינטות.
  2. `Spatial_Deduplication_Tool`: שאילתת PostgreSQL/PostGIS לאיתור אירועים קיימים ברדיוס 500 מטר ובחלון זמן של שעה.

      הערה - 500 מטר זה רמת הדיוק של הכלי.
  3. `Weather_API_Tool`: שליפת תנאי מזג אוויר ותאורה בזמן האירוע לפי המיקום המאומת.
* **מה קורה כשהוא נכשל (Fallback / Guardrails)?**
  אם הסוכן חורג מ-3 נסיונות תיקון עצמי (Max Retries) או מזהה כשל ב-API חיצוני, מנוע ה-**Deterministic Guardrail** שומר את ה-JSON הבסיסי שחולץ ללא הנ"צ, מתייג את הרשומה בבסיס הנתונים כ-`Requires_Manual_Review`, וממשיכה בהרצת ה-Pipeline כרגיל. **המערכת עובדת בצורה מלאה ומניבה פלט גם ללא השכבה האג'נטית.**

---

### 6. סיכונים וגרסת חתך (Risks & Scope Cut)
* **סיכון 1 (הזיות מיקום ב-LLM):** היעדר מיקום קבוע ומדוייק של מקום התאונה.
  * *הערכות:* אכיפת פלט קשיח באמצעות Pydantic Schema ואימות חובה מול API גאוגרפי חיצוני.
* **סיכון 2 (חסימת API / Scraping):** חסימת גישה לטלגרם או שינוי במבנה HTML באתרי החדשות.
  * *הערכות:* מעבר לעבודה מול מאגר סטטי של תאונות המאוחסן מראש ב-`data/raw/`.
* **סיכון 3 (חריגת עלויות ואיטיות ב-LLM):** קריאות מרובות מדי למודלים יקרים.
  * *הערכות:* שימוש במודל קטן ומהיר (Llama-3.3-70B via Groq / GPT-4o-mini) והגבלת התיקון העצמי ל-2 סבבים בלבד.
* **משפט חתך (Scope Cut):** *"אם נשארים שבועיים בלבד לפני ההגשה, מוותרים על דאשבורד ה-Streamlit ועל שליפת נתוני מזג האוויר, ומגישים Pipeline עובד שמפיק בסיס נתונים/קובץ CSV מעובד ומאומת ברמת הסוכן בלבד"*.

---

### 7. אבני דרך וכובעים (Milestones & Team Roles)

#### חלוקת תפקידים ותחומי אחריות בפרויקט (Team Roles & Responsibilities)
> **הערה:** חלוקת התפקידים בצוות הינה **דינמית ותשתנה באופן גמיש בהתאם לקצב פיתוח הפרויקט**, עומסי העבודה והצרכים שיווצרו באזורים השונים. 

**תחומי הליבה הדורשים טיפול בפרויקט והובלה משותפת:**
1. **Data Ingestion & Pipeline:** פיתוח סקריפטי האיסוף (Telegram/Scraping) וצינור הנתונים.
2. **Agentic Architecture & Tools:** הגדרת הסוכן (LangGraph), בניית לולאת התיקון העצמי וחיבור הכלים (Geocoding / DB Search).
3. **Guardrails & Fallbacks:** בניית מנגנוני ההגנה וה-Fallback הדטרמיניסטי במקרה של כשל בסוכן.
4. **Prompt Engineering & Structured Schema:** עיצוב הפרומפטים ואכיפת פורמט Pydantic JSON.
5. **Evaluation Set & Benchmarking:** בניית ערכת בדיקה (Eval-Set), מדידת Precision/Recall ומדד Groundedness.
6. **Baseline Engine:** פיתוח מערכת הבסיס (ללא סוכן) לצורך השוואה וטבלת Baseline.
7. **Database & Storage:** הקמה וניהול בסיס הנתונים המרחבי (PostgreSQL + PostGIS).
8. **Product, Documentation & Dashboard:** כתיבת ה-Project Charter, ה-README המרכזי ופיתוח דאשבורד ה-Streamlit.

---

## 8. אבני דרך (Milestones)

| תאריך | יום | פורמט | אבן דרך |
| :--- | :---: | :---: | :--- |
| **25.09.26** | ו | | הגשת Project Charter |
| **18.10.26** | א | | Checkpoint 1 (Optional): מערכת בסיס |
| **04.11.26** | ד | זום | מפגש ליווי פרטני 1 |
| **08.11.26** | א | זום | מפגש ליווי פרטני 2 |
| **18.11.26** | א | כיתה | הצגת פרויקטים + חלוקת תעודות |
