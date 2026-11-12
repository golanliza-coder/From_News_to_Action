import ast
import json
import numpy as np
import pandas as pd
import plotly.express as px
import psycopg
import pydeck as pdk
import streamlit as st

conn_str = st.secrets["DATABASE_URL"]

# 4. הזרקת CSS מותאם אישית - עיצוב רקע ושינוי צבע תגיות הסינון מאדום לתכלת
st.markdown(
    """
<style>
/* עיצוב רקע כללי */
.stApp, [data-testid="stHeader"] { background-color: #E3F2FD; }

/* שינוי צבע הרקע של התגיות שנבחרו בתוך ה-multiselect לתכלת */
div[data-baseweb="tag"] {
    background-color: #B3E5FC !important;
    color: #01579B !important; /* טקסט כהה לקריאות */
    border-radius: 6px !important;
}
/* שינוי אייקון ה-X למחיקת התגית */
div[data-baseweb="tag"] svg {
    fill: #01579B !important;
}

/* עיצובי כרטיסיות KPI */
.kpi-card {
    background-color: #FFFFFF; padding: 14px; border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.08); text-align: center;
    min-height: 115px; display: flex; flex-direction: column; justify-content: center;
    transition: all 0.2s ease;
}
.click-card {
    background-color: #FFFFFF; padding: 14px; border-radius: 10px;
    border: 2px solid #90CAF9; box-shadow: 0 2px 4px rgba(0,0,0,0.08); text-align: center;
    min-height: 115px; display: flex; flex-direction: column; justify-content: center;
    cursor: pointer; transition: all 0.2s ease; text-decoration: none !important; color: #111 !important;
}
.click-card:hover {
    border-color: #1976D2; transform: translateY(-2px); box-shadow: 0 4px 10px rgba(25,118,210,0.2);
}
.meta-card {
    background-color: #F4F9FF; padding: 14px; border-radius: 10px;
    border: 1.5px solid #90CAF9; box-shadow: 0 2px 4px rgba(0,0,0,0.06); text-align: center;
    min-height: 115px; display: flex; flex-direction: column; justify-content: center;
}

/* הסתרת אזור ה-sidebar המובנה הריק של סטרימליט בצד שמאל */
[data-testid="stSidebar"] {
    display: none !important;
}

/* הסתרת כפתור החץ (הלולאה/פתיחה) של ה-sidebar המקורי */
[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}

/* הרחבת התוכן המרכזי שיתפוס את כל רוחב המסך שהתפנה */
.stMainBlockContainer {
    max-width: 100% !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}
</style>
""",
    unsafe_allow_html=True,
)

sev_map = {
    "moderate": "בינונית",
    "not specified": "לא מצוין",
    "not_specified": "לא מצוין",
    "severe": "קשה / קטלנית",
    "fatal": "קטלנית",
    "hard": "קשה",
    "medium": "בינונית",
    "light": "קלה",
    "mild": "קלה",
    "unknown": "לא מצוין",
}
veh_map = {
    "car": "רכב פרטי",
    "bus": "אוטובוס",
    "motorcycle": "אופנוע",
    "tractor": "טרקטור",
    "bicycle": "אופניים",
    "truck": "משאית",
    "electric scooter": "קורקינט חשמלי",
    "e-scooter": "קורקינט חשמלי",
    "minibus": "מיניבוס",
    "train": "רכבת",
    "electric bicycle": "אופניים חשמליים",
    "e-bike": "אופניים חשמליים",
    "mobility scooter": "קלנועית",
    "excavator": "מחפר / כלי הנדסי",
    "scooter": "קטנוע",
    "commercial vehicle": "רכב מסחרי",
}
two_wheel_keys = (
    "motorcycle",
    "scooter",
    "bicycle",
    "e-bike",
    "e-scooter",
    "אופנוע",
    "קורקינט",
    "אופניים",
    "קטנוע",
)

def classify_vuln(raw_v, v_list):
    cats = set()
    t = str(raw_v).lower() if raw_v else ""
    if t and t not in ("none", "not specified", "לא מצוין", "[]", "nan"):
        if any(w in t for w in ("pedestrian", "הולך רגל", "הולכת רגל", "הולכי רגל")):
            cats.add("הולכי רגל")
        if any(
            w in t
            for w in (
                "child",
                "kid",
                "boy",
                "girl",
                "teen",
                "youth",
                "ילד",
                "ילדה",
                "נער",
                "נערה",
                "בן 1",
                "בת 1",
            )
        ):
            cats.add("ילדים ובני נוער (0-18)")
        if any(
            w in t
            for w in (
                "70",
                "80",
                "90",
                "65",
                "elderly",
                "senior",
                "קשיש",
                "קשישה",
                "מבוגר",
            )
        ):
            cats.add("אזרחים ותיקים (60+)")
    if isinstance(v_list, list):
        vs = " ".join(str(v).lower() for v in v_list)
        if any(w in vs for w in two_wheel_keys):
            cats.add("רוכבי דו-גלגלי / מיקרו-מוביליטי")
    return list(cats)

def compute_spatial_anomaly(df):
    df["cluster_count"], df["suspected__hazard"] = 1, False
    df["hazard_level"] = "🟢 תקין (אירוע בודד)"
    df["r"], df["g"], df["b"] = 46, 125, 50
    valid_mask = (
        df["lat"].notna()
        & df["lon"].notna()
        & df["pub_date"].notna()
        & (~df["loc"].str.lower().isin(("not specified", "לא מצוין", "לא פוענח", "none", "")))
        & (
            ~((df["lat"].round(4) == 32.0927) & (df["lon"].round(4) == 34.8465))
        )
    )
    valid = df[valid_mask].copy()
    if valid.empty:
        return df
    lats, lons = np.radians(valid["lat"].values), np.radians(valid["lon"].values)
    dates = valid["pub_date"].values.astype("datetime64[D]").astype(int)
    dlat, dlon = lats[:, None] - lats[None, :], lons[:, None] - lons[None, :]
    a = (
        np.sin(dlat / 2.0) ** 2
        + np.cos(lats[:, None]) * np.cos(lats[None, :]) * np.sin(dlon / 2.0) ** 2
    )
    counts = (
        (6371000 * 2 * np.arcsin(np.sqrt(a)) <= 500)
        & (np.abs(dates[:, None] - dates[None, :]) <= 90)
    ).sum(axis=1)
    for idx, cnt in zip(valid.index, counts):
        df.at[idx, "cluster_count"] = int(cnt)
        if cnt >= 3:
            (
                df.at[idx, "suspected__hazard"],
                df.at[idx, "hazard_level"],
            ) = (True, "🔴 אדום - התרעת אנומליה מרחבית (3+)")
            df.at[idx, "r"], df.at[idx, "g"], df.at[idx, "b"] = 211, 47, 47
        elif cnt == 2:
            df.at[idx, "hazard_level"] = "🟠 כתום - אזהרה (2 אירועים)"
            df.at[idx, "r"], df.at[idx, "g"], df.at[idx, "b"] = 245, 124, 0
    return df


@st.cache_data(ttl=5)
def load_data():
    with psycopg.connect(conn_str) as conn:
        df_raw = pd.read_sql_query(
            "SELECT id, source, published_date, article_data FROM traffic_incidents;",
            conn,
        )
    rows = []
    for _, r in df_raw.iterrows():
        d = (
            json.loads(r["article_data"])
            if isinstance(r["article_data"], str)
            else r["article_data"]
        )
        sev = sev_map.get(
            str(d.get("accident_severity", "לא מצוין")).strip().lower(),
            str(d.get("accident_severity", "לא מצוין")).strip(),
        )
        try:
            lat, lon = float(d.get("latitude")), float(d.get("longitude"))
            if not (29.0 <= lat <= 33.5 and 34.0 <= lon <= 36.0):
                lat, lon = None, None
        except:
            lat, lon = None, None
        vehs = d.get("vehicle_types") or d.get("involved_vehicles") or []
        if isinstance(vehs, str) and vehs.startswith("["):
            try:
                vehs = ast.literal_eval(vehs)
            except:
                vehs = []
        vulns = classify_vuln(
            d.get("vulnerable_users_and_ages") or d.get("vulnerable_road_users"),
            vehs,
        )
        has_2w = (
            any(k in " ".join(str(v).lower() for v in vehs) for k in two_wheel_keys)
            if isinstance(vehs, list)
            else False
        )
        rows.append(
            {
                "id": r["id"],
                "source": r["source"],
                "pub_date": pd.to_datetime(r["published_date"]),
                "sev": sev,
                "loc": d.get("verbal_location")
                or d.get("resolved_address")
                or "לא מצוין",
                "lat": lat,
                "lon": lon,
                "vehs": vehs,
                "vulns": vulns,
                "has_2w": has_2w,
                "has_vru": len(vulns) > 0,
                "raw_text": d.get("raw_text", ""),
            }
        )
    return compute_spatial_anomaly(
        pd.DataFrame(rows).drop_duplicates(subset=["id"])
    )

try:
    df_all = load_data()
    active_f = st.query_params.get("f", "ALL")

    # 1. חלוקת המסך: עמודת תוכן רחבה משמאל (4) ועמודת סרגל צרה מימין (1)
    main_content_col, sidebar_right_col = st.columns([4, 1], gap="large")

    # ------------------ סרגל סינון אינטראקטיבי בצד ימין ------------------
    with sidebar_right_col:
        st.markdown("### 🔍 סרגל סינון נתונים")
        
        min_d = df_all['pub_date'].min().date()
        max_d = df_all['pub_date'].max().date()
        date_range = st.date_input("טווח תאריכים", [min_d, max_d], min_value=min_d, max_value=max_d)
        
        all_sevs = sorted(df_all['sev'].unique())
        selected_sevs = st.multiselect("רמת חומרה", all_sevs, default=all_sevs)
        
        all_sources = sorted(df_all['source'].unique())
        selected_sources = st.multiselect("ערוץ מקור", all_sources, default=all_sources)
        
        # מסנן מדד הרמזור החדש (בחירה מרובה)
        traffic_light_options = [
            "🔴 אדום - אנומליה מרחבית (+3)",
            "🟠 כתום - אזהרה (2)",
            "🟢 ירוק - תקין / בודד (1)"
        ]
        selected_traffic_lights = st.multiselect(
            "מדד רמזור",
            traffic_light_options,
            default=traffic_light_options
        )
        
        # תיבת הסימון הקיימת בתחתית הסרגל
        only_red_anomalies = st.checkbox("הצג מוקדי אנומליה אדומים בלבד (+3)", value=False)

    # ------------------ לוגיקת סינון הדאטה ------------------
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        df_filtered = df_all[(df_all['pub_date'] >= start_date) & (df_all['pub_date'] <= end_date)]
    else:
        df_filtered = df_all.copy()
        
    df_filtered = df_filtered[df_filtered['sev'].isin(selected_sevs)]
    df_filtered = df_filtered[df_filtered['source'].isin(selected_sources)]
    
    # סינון לפי מדד הרמזור שנבחר ב-multiselect
    tl_mask = pd.Series(False, index=df_filtered.index)
    if "🔴 אדום - אנומליה מרחבית (+3)" in selected_traffic_lights:
        tl_mask |= (df_filtered['cluster_count'] >= 3)
    if "🟠 כתום - אזהרה (2)" in selected_traffic_lights:
        tl_mask |= (df_filtered['cluster_count'] == 2)
    if "🟢 ירוק - תקין / בודד (1)" in selected_traffic_lights:
        tl_mask |= (df_filtered['cluster_count'] == 1)
    df_filtered = df_filtered[tl_mask]
    
    # החלת תיבת הסימון התחתונה (אם סומנה)
    if only_red_anomalies:
        df_filtered = df_filtered[df_filtered['cluster_count'] >= 3]
    
    # חישוב נתונים לכרטיסיות
    total_events = len(df_filtered)
    total_sources = df_filtered['source'].nunique()
    fatal_severe = len(df_filtered[df_filtered['sev'].isin(['קטלנית', 'קשה / קטלנית', 'קשה'])])
    two_wheel_count = len(df_filtered[df_filtered['has_2w'] == True])
    vulnerable_pct = int((len(df_filtered[df_filtered['has_vru'] == True]) / total_events * 100)) if total_events > 0 else 0
    vulnerable_count = len(df_filtered[df_filtered['has_vru'] == True])
    
    anomaly_red = len(df_filtered[df_filtered['cluster_count'] >= 3])
    anomaly_orange = len(df_filtered[df_filtered['cluster_count'] == 2])
    anomaly_green = len(df_filtered[df_filtered['cluster_count'] == 1])

    # ------------------ תוכן הדשבורד המרכזי בצד שמאל ------------------
    with main_content_col:
        st.markdown("<h1 style='text-align: right;'>🚨 From News To Action</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: right;'>מערכת אג'נטית לניתוח והשלמת נתוני תאונות דרכים עבור הנהלת הרלב\"ד</h3>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # תצוגת חמשת כרטיסיות ה-KPI העליונות (מימין לשמאל)
        kpi_cols = st.columns(5)
        
        with kpi_cols[4]:
            st.markdown(f"<div class='kpi-card'><span style='color: #0D47A1; font-size: 14px; font-weight: bold;'>סה\"כ אירועים</span><h2 style='margin: 5px 0; color: #0D47A1;'>{total_events}</h2></div>", unsafe_allow_html=True)
        with kpi_cols[3]:
            st.markdown(f"<div class='kpi-card'><span style='color: #4A148C; font-size: 14px; font-weight: bold;'>מקורות מידע</span><h2 style='margin: 5px 0; color: #4A148C;'>{total_sources}</h2></div>", unsafe_allow_html=True)
        with kpi_cols[2]:
            st.markdown(f"<div class='kpi-card'><span style='color: #1565C0; font-size: 14px; font-weight: bold;'>אוכלוסיות סיכון</span><h2 style='margin: 5px 0; color: #1565C0;'>{vulnerable_pct}%</h2><span style='font-size: 12px; color: #555;'>({vulnerable_count})</span></div>", unsafe_allow_html=True)
        with kpi_cols[1]:
            st.markdown(f"<div class='kpi-card'><span style='color: #006064; font-size: 14px; font-weight: bold;'>מעורבות דו-גלגלי</span><h2 style='margin: 5px 0; color: #006064;'>{int(two_wheel_count/total_events*100) if total_events > 0 else 0}%</h2><span style='font-size: 12px; color: #555;'>({two_wheel_count})</span></div>", unsafe_allow_html=True)
        with kpi_cols[0]:
            st.markdown(f"<div class='kpi-card'><span style='color: #B71C1C; font-size: 14px; font-weight: bold;'>קטלניות / קשות</span><h2 style='margin: 5px 0; color: #B71C1C;'>{fatal_severe}</h2></div>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: right;'>מדד רמזור: התרעות אנומליה מרחבית (רדיוס 500 מ' / 90 יום) ⏳</h4>", unsafe_allow_html=True)
        
        # תצוגת כרטיסיות מדד הרמזור (מימין לשמאל)
        traffic_light_cols = st.columns(3)
        
        with traffic_light_cols[2]:
            st.markdown(f"<div class='meta-card' style='border-top: 5px solid #D32F2F;'><span style='color: #D32F2F; font-weight: bold;'>אנומליה מרחבית (+3) 🔴</span><h2 style='margin: 5px 0;'>{anomaly_red}</h2><span style='font-size: 11px; color: #777;'>suspected_hazard = True</span></div>", unsafe_allow_html=True)
        with traffic_light_cols[1]:
            st.markdown(f"<div class='meta-card' style='border-top: 5px solid #F57C00;'><span style='color: #F57C00; font-weight: bold;'>רמת אזהרה (2) 🟠</span><h2 style='margin: 5px 0;'>{anomaly_orange}</h2><span style='font-size: 11px; color: #777;'>תאונות ברדיוס 500 מ'</span></div>", unsafe_allow_html=True)
        with traffic_light_cols[0]:
            st.markdown(f"<div class='meta-card' style='border-top: 5px solid #2E7D32;'><span style='color: #2E7D32; font-weight: bold;'>תקין / בודד (1) 🟢</span><h2 style='margin: 5px 0;'>{anomaly_green}</h2><span style='font-size: 11px; color: #777;'>אירוע יחיד במרחב</span></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: right;'>פריסת אירועים ומוקדי אנומליה במרחב ישראל 🗺️</h4>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"שגיאה בטעינת הדשבורד: {e}")


