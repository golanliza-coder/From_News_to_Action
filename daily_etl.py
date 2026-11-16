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
}
div[data-baseweb="tag"] { background-color: #B3E5FC !important; color: #01579B !important; border-radius: 6px !important; }
div[data-baseweb="tag"] svg { fill: #01579B !important; }
div[data-baseweb="select"] > div:focus-within { border-color: #0288D1 !important; box-shadow: 0 0 0 1px #0288D1 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<h1 style='text-align: center; display: flex; align-items: center; justify-content: center; gap: 12px; color: #0D47A1;'>
    <span>From News To Action</span>
    <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#0288D1" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle>
        <circle cx="12" cy="12" r="2"></circle><line x1="12" y1="2" x2="12" y2="6"></line>
    </svg>
</h1>
<h3 style='text-align: center;'>מערכת אג'נטית לניתוח והשלמת נתוני תאונות דרכים עבור הנהלת הרלב"ד</h3><hr>
""", unsafe_allow_html=True)

sev_map = {
    'moderate': 'בינונית', 'not specified': 'לא מצוין', 'not_specified': 'לא מצוין',
    'severe': 'קשה / קטלנית', 'fatal': 'קטלנית', 'hard': 'קשה',
    'medium': 'בינונית', 'light': 'קלה', 'mild': 'קלה', 'unknown': 'לא מצוין'
}
sev_rank = {'קטלנית': 5, 'קשה / קטלנית': 4, 'קשה': 3, 'בינונית': 2, 'קלה': 1, 'לא מצוין': 0}
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

def deduplicate_incidents(df):
    if df.empty:
        return df
    df = df.sort_values('pub_date').reset_index(drop=True)
    merged_rows, used = [], set()
    for i in range(len(df)):
        if i in used:
            continue
        base = df.iloc[i].to_dict()
        sources = [s.strip() for s in str(base['source']).split(',') if s.strip()]
        raw_texts = [base['raw_text']]
        vehs = list(base['vehs']) if isinstance(base['vehs'], list) else []
        vulns = set(base['vulns']) if isinstance(base['vulns'], list) else set()

        if pd.notna(base['lat']) and pd.notna(base['lon']) and pd.notna(base['pub_date']):
            lat1, lon1, t1 = np.radians(base['lat']), np.radians(base['lon']), base['pub_date']
            for j in range(i + 1, len(df)):
                if j in used:
                    continue
                cand = df.iloc[j]
                if pd.isna(cand['lat']) or pd.isna(cand['lon']) or pd.isna(cand['pub_date']):
                    continue
                if abs((cand['pub_date'] - t1).total_seconds()) / 3600.0 > 3.0:
                    break
                lat2, lon2 = np.radians(cand['lat']), np.radians(cand['lon'])
                dlat, dlon = lat2 - lat1, lon2 - lon1
                a = np.sin(dlat / 2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0)**2
                if 6371000 * 2 * np.arcsin(np.sqrt(a)) <= 500:
                    used.add(j)
                    for s in str(cand['source']).split(','):
                        if s.strip() and s.strip() not in sources:
                            sources.append(s.strip())
                    if sev_rank.get(cand['sev'], 0) > sev_rank.get(base['sev'], 0):
                        base['sev'] = cand['sev']
                    if isinstance(cand['vehs'], list):
                        for v in cand['vehs']:
                            if v not in vehs:
                                vehs.append(v)
                    if isinstance(cand['vulns'], list):
                        vulns.update(cand['vulns'])
                    if cand['raw_text'] and cand['raw_text'] not in raw_texts:
                        raw_texts.append(f"[{cand['source']}]: {cand['raw_text']}")

        base['source'], base['vehs'], base['vulns'] = ", ".join(sources), vehs, list(vulns)
        base['has_2w'] = base['has_2w'] or any(k in " ".join(str(v).lower() for v in vehs) for k in two_wheel_keys)
        base['has_vru'] = len(vulns) > 0
        base['raw_text'] = " | ".join(raw_texts)
        merged_rows.append(base)
    return pd.DataFrame(merged_rows)

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
            'id': r['id'], 'source': r['source'], 'pub_date': pd.to_datetime(r['published_date']),
            'sev': sev, 'loc': d.get('verbal_location') or d.get('resolved_address') or 'לא מצוין',
            'lat': lat, 'lon': lon, 'vehs': vehs, 'vulns': vulns,
            'has_2w': has_2w, 'has_vru': len(vulns) > 0, 'raw_text': d.get('raw_text', '')
        })
    df_clean = deduplicate_incidents(pd.DataFrame(rows).drop_duplicates(subset=['id']))
    return compute_spatial_anomaly(df_clean)
try:
    df_all = load_data()

    # ------------------ סרגל סינון אינטראקטיבי בצד ------------------
    st.sidebar.header("🔍 סרגל סינון נתונים")
    min_d, max_d = df_all['pub_date'].min().date(), df_all['pub_date'].max().date()
    date_range = st.sidebar.date_input("טווח תאריכים", value=(min_d, max_d), min_value=min_d, max_value=max_d)

    sev_opts = sorted(df_all['sev'].unique().tolist())
    sel_sev = st.sidebar.multiselect("רמת חומרה", options=sev_opts, default=sev_opts)

    all_sources = sorted({s.strip() for src in df_all['source'].dropna() for s in str(src).split(',') if s.strip()})
    sel_src = st.sidebar.multiselect("ערוץ מקור", options=all_sources, default=all_sources)

    haz_opts = sorted(df_all['hazard_level'].unique().tolist())
    sel_haz = st.sidebar.multiselect("מדד רמזור", options=haz_opts, default=haz_opts)

    # החלת מסננים
    mask = pd.Series(True, index=df_all.index)
    if isinstance(date_range, tuple) and len(date_range) == 2:
        mask &= (df_all['pub_date'].dt.date >= date_range[0]) & (df_all['pub_date'].dt.date <= date_range[1])
    if sel_sev:
        mask &= df_all['sev'].isin(sel_sev)
    if sel_src:
        mask &= df_all['source'].apply(lambda x: any(s.strip() in sel_src for s in str(x).split(',')))
    if sel_haz:
        mask &= df_all['hazard_level'].isin(sel_haz)

    df_f = df_all[mask].copy()

    # ------------------ כרטיסי KPI עליונים ------------------
    c1, c2, c3, c4 = st.columns(4)
    total_acc = len(df_f)
    red_cnt = int((df_f['cluster_count'] >= 3).sum())
    tw_pct = (df_f['has_2w'].mean() * 100) if total_acc > 0 else 0.0
    vru_pct = (df_f['has_vru'].mean() * 100) if total_acc > 0 else 0.0

    c1.markdown(f"<div class='kpi-card'><h4>סה\"כ אירועים ייחודיים</h4><h2>{total_acc}</h2></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='kpi-card'><h4>🔴 מוקדי סיכון אדומים (3+)</h4><h2 style='color:#D32F2F;'>{red_cnt}</h2></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='kpi-card'><h4>🛵 מעורבות דו-גלגלי</h4><h2>{tw_pct:.1f}%</h2></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='kpi-card'><h4>🚶 פגיעות ב-VRU</h4><h2>{vru_pct:.1f}%</h2></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------ תרשימים ומפת מוקדים ------------------
    g1, g2 = st.columns(2)
    with g1:
        st.subheader("התפלגות חומרת תאונות")
        fig_sev = px.pie(df_f, names='sev', hole=0.45, color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig_sev, use_container_width=True)

    with g2:
        st.subheader("אירועים לפי מדד רמזור")
        haz_df = df_f['hazard_level'].value_counts().reset_index()
        haz_df.columns = ['מדד רמזור', 'כמות']
        fig_haz = px.bar(haz_df, x='מדד רמזור', y='כמות', color='מדד רמזור',
                         color_discrete_map={
                             '🔴 אדום - התרעת אנומליה מרחבית (3+)': '#D32F2F',
                             '🟠 כתום - אזהרה (2 אירועים)': '#F57C00',
                             '🟢 תקין (אירוע בודד)': '#2E7D32'
                         })
        st.plotly_chart(fig_haz, use_container_width=True)

    map_df = df_f.dropna(subset=['lat', 'lon'])
    if not map_df.empty:
        st.subheader("🗺️ מפת מוקדי סיכון בזמן אמת")
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position='[lon, lat]',
            get_color='[r, g, b, 200]',
            get_radius=350,
            pickable=True,
        )
        view_state = pdk.ViewState(latitude=31.8, longitude=34.9, zoom=7.5)
        st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state,
                                 tooltip={"text": "מיקום: {loc}\nחומרה: {sev}\nרמזור: {hazard_level}"}))

    # ------------------ טבלת האירועים המסוננים ------------------
    st.subheader("📋 צפייה בטבלת האירועים המסוננים")
    disp_df = df_f[['id', 'pub_date', 'source', 'loc', 'sev', 'hazard_level', 'cluster_count', 'raw_text']].sort_values('pub_date', ascending=False)
    disp_df.columns = ['מזהה', 'תאריך פרסום', 'מקור', 'מיקום', 'חומרה', 'מדד רמזור', 'מספר אירועים במוקד', 'טקסט דיווח']
    st.dataframe(disp_df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"אירעה שגיאה בטעינת הדשבורד: {e}")
