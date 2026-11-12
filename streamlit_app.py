import ast
import json
import numpy as np
import pandas as pd
import plotly.express as px
import psycopg
import pydeck as pdk
import streamlit as st

st.set_page_config(page_title="From News To Action - הרלב\"ד", layout="wide")

conn_str = st.secrets["DATABASE_URL"]

st.markdown("""
<style>
.stApp, [data-testid="stHeader"] { background-color: #E3F2FD; }
.kpi-card {
    background-color: #FFFFFF; padding: 14px; border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.08); text-align: center;
    height: 145px; display: flex; flex-direction: column; justify-content: center;
    transition: all 0.2s ease;
}
.click-card {
    background-color: #FFFFFF; padding: 14px; border-radius: 10px;
    border: 2px solid #90CAF9; box-shadow: 0 2px 4px rgba(0,0,0,0.08); text-align: center;
    min-height: 115px; display: flex !important; flex-direction: column; justify-content: center;
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
div[data-baseweb="tag"] {
    background-color: #B3E5FC !important;
    color: #01579B !important;
}
div[data-baseweb="tag"] svg {
    fill: #01579B !important;
}
/* שינוי צבע תגיות הבחירה (Multiselect) מאדום לתכלת */
div[data-baseweb="tag"] {
    background-color: #B3E5FC !important;
    color: #01579B !important;
    border-radius: 6px !important;
}

/* שינוי צבע אייקון ה-X למחיקת תגית */
div[data-baseweb="tag"] svg {
    fill: #01579B !important;
}

/* שינוי צבע המסגרת של תיבת הסינון כשלוחצים עליה מאדום לתכלת-כחול */
div[data-baseweb="select"] > div:focus-within {
    border-color: #0288D1 !important;
    box-shadow: 0 0 0 1px #0288D1 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<h1 style='text-align: center; display: flex; align-items: center; justify-content: center; gap: 12px; color: #0D47A1;'>
    <span>From News To Action</span>
    <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#0288D1" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"></circle>
        <circle cx="12" cy="12" r="6"></circle>
        <circle cx="12" cy="12" r="2"></circle>
        <line x1="12" y1="2" x2="12" y2="6"></line>
    </svg>
</h1>
""", unsafe_allow_html=True)

st.markdown("<h3 style='text-align: center;'>מערכת אג'נטית לניתוח והשלמת נתוני תאונות דרכים עבור הנהלת הרלב\"ד</h3>", unsafe_allow_html=True)
st.markdown("---")

sev_map = {
    'moderate': 'בינונית', 'not specified': 'לא מצוין', 'not_specified': 'לא מצוין',
    'severe': 'קשה / קטלנית', 'fatal': 'קטלנית', 'hard': 'קשה',
    'medium': 'בינונית', 'light': 'קלה', 'mild': 'קלה', 'unknown': 'לא מצוין'
}
veh_map = {
    'car': 'רכב פרטי', 'bus': 'אוטובוס', 'motorcycle': 'אופנוע', 'tractor': 'טרקטור',
    'bicycle': 'אופניים', 'truck': 'משאית', 'electric scooter': 'קורקינט חשמלי',
    'e-scooter': 'קורקינט חשמלי', 'minibus': 'מיניבוס', 'train': 'רכבת',
    'electric bicycle': 'אופניים חשמליים', 'e-bike': 'אופניים חשמליים',
    'mobility scooter': 'קלנועית', 'excavator': 'מחפר / כלי הנדסי',
    'scooter': 'קטנוע', 'commercial vehicle': 'רכב מסחרי'
}
two_wheel_keys = ('motorcycle', 'scooter', 'bicycle', 'e-bike', 'e-scooter', 'אופנוע', 'קורקינט', 'אופניים', 'קטנוע')

def classify_vuln(raw_v, v_list):
    cats = set()
    t = str(raw_v).lower() if raw_v else ""
    if t and t not in ('none', 'not specified', 'לא מצוין', '[]', 'nan'):
        if any(w in t for w in ('pedestrian', 'הולך רגל', 'הולכת רגל', 'הולכי רגל')):
            cats.add('הולכי רגל')
        if any(w in t for w in ('child', 'kid', 'boy', 'girl', 'teen', 'youth', 'ילד', 'ילדה', 'נער', 'נערה', 'בן 1', 'בת 1')):
            cats.add('ילדים ובני נוער (0-18)')
        if any(w in t for w in ('70', '80', '90', '65', 'elderly', 'senior', 'קשיש', 'קשישה', 'מבוגר')):
            cats.add('אזרחים ותיקים (60+)')
    if isinstance(v_list, list):
        vs = " ".join(str(v).lower() for v in v_list)
        if any(w in vs for w in two_wheel_keys):
            cats.add('רוכבי דו-גלגלי / מיקרו-מוביליטי')
    return list(cats)

def compute_spatial_anomaly(df):
    df['cluster_count'], df['suspected__hazard'] = 1, False
    df['hazard_level'] = '🟢 תקין (אירוע בודד)'
    df['r'], df['g'], df['b'] = 46, 125, 50
    valid_mask = (
        df['lat'].notna() & df['lon'].notna() & df['pub_date'].notna()
        & (~df['loc'].str.lower().isin(('not specified', 'לא מצוין', 'לא פוענח', 'none', '')))
        & (~((df['lat'].round(4) == 32.0927) & (df['lon'].round(4) == 34.8465)))
    )
    valid = df[valid_mask].copy()
    if valid.empty:
        return df
    lats, lons = np.radians(valid['lat'].values), np.radians(valid['lon'].values)
    dates = valid['pub_date'].values.astype('datetime64[D]').astype(int)
    dlat, dlon = lats[:, None] - lats[None, :], lons[:, None] - lons[None, :]
    a = np.sin(dlat / 2.0)**2 + np.cos(lats[:, None]) * np.cos(lats[None, :]) * np.sin(dlon / 2.0)**2
    counts = ((6371000 * 2 * np.arcsin(np.sqrt(a)) <= 500) & (np.abs(dates[:, None] - dates[None, :]) <= 90)).sum(axis=1)
    for idx, cnt in zip(valid.index, counts):
        df.at[idx, 'cluster_count'] = int(cnt)
        if cnt >= 3:
            df.at[idx, 'suspected__hazard'], df.at[idx, 'hazard_level'] = True, '🔴 אדום - התרעת אנומליה מרחבית (3+)'
            df.at[idx, 'r'], df.at[idx, 'g'], df.at[idx, 'b'] = 211, 47, 47
        elif cnt == 2:
            df.at[idx, 'hazard_level'] = '🟠 כתום - אזהרה (2 אירועים)'
            df.at[idx, 'r'], df.at[idx, 'g'], df.at[idx, 'b'] = 245, 124, 0
    return df

@st.cache_data(ttl=5)
def load_data():
    with psycopg.connect(conn_str) as conn:
        df_raw = pd.read_sql_query("SELECT id, source, published_date, article_data FROM traffic_incidents;", conn)
    rows = []
    for _, r in df_raw.iterrows():
        d = json.loads(r['article_data']) if isinstance(r['article_data'], str) else r['article_data']
        sev = sev_map.get(str(d.get('accident_severity', 'לא מצוין')).strip().lower(), str(d.get('accident_severity', 'לא מצוין')).strip())
        try:
            lat, lon = float(d.get('latitude')), float(d.get('longitude'))
            if not (29.0 <= lat <= 33.5 and 34.0 <= lon <= 36.0):
                lat, lon = None, None
        except:
            lat, lon = None, None
        vehs = d.get('vehicle_types') or d.get('involved_vehicles') or []
        if isinstance(vehs, str) and vehs.startswith('['):
            try:
                vehs = ast.literal_eval(vehs)
            except:
                vehs = []
        vulns = classify_vuln(d.get('vulnerable_users_and_ages') or d.get('vulnerable_road_users'), vehs)
        has_2w = any(k in " ".join(str(v).lower() for v in vehs) for k in two_wheel_keys) if isinstance(vehs, list) else False
        rows.append({
            'id': r['id'],
            'source': r['source'],
            'pub_date': pd.to_datetime(r['published_date']),
            'sev': sev,
            'loc': d.get('verbal_location') or d.get('resolved_address') or 'לא מצוין',
            'lat': lat,
            'lon': lon,
            'vehs': vehs,
            'vulns': vulns,
            'has_2w': has_2w,
            'has_vru': len(vulns) > 0,
            'raw_text': d.get('raw_text', '')
        })
    return compute_spatial_anomaly(pd.DataFrame(rows).drop_duplicates(subset=['id']))

try:
    df_all = load_data()
    active_f = st.query_params.get("f", "ALL")

    # ------------------ סרגל סינון אינטראקטיבי בצד ------------------
    st.sidebar.header("🔍 סרגל סינון נתונים")
    min_d, max_d = df_all['pub_date'].min().date(), df_all['pub_date'].max().date()
    date_range = st.sidebar.date_input("טווח תאריכים", value=(min_d, max_d), min_value=min_d, max_value=max_d)
    
    sel_sev = st.sidebar.multiselect("רמת חומרה", options=sorted(df_all['sev'].unique().tolist()), default=sorted(df_all['sev'].unique().tolist()))
    sel_src = st.sidebar.multiselect("ערוץ מקור", options=sorted(df_all['source'].unique().tolist()), default=sorted(df_all['source'].unique().tolist()))
    
    # מסנן מדד הרמזור החדש (multiselect)
    tl_options = [
        "🔴 אדום - התרעת אנומליה מרחבית (3+)",
        "🟠 כתום - אזהרה (2 אירועים)",
        "🟢 תקין (אירוע בודד)"
    ]
    sel_tl = st.sidebar.multiselect("מדד רמזור", options=tl_options, default=tl_options)
    
    # תיבת הסימון הקיימת בתחתית הסרגל
    only_red = st.sidebar.checkbox("הצג מוקדי אנומליה אדומים בלבד (3+)", value=False)

    if active_f != 'ALL':
        if st.sidebar.button("🔄 נקה סינון כרטיסייה (הצג הכל)", width='stretch'):
            st.query_params.clear()
            st.rerun()

    # ------------------ לוגיקת סינון הדאטה ------------------
    df_base = df_all[
        df_all['sev'].isin(sel_sev) &
        df_all['source'].isin(sel_src) &
        df_all['hazard_level'].isin(sel_tl)
    ].copy()
    
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_d, end_d = date_range
        df_base = df_base[(df_base['pub_date'].dt.date >= start_d) & (df_base['pub_date'].dt.date <= end_d)]

    if only_red:
        df_base = df_base[df_base['suspected__hazard']]

    # חישוב מדדי הרמזור מתוך הטבלה המסוננת
    red_cnt = int((df_base['cluster_count'] >= 3).sum())
    orange_cnt = int((df_base['cluster_count'] == 2).sum())
    green_cnt = int((df_base['cluster_count'] == 1).sum())

    # סינון נוסף לפי לחיצה על כרטיסיית KPI עליונה
    df_view = df_base.copy()
    if active_f == "2W":
        df_view = df_view[df_view['has_2w']]
    elif active_f == "VRU":
        df_view = df_view[df_view['has_vru']]

    total_base = len(df_view)
    total_sources = df_view['source'].nunique()
    fatal_cnt = len(df_view[df_view['sev'].isin(('קטלנית', 'קשה / קטלנית', 'קשה'))])
    cnt_2w = int(df_view['has_2w'].sum())
    cnt_vru = int(df_view['has_vru'].sum())
    pct_2w = round((cnt_2w / total_base) * 100) if total_base else 0
    pct_vru = round((cnt_vru / total_base) * 100) if total_base else 0

    # ------------------ שורה 1: 5 מדדי מפתח ------------------   
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(f"<div class='kpi-card'><div style='font-weight:700;font-size:1.15rem;color:#B71C1C;'>💀 קטלניות / קשות</div><div style='font-weight:800;font-size:2.4rem;margin-top:6px;color:#B71C1C;'>{fatal_cnt}</div></div>", unsafe_allow_html=True)

    next_2w = "ALL" if active_f == "2W" else "2W"
    bg_2w = "background-color:#BBDEFB;border-color:#1565C0;" if active_f == "2W" else ""
    c2.markdown(f"<div class='kpi-card'><div style='font-weight:700;font-size:1.15rem;color:#006064;'>🛵 מעורבות דו-גלגלי</div><div style='font-weight:800;font-size:2.4rem;margin-top:6px;color:#006064;'>{pct_2w}%</div><div style='font-size:0.95rem;color:#444;'>({cnt_2w})</div></div>", unsafe_allow_html=True)

    next_vru = "ALL" if active_f == "VRU" else "VRU"
    bg_vru = "background-color:#BBDEFB;border-color:#1565C0;" if active_f == "VRU" else ""
    c3.markdown(f"<div class='kpi-card'><div style='font-weight:700;font-size:1.15rem;color:#1565C0;'>🚶 אוכלוסיות סיכון</div><div style='font-weight:800;font-size:2.4rem;margin-top:6px;color:#1565C0;'>{pct_vru}%</div><div style='font-size:0.95rem;color:#444;'>({cnt_vru})</div></div>", unsafe_allow_html=True)
    
    c4.markdown(f"<div class='kpi-card'><div style='font-weight:700;font-size:1.15rem;color:#4A148C;'>📰 מקורות מידע</div><div style='font-weight:800;font-size:2.4rem;margin-top:6px;color:#4A148C;'>{total_sources}</div></div>", unsafe_allow_html=True)
    c5.markdown(f"<div class='kpi-card'><div style='font-weight:700;font-size:1.15rem;color:#0D47A1;'>📊 סה\"כ אירועים</div><div style='font-weight:800;font-size:2.4rem;margin-top:6px;color:#0D47A1;'>{total_base}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------ שורה 2: כרטיסיות מדד הרמזור ------------------
    st.markdown("<h4 style='text-align: right;'>🚦 מדד רמזור: התרעות אנומליה מרחבית (רדיוס 500 מ' / 90 יום)</h4>", unsafe_allow_html=True)
    tl1, tl2, tl3 = st.columns(3)
    tl1.markdown(f"<div class='meta-card' style='border-top: 5px solid #2E7D32;'><div style='color:#2E7D32;font-weight:bold;font-size:1.15rem;'>🟢 תקין / בודד (1)</div><div style='font-size:2.4rem;font-weight:800;margin:6px 0;'>{green_cnt}</div><div style='font-size:0.95rem;color:#555;'>אירוע יחיד במרחב</div></div>", unsafe_allow_html=True)
    tl2.markdown(f"<div class='meta-card' style='border-top: 5px solid #F57C00;'><div style='color:#F57C00;font-weight:bold;font-size:1.15rem;'>🟠 רמת אזהרה (2)</div><div style='font-size:2.4rem;font-weight:800;margin:6px 0;'>{orange_cnt}</div><div style='font-size:0.95rem;color:#555;'>תאונות ברדיוס 500 מ'</div></div>", unsafe_allow_html=True)
    tl3.markdown(f"<div class='meta-card' style='border-top: 5px solid #D32F2F;'><div style='color:#D32F2F;font-weight:bold;font-size:1.15rem;'>🔴 אנומליה מרחבית (+3)</div><div style='font-size:2.4rem;font-weight:800;margin:6px 0;'>{red_cnt}</div><div style='font-size:0.95rem;color:#555;'>suspected_hazard = True</div></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------ שורה 3: מפה אינטראקטיבית ------------------
    st.markdown("<h4 style='text-align: right;'>🗺️ פריסת אירועים ומוקדי אנומליה במרחב ישראל</h4>", unsafe_allow_html=True)
    map_df = df_view.dropna(subset=['lat', 'lon']).copy()
    if not map_df.empty:
        map_df['date_str'] = map_df['pub_date'].dt.strftime('%Y-%m-%d')
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position='[lon, lat]',
            get_fill_color='[r, g, b, 200]',
            get_radius=450,
            radius_min_pixels=6,
            radius_max_pixels=22,
            pickable=True,
        )
        view_state = pdk.ViewState(
            latitude=float(map_df['lat'].mean()),
            longitude=float(map_df['lon'].mean()),
            zoom=7.5,
            pitch=0
        )
        st.pydeck_chart(
            pdk.Deck(
                map_style='light',
                layers=[layer],
                initial_view_state=view_state,
                tooltip={"html": "<b>מיקום:</b> {loc}<br/><b>סטטוס:</b> {hazard_level}<br/><b>חומרה:</b> {sev}<br/><b>תאריך:</b> {date_str}"}
            ),
            width='stretch'
        )
    else:
        st.info("אין אירועים עם נקודות ציון גאוגרפיות תקינות להצגה במפה עבור הסינון שנבחר.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------ שורה 4: גרפי ניתוח ------------------
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("<h5 style='text-align: right;'>📈 התפלגות אירועים לפי רמת חומרה</h5>", unsafe_allow_html=True)
        sev_counts = df_view['sev'].value_counts().reset_index()
        sev_counts.columns = ['רמת חומרה', 'כמות']
        fig_sev = px.pie(sev_counts, names='רמת חומרה', values='כמות', hole=0.4)
        fig_sev.update_layout(margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_sev, width='stretch')

    with g2:
        st.markdown("<h5 style='text-align: right;'>🚗 סוגי כלי רכב מעורבים (Top 10)</h5>", unsafe_allow_html=True)
        all_vehs = [veh_map.get(str(v).lower().strip(), str(v)) for sublist in df_view['vehs'] if isinstance(sublist, list) for v in sublist]
        if all_vehs:
            veh_counts = pd.Series(all_vehs).value_counts().head(10).reset_index()
            veh_counts.columns = ['סוג רכב', 'כמות']
            fig_veh = px.bar(veh_counts, x='כמות', y='סוג רכב', orientation='h', color_discrete_sequence=['#1976D2'])
            fig_veh.update_layout(yaxis={'categoryorder': 'total ascending'}, margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_veh, width='stretch')
        else:
            st.info("אין נתוני כלי רכב להצגה בסינון הנוכחי.")

    # ------------------ שורה 5: טבלת פירוט אירועים ------------------
    with st.expander("📋 צפייה בטבלת האירועים המסוננים"):
        display_df = df_view[['pub_date', 'source', 'loc', 'sev', 'hazard_level', 'cluster_count', 'raw_text']].copy()
        display_df.columns = ['תאריך פרסום', 'מקור', 'מיקום', 'חומרה', 'מדד רמזור', 'מספר אירועים באשכול', 'טקסט דיווח']
        st.dataframe(display_df.sort_values(by='תאריך פרסום', ascending=False), width='stretch')

except Exception as e:
    st.error(f"שגיאה בטעינת הדשבורד: {e}")
