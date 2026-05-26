"""
Scouting Dashboard — Premier League 2024-25
Ejecutar: streamlit run app.py
"""
import warnings
warnings.filterwarnings('ignore')

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import math

# ── Configuración ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Scouting Dashboard · PL 2024-25",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).parent / 'data' / 'players.csv'

DARK = '#1a1a2e'
MID  = '#12122a'
BLUE = '#4472C4'
RED  = '#FF6B6B'
GRN  = '#50C878'
YEL  = '#FFD700'
ORG  = '#FF8C00'
POS_COLORS = {'GK': ORG, 'DF': BLUE, 'MF': GRN, 'FW': RED}

# ── Métricas disponibles ──────────────────────────────────────────────────────
METRICS_LABELS = {
    'Per 90 Minutes_Gls':  'Goles / 90',
    'Per 90 Minutes_Ast':  'Asistencias / 90',
    'Standard_Sh/90':      'Tiros / 90',
    'Standard_SoT/90':     'Tiros a puerta / 90',
    'Standard_SoT%':       'Precisión tiro %',
    'Standard_G/Sh':       'Goles por tiro',
    'TklW_p90':            'Tackles ganados / 90',
    'Int_p90':             'Intercepciones / 90',
    'Performance_Fls':     'Faltas cometidas',
    'Performance_Fld':     'Faltas recibidas',
}

POS_METRICS = {
    'GK': ['Int_p90', 'TklW_p90', 'Performance_Fls'],
    'DF': ['TklW_p90', 'Int_p90', 'Standard_Sh/90',
           'Performance_Fld', 'Performance_Fls'],
    'MF': ['TklW_p90', 'Int_p90', 'Per 90 Minutes_Ast',
           'Standard_Sh/90', 'Performance_Fld'],
    'FW': ['Per 90 Minutes_Gls', 'Per 90 Minutes_Ast',
           'Standard_Sh/90', 'Standard_SoT/90',
           'Standard_G/Sh', 'Standard_SoT%'],
}

# ── Carga de datos ────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    if not DATA_PATH.exists():
        return None
    df = pd.read_csv(DATA_PATH)
    # Convertir columnas numéricas
    for col in df.columns:
        if col not in ['league', 'season', 'team', 'player', 'pos', 'age']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df


def label(col):
    return METRICS_LABELS.get(col, col.replace('_', ' '))


# ── Estilos de gráficos ───────────────────────────────────────────────────────
def dark_fig(fig, title=''):
    fig.update_layout(
        paper_bgcolor=DARK, plot_bgcolor=MID,
        font_color='white', title_text=title,
        title_font_size=14, title_font_color='white',
        legend=dict(bgcolor='rgba(0,0,0,0)', font_color='white'),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    fig.update_xaxes(color='white', gridcolor='#2a2a4a', zerolinecolor='#2a2a4a')
    fig.update_yaxes(color='white', gridcolor='#2a2a4a', zerolinecolor='#2a2a4a')
    return fig


def percentile_bar_chart(row, metrics, pos):
    valid  = [m for m in metrics if m in row.index and f'pct_{m}' in row.index]
    if not valid:
        return None
    labels = [label(m) for m in valid]
    pcts   = [float(row[f'pct_{m}']) if not pd.isna(row[f'pct_{m}']) else 0 for m in valid]
    raws   = [round(float(row[m]), 2) if not pd.isna(row[m]) else 0 for m in valid]
    colors = [GRN if p >= 66 else YEL if p >= 33 else RED for p in pcts]

    fig = go.Figure(go.Bar(
        x=pcts, y=labels, orientation='h',
        marker_color=colors,
        text=[f'{r}  ({p:.0f}°)' for r, p in zip(raws, pcts)],
        textposition='outside', textfont_color='white',
        hovertemplate='%{y}: <b>%{x:.0f}° percentil</b><extra></extra>',
    ))
    fig.add_vline(x=50, line_dash='dot', line_color='rgba(255,255,255,0.27)')
    fig.update_xaxes(range=[0, 120])
    return dark_fig(fig, f'Perfil de percentiles — {pos}')


def radar_chart(row, metrics):
    valid = [m for m in metrics if m in row.index and f'pct_{m}' in row.index]
    if not valid:
        return None
    N = len(valid)
    angles = [n / N * 2 * math.pi for n in range(N)]
    angles += angles[:1]
    vals = [min(float(row[f'pct_{m}']) / 100, 1.0) if not pd.isna(row[f'pct_{m}']) else 0 for m in valid]
    vals += vals[:1]
    theta = [label(m) for m in valid] + [label(valid[0])]

    fig = go.Figure(go.Scatterpolar(
        r=vals, theta=theta,
        fill='toself', fillcolor='rgba(68,114,196,0.3)',
        line_color=BLUE, name=row['player'],
    ))
    fig.update_layout(
        polar=dict(
            bgcolor=MID,
            radialaxis=dict(visible=True, range=[0, 1],
                            color='#aaaaaa', gridcolor='#333366'),
            angularaxis=dict(color='white', gridcolor='#333366'),
        ),
        showlegend=False,
        paper_bgcolor=DARK, font_color='white',
        margin=dict(l=60, r=60, t=60, b=60),
    )
    return fig


def beeswarm_fig(df, metric, highlight=None, pos_filter='Todos'):
    dft = df.dropna(subset=[metric]).copy()
    if pos_filter != 'Todos':
        dft = dft[dft['pos'] == pos_filter]
    dft = dft.sort_values(metric).reset_index(drop=True)
    np.random.seed(42)
    dft['y_jitter'] = np.random.uniform(-0.4, 0.4, len(dft))

    fig = go.Figure()
    for pos, grp in dft.groupby('pos'):
        sizes   = grp['player'].apply(lambda p: 14 if p == highlight else 7)
        opacity = grp['player'].apply(lambda p: 1.0 if p == highlight else 0.65)
        lwidths = grp['player'].apply(lambda p: 2   if p == highlight else 0)
        fig.add_trace(go.Scatter(
            x=grp[metric], y=grp['y_jitter'],
            mode='markers',
            marker=dict(color=POS_COLORS.get(pos, BLUE),
                        size=list(sizes), opacity=list(opacity),
                        line=dict(color='white', width=list(lwidths))),
            text=grp['player'] + '<br>' + grp['team'],
            hovertemplate='<b>%{text}</b><br>' + label(metric) + ': %{x:.2f}<extra></extra>',
            name=pos,
        ))

    if highlight:
        row = dft[dft['player'] == highlight]
        if not row.empty:
            fig.add_annotation(
                x=float(row[metric].iloc[0]),
                y=float(row['y_jitter'].iloc[0]) + 0.42,
                text=f'<b>{highlight}</b>',
                showarrow=True, arrowcolor='white',
                font=dict(color='white', size=11), bgcolor=DARK,
            )

    fig.update_yaxes(showticklabels=False, showgrid=False)
    return dark_fig(fig, f'Distribución: {label(metric)}')


def find_similar(df, player_name, n=8):
    pos = df.loc[df['player'] == player_name, 'pos'].values[0]
    pool = df[df['pos'] == pos].copy()
    num_cols = [c for c in pool.columns
                if not c.startswith('pct_')
                and c not in ['league', 'season', 'team', 'player', 'pos', 'age']
                and pd.api.types.is_numeric_dtype(pool[c])]
    X = StandardScaler().fit_transform(pool[num_cols].fillna(0))
    local_idx = pool.reset_index(drop=True)[pool['player'].values == player_name].index[0]
    sims = cosine_similarity(X[local_idx:local_idx+1], X)[0]
    pool = pool.reset_index(drop=True)
    pool['similarity'] = sims
    return pool[pool['player'] != player_name].nlargest(n, 'similarity')[
        ['player', 'team', 'pos', 'similarity']
    ].to_dict('records')


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    st.markdown(
        f'<style>.stApp{{background-color:{DARK};}}</style>',
        unsafe_allow_html=True,
    )

    st.sidebar.title("⚽ Scouting Dashboard")
    st.sidebar.caption("Premier League 2024-25 · FBref")

    df = load_data()
    if df is None:
        st.error("No se encontraron datos. Ejecuta `python data_prep.py` primero.")
        st.stop()

    pagina = st.sidebar.radio(
        "Sección",
        ["Visión General", "Perfil de Jugador", "Beeswarm", "Jugadores Similares"],
    )

    st.sidebar.divider()
    min_min = st.sidebar.slider("Minutos mínimos", 100, 2000, 300, 100)
    df_fil  = df[df['Playing Time_Min'] >= min_min].copy()
    st.sidebar.caption(f"{len(df_fil)} jugadores")

    # ── VISIÓN GENERAL ────────────────────────────────────────────────────────
    if pagina == "Visión General":
        st.title("Visión General — Premier League 2024-25")

        goleador = df_fil.nlargest(1, 'Performance_Gls')
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Jugadores", len(df_fil))
        col2.metric("Equipos", df_fil['team'].nunique())
        col3.metric("Máx. Goles", f"{int(goleador['Performance_Gls'].iloc[0])}  ({goleador['player'].iloc[0]})")
        col4.metric("Máx. Tiros/90", f"{df_fil['Standard_Sh/90'].max():.2f}")

        st.divider()

        metric_opts = {label(k): k for k in METRICS_LABELS if k in df_fil.columns}
        c1, c2 = st.columns(2)
        with c1:
            sel_label  = st.selectbox("Métrica:", list(metric_opts.keys()))
        with c2:
            pos_sel = st.selectbox("Posición:", ['Todas', 'GK', 'DF', 'MF', 'FW'])

        sel_col = metric_opts[sel_label]
        dft = df_fil.copy()
        if pos_sel != 'Todas':
            dft = dft[dft['pos'] == pos_sel]

        top10 = dft.nlargest(10, sel_col).reset_index(drop=True)
        top10.index += 1

        ca, cb = st.columns([1, 1])
        with ca:
            st.dataframe(
                top10[['player', 'team', 'pos', sel_col]].rename(
                    columns={sel_col: sel_label}
                ),
                use_container_width=True,
            )
        with cb:
            fig = px.bar(
                top10[::-1], x=sel_col, y='player', orientation='h',
                color='pos', color_discrete_map=POS_COLORS,
                labels={sel_col: sel_label, 'player': ''},
            )
            dark_fig(fig)
            st.plotly_chart(fig, use_container_width=True)

    # ── PERFIL DE JUGADOR ─────────────────────────────────────────────────────
    elif pagina == "Perfil de Jugador":
        st.title("Perfil de Jugador")

        player = st.selectbox("Selecciona un jugador:",
                              sorted(df_fil['player'].unique().tolist()))
        row = df_fil[df_fil['player'] == player].iloc[0]
        pos = str(row['pos'])

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Equipo",   row['team'])
        c2.metric("Posición", pos)
        c3.metric("Minutos",  int(row['Playing Time_Min']))
        c4.metric("Goles",    int(row.get('Performance_Gls', 0)))
        c5.metric("Asist.",   int(row.get('Performance_Ast', 0)))
        st.divider()

        metrics = [m for m in POS_METRICS.get(pos, list(METRICS_LABELS)) if m in row.index]

        cl, cr = st.columns([3, 2])
        with cl:
            fig = percentile_bar_chart(row, metrics, pos)
            if fig:
                fig.update_layout(height=380)
                st.plotly_chart(fig, use_container_width=True)
        with cr:
            fig = radar_chart(row, metrics)
            if fig:
                fig.update_layout(height=380)
                st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "Verde = top 33%  ·  Amarillo = medio tercio  ·  Rojo = tercio inferior  "
            f"(comparado con jugadores de la misma posición con >= {min_min} min)"
        )

    # ── BEESWARM ──────────────────────────────────────────────────────────────
    elif pagina == "Beeswarm":
        st.title("Beeswarm — Distribución por Métrica")
        st.caption("Cada punto es un jugador. Pasa el cursor para ver el nombre y equipo.")

        metric_opts = {label(k): k for k in METRICS_LABELS if k in df_fil.columns}
        c1, c2, c3 = st.columns(3)
        with c1:
            sel_label  = st.selectbox("Métrica:", list(metric_opts.keys()))
        with c2:
            pos_filter = st.selectbox("Posición:", ['Todos', 'GK', 'DF', 'MF', 'FW'])
        with c3:
            highlight  = st.selectbox(
                "Destacar jugador:",
                ['—'] + sorted(df_fil['player'].unique().tolist()),
            )

        sel_col = metric_opts[sel_label]
        hl      = None if highlight == '—' else highlight

        np.random.seed(42)
        fig = beeswarm_fig(df_fil, sel_col, hl, pos_filter)
        fig.update_layout(height=430)
        st.plotly_chart(fig, use_container_width=True)

        dft = df_fil.dropna(subset=[sel_col])
        if pos_filter != 'Todos':
            dft = dft[dft['pos'] == pos_filter]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Mediana", f"{dft[sel_col].median():.2f}")
        c2.metric("Media",   f"{dft[sel_col].mean():.2f}")
        c3.metric("Máximo",  f"{dft[sel_col].max():.2f}")
        c4.metric("Mínimo",  f"{dft[sel_col].min():.2f}")

        if hl:
            val = df_fil.loc[df_fil['player'] == hl, sel_col]
            pct = df_fil.loc[df_fil['player'] == hl, f'pct_{sel_col}']
            if not val.empty and not pct.empty:
                st.info(
                    f"**{hl}** — {label(sel_col)}: **{float(val.iloc[0]):.2f}** "
                    f"(percentil **{float(pct.iloc[0]):.0f}°** en su posición)"
                )

    # ── JUGADORES SIMILARES ───────────────────────────────────────────────────
    elif pagina == "Jugadores Similares":
        st.title("Jugadores Similares")
        st.caption(
            "Similitud de coseno sobre todas las métricas numéricas, "
            "comparando jugadores de la misma posición."
        )

        c1, c2 = st.columns([3, 1])
        with c1:
            player = st.selectbox("Jugador de referencia:",
                                  sorted(df_fil['player'].unique().tolist()))
        with c2:
            n_sim = st.slider("Nº similares:", 3, 12, 6)

        row = df_fil[df_fil['player'] == player].iloc[0]
        pos = str(row['pos'])
        st.markdown(
            f"**Posición:** {pos} · **Equipo:** {row['team']} · "
            f"**Minutos:** {int(row['Playing Time_Min'])} · "
            f"**Goles:** {int(row.get('Performance_Gls',0))} · "
            f"**Asist.:** {int(row.get('Performance_Ast',0))}"
        )

        similar = find_similar(df_fil, player, n_sim)

        cl, cr = st.columns([1, 1])
        with cl:
            fig = go.Figure(go.Bar(
                x=[r['similarity'] for r in similar],
                y=[f"{r['player']} ({r['team'][:10]})" for r in similar],
                orientation='h', marker_color=BLUE,
                text=[f"{r['similarity']:.3f}" for r in similar],
                textposition='outside', textfont_color='white',
            ))
            fig.update_xaxes(range=[0, 1.1])
            dark_fig(fig, f'Jugadores más similares a {player}')
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

        with cr:
            sim_df = pd.DataFrame(similar).rename(columns={
                'player': 'Jugador', 'team': 'Equipo',
                'pos': 'Pos.', 'similarity': 'Similitud',
            })
            sim_df['Similitud'] = sim_df['Similitud'].round(3)
            st.dataframe(sim_df, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Comparativa directa de métricas")
        metrics = [m for m in POS_METRICS.get(pos, list(METRICS_LABELS)) if m in df_fil.columns]
        comp_names = [player] + [r['player'] for r in similar[:4]]
        comp = df_fil[df_fil['player'].isin(comp_names)][['player', 'team'] + metrics].copy()
        comp = comp.set_index('player').round(2)
        comp.columns = ['Equipo'] + [label(m) for m in metrics]
        st.dataframe(comp, use_container_width=True)


if __name__ == '__main__':
    main()
