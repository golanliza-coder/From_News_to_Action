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

    # 2. העברת סרגל סינון הנתונים לצד ימין באמצעות פיצול לעמודות ראשיות
    # main_content_col (עמודה שמאלית רחבה) | sidebar_right_col (עמודה ימנית צרה)
    main_content_col, sidebar_right_col = st.columns([4, 1], gap="large")

    # ------------------ סרגל סינון אינטראקטיבי בצד ימין ------------------
    with sidebar_right_col:
        st.header("🔍 סרגל סינון")
        min_d, max_d = df_all['pub_date'].min().date(), df_all['pub_date'].max().date()
        date_range = st.date_input("טווח תאריכים", value=(min_d, max_d), min_value=min_d, max_value=max_d)
        sel_sev = st.multiselect("רמת חומרה", options=df_all['sev'].unique().tolist(), default=df_all['sev'].unique().tolist())
        sel_src = st.multiselect("ערוץ מקור", options=df_all['source'].unique().tolist(), default=df_all['source'].unique().tolist())
        
        # 3. הוספת סט סינון חדש: סינון לפי מדד הרמזור
        traffic_light_options = ['🔴 אדום - התרעת אנומליה מרחבית (3+)', '🟠 כתום - אזהרה (2 אירועים)', '🟢 תקין (אירוע בודד)']
        sel_traffic_light = st.multiselect("מדד הרמזור", options=traffic_light_options, default=traffic_light_options)
        
        only_red = st.checkbox("הצג מוקדי אנומליה אדומים בלבד (3+)", value=False)

        if active_f != 'ALL':
            if st.button("🔄 נקה סינון כרטיסייה (הצג הכל)", use_container_width=True):
                st.query_params.clear()
                st.rerun()

    # עיבוד וסינון הנתונים ב-DataFrame על בסיס הבחירות שנעשו בסרגל הימני
    df_base = df_all[df_all['sev'].isin(sel_sev) & df_all['source'].isin(sel_src)].copy()
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_d, end_d = date_range
        df_base = df_base[(df_base['pub_date'].dt.date >= start_d) & (df_base['pub_date'].dt.date <= end_d)]
    
    # החלת סינון מדד הרמזור
    df_base = df_base[df_base['hazard_level'].isin(sel_traffic_light)]
    
    if only_red:
        df_base = df_base[df_base['suspected__hazard']]

    total_base = len(df_base)
    fatal_cnt = len(df_base[df_base['sev'].isin(('קטלנית', 'קשה / קטלנית', 'קשה'))])
    cnt_2w = int(df_base['has_2w'].sum())
    cnt_vru = int(df_base['has_vru'].sum())
    pct_2w = round((cnt_2w / total_base) * 100) if total_base else 0
    pct_vru = round((cnt_vru / total_base) * 100) if total_base else 0

    # ------------------ עמודת תוכן הדשבורד הראשי (משמאל) ------------------
    with main_content_col:
        
    # 1. מרכוז שתי הכותרות הראשיות באמצעות אלמנטי HTML
        st.markdown("""
            <div style="text-align: center; margin-bottom: 5px;">
                <h1 style="font-size: 2.6rem; margin-bottom: 0px; padding-bottom: 0px;">🚨 From News To Action</h1>
                <h3 style="font-size: 1.25rem; color: #424242; font-weight: 500; margin-top: 8px; margin-bottom: 10px;">
                    מערכת אג'נטית לניתוח והשלמת נתוני תאונות דרכים עבור הנהלת הרלב"ד
                </h3>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

    # ------------------ שורה 1: 5 מדדי מפתח (KPIs) ------------------
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.markdown(f"<div class='kpi-card'><div style='font-weight:700;font-size:0.95rem;'>💀 קטלניות / קשות</div><div style='font-weight:800;font-size:1.85rem;margin-top:4px;'>{fatal_cnt}</div></div>", unsafe_allow_html=True)

        next_2w = "ALL" if active_f == "2W" else "2W"
        bg_2w = "background-color:#BBDEFB;border-color:#1565C0;" if active_f == "2W" else ""
        c2.markdown(f"<a href='?f={next_2w}' target='_self' style='text-decoration:none;'><div class='click-card' style='{bg_2w}'><div style='font-weight:700;font-size:0.95rem;'>🏍️ רוכבי דו-גלגלי</div><div style='font-weight:800;font-size:1.85rem;margin-top:4px;'>{cnt_2w} <span style='font-size:1rem;font-weight:500;'>({pct_2w}%)</span></div></div></a>", unsafe_allow_html=True)

        next_vru = "ALL" if active_f == "VRU" else "VRU"
        bg_vru = "background-color:#F8BBD0;border-color:#C2185B;" if active_f == "VRU" else ""
        c3.markdown(f"<a href='?f={next_vru}' target='_self' style='text-decoration:none;'><div class='click-card' style='{bg_vru}'><div style='font-weight:700;font-size:0.95rem;'>🚶 אוכלוסיות בסיכון</div><div style='font-weight:800;font-size:1.85rem;margin-top:4px;'>{cnt_vru} <span style='font-size:1rem;font-weight:500;'>({pct_vru}%)</span></div></div></a>", unsafe_allow_html=True)

        # החלת סינון לפי כרטיסיות KPI לחיצות
        if active_f == "2W":
            df_display = df_base[df_base['has_2w']].copy()
        elif active_f == "VRU":
            df_display = df_base[df_base['has_vru']].copy()
        else:
            df_display = df_base.copy()

        sources_count = df_display['source'].nunique()
        c4.markdown(f"<div class='meta-card'><div style='font-weight:700;font-size:0.95rem;'>📰 מקורות מידע</div><div style='font-weight:800;font-size:1.85rem;margin-top:4px;'>{sources_count}</div></div>", unsafe_allow_html=True)
        c5.markdown(f"<div class='kpi-card'><div style='font-weight:700;font-size:0.95rem;'>📊 סה\"כ אירועים</div><div style='font-weight:800;font-size:1.85rem;margin-top:4px;'>{len(df_display)}</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

    # ------------------ שורה 2: כותרת המפה ופירוט תכולה מרחבית ------------------
        st.markdown(f"### 🗺️ מדד רמזור: התרעות אנומליה מרחבית (רדיוס 500 מ' / 90 יום)")
        
        r_col, o_col, g_col = st.columns(3)
        red_count = len(df_display[df_display['hazard_level'].str.contains('🔴')])
        orange_count = len(df_display[df_display['hazard_level'].str.contains('🟠')])
        green_count = len(df_display[df_display['hazard_level'].str.contains('🟢')])

        r_col.markdown(f"<div class='kpi-card' style='border-top: 4px solid #D32F2F;'><div style='color:#D32F2F;font-weight:700;'>🔴 אנומליה מרחבית (3+)</div><div style='font-weight:800;font-size:1.6rem;'>{red_count}</div><div style='font-size:0.8rem;color:#777;'>suspected_hazard = True</div></div>", unsafe_allow_html=True)
        o_col.markdown(f"<div class='kpi-card' style='border-top: 4px solid #F57C00;'><div style='color:#F57C00;font-weight:700;'>🟠 רמת אזהרה (2)</div><div style='font-weight:800;font-size:1.6rem;'>{orange_count}</div><div style='font-size:0.8rem;color:#777;'>תאונות ברדיוס 500 מ'</div></div>", unsafe_allow_html=True)
        g_col.markdown(f"<div class='kpi-card' style='border-top: 4px solid #2E7D32;'><div style='color:#2E7D32;font-weight:700;'>🟢 תקין / בודד (1)</div><div style='font-weight:800;font-size:1.6rem;'>{green_count}</div><div style='font-size:0.8rem;color:#777;'>אירוע יחיד במרחב</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

    # ------------------ תצוגת מפת Pydeck ------------------
        df_map = df_display[df_display['lat'].notna() & df_display['lon'].notna()].copy()
        if not df_map.empty:
            view_state = pdk.ViewState(
                latitude=df_map['lat'].mean(),
                longitude=df_map['lon'].mean(),
                zoom=11,
                pitch=0
            )
            layer = pdk.Layer(
                "ScatterplotLayer",
                df_map,
                get_position=["lon", "lat"],
                get_color=["r", "g", "b", 160],
                get_radius=180,
                pickable=True,
            )
            st.pydeck_chart(pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip={"text": "מיקום: {loc}\nתאריך: {pub_date}\nחומרה: {sev}\nסטטוס: {hazard_level}"}
            ))
        else:
            st.warning("אין נתונים גיאוגרפיים להצגה על המפה עבור הסינון הנבחר.")

    # ------------------ טבלת נתונים מפורטת ------------------
        st.markdown("### 📋 רשימת אירועים מפורטת")
        st.dataframe(
            df_display[['pub_date', 'source', 'sev', 'loc', 'hazard_level']],
            column_config={
                "pub_date": st.column_config.DatetimeColumn("תאריך פרסום", format="DD/MM/YYYY HH:mm"),
                "source": "מקור",
                "sev": "חומרה",
                "loc": "מיקום מילולי",
                "hazard_level": "מדד רמזור מרחבי"
            },
            use_container_width=True,
            hide_index=True
        )

except Exception as e:
    st.error(f"שגיאה בטעינת הנתונים או בהרצת הדשבורד: {e}")






