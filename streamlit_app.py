import streamlit as st
import pandas as pd
import numpy as np
import psycopg
import json
import plotly.express as px
import pydeck as pdk
import ast

conn_str = st.secrets["DATABASE_URL"]

st.markdown("""
<style>
.stApp, [data-testid="stHeader"] { background-color: #E3F2FD; }
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
""", unsafe_allow_html=True)

st.title("🚨 From News To Action")
st.subheader("מערכת אג'נטית לניתוח והשלמת נתוני תאונות דרכים עבור הנהלת הרלב\"ד")
st.markdown("---")

sev_map = {'moderate': 'בינונית', 'not specified': 'לא מצוין', 'not_specified': 'לא מצוין', 'severe': 'קשה / קטלנית', 'fatal': 'קטלנית', 'hard': 'קשה', 'medium': 'בינונית', 'light': 'קלה', 'mild': 'קלה', 'unknown': 'לא מצוין'}
veh_map = {'car': 'רכב פרטי', 'bus': 'אוטובוס', 'motorcycle': 'אופנוע', 'tractor': 'טרקטור', 'bicycle': 'אופניים', 'truck': 'משאית', 'electric scooter': 'קורקינט חשמלי', 'e-scooter': 'קורקינט חשמלי', 'minibus': 'מיניבוס', 'train': 'רכבת', 'electric bicycle': 'אופניים חשמליים', 'e-bike': 'אופניים חשמליים', 'mobility scooter': 'קלנועית', 'excavator': 'מחפר / כלי הנדסי', 'scooter': 'קטנוע', 'commercial vehicle': 'רכב מסחרי'}
two_wheel_keys = ('motorcycle', 'scooter', 'bicycle', 'e-bike', 'e-scooter', 'אופנוע', 'קורקינט', 'אופניים', 'קטנוע')

def classify_vuln(raw_v, v_list):
    cats = set()
    t = str(raw_v).lower() if raw_v else ""
    if t and t not in ('none', 'not specified', 'לא מצוין', '[]', 'nan'):
        if any(w in t for w in ('pedestrian', 'הולך רגל', 'הולכת רגל', 'הולכי רגל')): cats.add('הולכי רגל')
        if any(w in t for w in ('child', 'kid', 'boy', 'girl', 'teen', 'youth', 'ילד', 'ילדה', 'נער', 'נערה', 'בן 1', 'בת 1')): cats.add('ילדים ובני נוער (0-18)')
        if any(w in t for w in ('70', '80', '90', '65', 'elderly', 'senior', 'קשיש', 'קשישה', 'מבוגר')): cats.add('אזרחים ותיקים (60+)')
    if isinstance(v_list, list):
        vs = " ".join(str(v).lower() for v in v_list)
        if any(w in vs for w in two_wheel_keys): cats.add('רוכבי דו-גלגלי / מיקרו-מוביליטי')
    return list(cats)

def compute_spatial_anomaly(df):
    df['cluster_count'], df['suspected__hazard'] = 1, False
    df['hazard_level'] = '🟢 תקין (אירוע בודד)'
    df['r'], df['g'], df['b'] = 46, 125, 50
    valid_mask = (df['lat'].notna() & df['lon'].notna() & df['pub_date'].notna() & (~df['loc'].str.lower().isin(('not specified', 'לא מצוין', 'לא פוענח', 'none', ''))) & (~((df['lat'].round(4) == 32.0927) & (df['lon'].round(4) == 34.8465))))
    valid = df[valid_mask].copy()
    if valid.empty: return df
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
            if not (29.0 <= lat <= 33.5 and 34.0 <= lon <= 36.0): lat, lon = None, None
        except: lat, lon = None, None
        vehs = d.get('vehicle_types') or d.get('involved_vehicles') or []
        if isinstance(vehs, str) and vehs.startswith('['):
            try: vehs = ast.literal_eval(vehs)
            except: vehs = []
        vulns = classify_vuln(d.get('vulnerable_users_and_ages') or d.get('vulnerable_road_users'), vehs)
        has_2w = any(k in " ".join(str(v).lower() for v in vehs) for k in two_wheel_keys) if isinstance(vehs, list) else False
        rows.append({'id': r['id'], 'source': r['source'], 'pub_date': pd.to_datetime(r['published_date']), 'sev': sev, 'loc': d.get('verbal_location') or d.get('resolved_address') or 'לא מצוין', 'lat': lat, 'lon': lon, 'vehs': vehs, 'vulns': vulns, 'has_2w': has_2w, 'has_vru': len(vulns) > 0, 'raw_text': d.get('raw_text', '')})
    return compute_spatial_anomaly(pd.DataFrame(rows).drop_duplicates(subset=['id']))
try:
    df_all = load_data()

    active_f = st.query_params.get("f", "ALL")

    # ------------------ סרגל סינון אינטראקטיבי בצד ------------------
    st.sidebar.header("🔍 סרגל סינון נתונים")
    min_d, max_d = df_all['pub_date'].min().date(), df_all['pub_date'].max().date()
    date_range = st.sidebar.date_input("טווח תאריכים", value=(min_d, max_d), min_value=min_d, max_value=max_d)
    sel_sev = st.sidebar.multiselect("רמת חומרה", options=df_all['sev'].unique().tolist(), default=df_all['sev'].unique().tolist())
    sel_src = st.sidebar.multiselect("ערוץ מקור", options=df_all['source'].unique().tolist(), default=df_all['source'].unique().tolist())
    only_red = st.sidebar.checkbox("הצג מוקדי אנומליה אדומים בלבד (3+)", value=False)

    if active_f != 'ALL':
        if st.sidebar.button("🔄 נקה סינון כרטיסייה (הצג הכל)", use_container_width=True):
            st.query_params.clear()
            st.rerun()

    df_base = df_all[df_all['sev'].isin(sel_sev) & df_all['source'].isin(sel_src)].copy()
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_d, end_d = date_range
        df_base = df_base[(df_base['pub_date'].dt.date >= start_d) & (df_base['pub_date'].dt.date <= end_d)]
    if only_red:
        df_base = df_base[df_base['suspected__hazard']]

    total_base = len(df_base)
    fatal_cnt = len(df_base[df_base['sev'].isin(('קטלנית', 'קשה / קטלנית', 'קשה'))])
    cnt_2w = int(df_base['has_2w'].sum())
    cnt_vru = int(df_base['has_vru'].sum())
    pct_2w = round((cnt_2w / total_base) * 100) if total_base else 0
    pct_vru = round((cnt_vru / total_base) * 100) if total_base else 0

    # ------------------ שורה 1: 5 מדדי מפתח בעיצוב HTML אחיד ומדויק ------------------
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(f"<div class='kpi-card'><div style='font-weight:700;font-size:0.95rem;'>💀 קטלניות / קשות</div><div style='font-weight:800;font-size:1.85rem;margin-top:4px;'>{fatal_cnt}</div></div>", unsafe_allow_html=True)

    next_2w = "ALL" if active_f == "2W" else "2W"
    bg_2w = "background-color:#BBDEFB;border-color:#1565C0;" if active_f == "2W" else ""
    c2.markdown(f"<a href='?f={next_2w}' target='_self' class='click-card' style='{bg_2w}'><span style='display:block;font-weight:700;font-size:0.95rem;'>🛵 מעורבות דו-גלגלי</span><span style='display:block;font-weight:800;font-size:1.85rem;margin-top:4px;'>{pct_2w}% ({cnt_2w})</span></a>", unsafe_allow_html=True)

    next_vru = "ALL" if active_f == "VRU" else "VRU"
    bg_vru = "background-color:#BBDEFB;border-color:#1565C0;" if active_f == "VRU" else ""
    c3.markdown(f"<a href='?f={next_vru}' target='_self' class='click-card' style='{bg_vru}'><span style='display:block;font-weight:700;font-size:0.95rem;'>🚶‍♂️ אוכלוסיות סיכון</span><span style='display:block;font-weight:800;font-size:1.85rem;margin-top:4px;'>{pct_vru}% ({cnt_vru})</span></a>", unsafe_allow_html=True)

    c4.markdown(f"<div class='meta-card'><div style='font-weight:800;font-size:0.95rem;color:#0D47A1;'>📱 מקורות מידע</div><div style='font-weight:900;font-size:1.95rem;color:#0D47A1;margin-top:4px;'>{df_base['source'].nunique()}</div></div>", unsafe_allow_html=True)
    c5.markdown(f"<div class='meta-card'><div style='font-weight:800;font-size:0.95rem;color:#0D47A1;'>📊 סה''כ אירועים</div><div style='font-weight:900;font-size:1.95rem;color:#0D47A1;margin-top:4px;'>{total_base}</div></div>", unsafe_allow_html=True)

    df = df_base.copy()
    if active_f == '2W':
        df = df[df['has_2w']]
        st.info(f"🛵 **מסנן פעיל:** מציג כעת אך ורק **{len(df)}** תאונות שבהן מעורבים כלי רכב דו-גלגליים / מיקרו-מוביליטי. (לחצו שוב על הכרטיסייה כדי לבטל)")
    elif active_f == 'VRU':
        df = df[df['has_vru']]
        st.info(f"🚶‍♂️ **מסנן פעיל:** מציג כעת אך ורק **{len(df)}** תאונות שבהן נפגעו משתמשי דרך פגיעים (ילדים, קשישים, הולכי רגל או דו-גלגלי). (לחצו שוב על הכרטיסייה כדי לבטל)")

    st.markdown("#### 🚦 מדד רמזור: התרעות אנומליה מרחבית (רדיוס 500 מ' / 90 יום)")
    r1, r2, r3 = st.columns(3)
    r1.markdown(f"<div class='kpi-card' style='border-top: 6px solid #D32F2F; padding: 16px;'><div style='color:#D32F2F;font-weight:800;font-size:1.1rem;'>🔴 אנומליה מרחבית (3+)</div><div style='margin:6px 0;color:#B71C1C;font-weight:900;font-size:2rem;'>{int((df['cluster_count'] >= 3).sum())}</div><div style='font-size:0.85rem;color:#444;'><b>suspected__hazard = True</b></div></div>", unsafe_allow_html=True)
    r2.markdown(f"<div class='kpi-card' style='border-top: 6px solid #F57C00; padding: 16px;'><div style='color:#E65100;font-weight:800;font-size:1.1rem;'>🟠 רמת אזהרה (2)</div><div style='margin:6px 0;color:#E65100;font-weight:900;font-size:2rem;'>{int((df['cluster_count'] == 2).sum())}</div><div style='font-size:0.85rem;color:#444;'><b>2 תאונות ברדיוס 500 מ'</b></div></div>", unsafe_allow_html=True)
    r3.markdown(f"<div class='kpi-card' style='border-top: 6px solid #388E3C; padding: 16px;'><div style='color:#2E7D32;font-weight:800;font-size:1.1rem;'>🟢 תקין / בודד (1)</div><div style='margin:6px 0;color:#1B5E20;font-weight:900;font-size:2rem;'>{int((df['cluster_count'] == 1).sum())}</div><div style='font-size:0.85rem;color:#444;'><b>אירוע יחיד במרחב</b></div></div>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### 🗺️ פריסת אירועים ומוקדי אנומליה במרחב ישראל")
    layer = pdk.Layer('ScatterplotLayer', df.dropna(subset=['lat', 'lon']), get_position='[lon, lat]', get_color='[r, g, b]', get_radius=2500, pickable=True)
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=pdk.ViewState(latitude=31.5, longitude=34.8, zoom=7.2), map_style='light', tooltip={"text": "מיקום: {loc}\nחומרה: {sev}\nסטטוס: {hazard_level}"}))
    st.markdown("---")

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("### 📈 התפלגות חומרת התאונות")
        sc = df['sev'].value_counts().reset_index()
        sc.columns = ['sev', 'count']
        fig1 = px.bar(sc, x='sev', y='count', labels={'count': 'מספר תאונות', 'sev': 'רמת חומרה'}, color='sev', text='count', color_discrete_sequence=px.colors.sequential.Reds_r)
        fig1.update_traces(textposition='outside')
        fig1.update_layout(showlegend=False, paper_bgcolor='white', plot_bgcolor='white')
        st.plotly_chart(fig1, use_container_width=True)

    with col_g2:
        st.markdown("### 🚌 פילוח כלי רכב מעורבים")
        all_v = [v for vl in df['vehs'].dropna() for v in (vl if isinstance(vl, list) else [])]
        if all_v:
            vt = [veh_map.get(str(v).strip().lower(), str(v).strip()) for v in all_v if v and str(v).lower() not in ('none', 'not specified', 'unknown')]
            vc = pd.Series(vt).value_counts().reset_index()
            vc.columns = ['סוג רכב', 'מספר אזכורים']
            fig2 = px.bar(vc.sort_values('מספר אזכורים'), x='מספר אזכורים', y='סוג רכב', orientation='h', text='מספר אזכורים', color_discrete_sequence=['#0d47a1'])
            fig2.update_traces(textposition='outside')
            fig2.update_layout(yaxis_title="", showlegend=False, paper_bgcolor='white', plot_bgcolor='white')
            st.plotly_chart(fig2, use_container_width=True)
    st.markdown("---")

    st.markdown("### 👶👵 פיצול אוכלוסיות סיכון: ילדים ובני נוער מול אזרחים ותיקים")
    all_vu = [u for ul in df['vulns'].dropna() if isinstance(ul, list) for u in ul]
    kids_cnt = sum(1 for u in all_vu if 'ילדים' in u)
    seniors_cnt = sum(1 for u in all_vu if 'ותיקים' in u)
    ped_cnt = sum(1 for u in all_vu if 'הולכי רגל' in u)
    riders_cnt = sum(1 for u in all_vu if 'דו-גלגלי' in u)

    v1, v2, v3, v4 = st.columns(4)
    v1.markdown(f"<div class='kpi-card' style='border-right: 5px solid #1976D2;'><div style='font-weight:700;'>👶 ילדים ובני נוער (0-18)</div><div style='font-weight:900;font-size:1.8rem;color:#0D47A1;'>{kids_cnt}</div></div>", unsafe_allow_html=True)
    v2.markdown(f"<div class='kpi-card' style='border-right: 5px solid #7B1FA2;'><div style='font-weight:700;'>👵 אזרחים ותיקים (60+)</div><div style='font-weight:900;font-size:1.8rem;color:#4A148C;'>{seniors_cnt}</div></div>", unsafe_allow_html=True)
    v3.markdown(f"<div class='kpi-card' style='border-right: 5px solid #E65100;'><div style='font-weight:700;'>🚶 הולכי רגל</div><div style='font-weight:900;font-size:1.8rem;color:#BF360C;'>{ped_cnt}</div></div>", unsafe_allow_html=True)
    v4.markdown(f"<div class='kpi-card' style='border-right: 5px solid #00796B;'><div style='font-weight:700;'>🛵 רוכבי דו-גלגלי</div><div style='font-weight:900;font-size:1.8rem;color:#004D40;'>{riders_cnt}</div></div>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### 🚨 טבלת מוקדי אנומליה מרחבית אדומים (`suspected__hazard = True`)")
    red_df = df[df['suspected__hazard']].sort_values(by=['cluster_count', 'pub_date'], ascending=[False, False])
    if not red_df.empty:
        disp_df = red_df[['pub_date', 'loc', 'sev', 'cluster_count', 'source', 'raw_text']].copy()
        disp_df.columns = ['תאריך פרסום', 'מיקום / צומת', 'חומרה', 'תאונות ברדיוס 500 מ\'', 'מקור', 'תקציר הדיווח']
        st.dataframe(disp_df, use_container_width=True, hide_index=True)
    else:
        st.info("לא נמצאו מוקדים אדומים תחת תנאי הסינון שנבחרו.")

except Exception as e:
    st.error(f"שגיאה: {e}")
