"""
Página 1 — Panorama Executivo (Visão Geral)
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.database import query_application_data, query_all_application_data
from utils.calculations import (
    calculate_volume,
    calculate_ticket_medio,
    count_contratos,
    calculate_taxa_inadimplencia,
    calculate_taxa_eficiencia,
    calculate_temporal_evolution,
    calculate_age_distribution,
    group_by_field,
)

st.set_page_config(page_title="Panorama Executivo", page_icon="📊", layout="wide")

# CSS
CSS_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
if os.path.exists(CSS_PATH):
    with open(CSS_PATH) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Plotly theme defaults
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#999", size=12),
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis=dict(gridcolor="rgba(201,165,92,0.1)", showline=False),
    yaxis=dict(gridcolor="rgba(201,165,92,0.1)", showline=False),
)

GOLD = "#C9A55C"
GOLD_DARK = "#8B7355"

# Pegar filtros
filters = st.session_state.get("filters", {
    "year": "todos", "month": "todos", "gender": "todos",
    "contractType": "todos", "ageRange": "todos",
})


@st.cache_data(ttl=60)
def load_data(filter_key):
    """Carrega dados com cache."""
    return query_application_data(filters)


df = load_data(str(filters))

if df.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

# --- Cálculos ---
vol = calculate_volume(df)
ticket = calculate_ticket_medio(df)
total = count_contratos(df)
inadimplencia = calculate_taxa_inadimplencia(df)
eficiencia = calculate_taxa_eficiencia(df)

# --- HEADER ---
st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <h1 style="font-family: 'Playfair Display', serif; font-size: 2rem; color: white; margin: 0;">
        Panorama Executivo
    </h1>
    <p style="color: rgba(201,165,92,0.6); font-size: 0.7rem; text-transform: uppercase; 
              letter-spacing: 0.15em; font-weight: 600; margin-top: 0.3rem;">
        Visão Geral de Crédito
    </p>
</div>
""", unsafe_allow_html=True)

# --- MÉTRICAS ---
def fmt_currency(val):
    """Formata valor em R$."""
    if val >= 1_000_000:
        return f"R$ {val/1_000_000:.1f}M"
    elif val >= 1_000:
        return f"R$ {val/1_000:.0f}k"
    return f"R$ {val:.0f}"


c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Volume Total", fmt_currency(vol["total_volume"]), f"{eficiencia:.1f}% eficiência")
c2.metric("🎫 Ticket Médio", fmt_currency(ticket), "Médio")
c3.metric("📄 Total de Contratos", f"{total:,}".replace(",", "."), "Contratos")
c4.metric("⚠️ Taxa Inadimplência", f"{inadimplencia:.2f}%", "Saudável" if inadimplencia < 5 else "Atenção")

st.markdown("---")

# --- GRÁFICO: Evolução Temporal ---
st.markdown("""
<div style="margin-bottom: 1rem;">
    <h2 style="font-family: 'Playfair Display', serif; font-size: 1.5rem; color: white; margin: 0;">
        Qual a evolução do nosso volume estratégico?
    </h2>
    <p style="color: rgba(201,165,92,0.5); font-size: 0.65rem; text-transform: uppercase; 
              letter-spacing: 0.12em; font-weight: 600;">
        Evolução do Volume ao Longo do Tempo
    </p>
</div>
""", unsafe_allow_html=True)

evo = calculate_temporal_evolution(df)

if not evo.empty:
    fig_evo = go.Figure()
    fig_evo.add_trace(go.Scatter(
        x=evo["label"], y=evo["volume"],
        mode="lines+markers", name="Volume (R$)",
        line=dict(color=GOLD, width=2),
        marker=dict(color=GOLD, size=6),
    ))
    fig_evo.add_trace(go.Scatter(
        x=evo["label"], y=evo["quantidade"],
        mode="lines+markers", name="Quantidade",
        line=dict(color=GOLD_DARK, width=2),
        marker=dict(color=GOLD_DARK, size=5),
        yaxis="y2",
    ))
    fig_evo.update_layout(
        **PLOT_LAYOUT,
        height=380,
        yaxis=dict(title="Volume (R$)", titlefont=dict(color=GOLD), tickfont=dict(color="#999"),
                   gridcolor="rgba(201,165,92,0.08)"),
        yaxis2=dict(title="Quantidade", titlefont=dict(color=GOLD_DARK), tickfont=dict(color="#999"),
                    overlaying="y", side="right", gridcolor="rgba(0,0,0,0)"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5,
                    font=dict(color=GOLD, size=11)),
        hovermode="x unified",
    )
    st.plotly_chart(fig_evo, use_container_width=True)
else:
    st.info("Sem dados temporais para exibir.")

st.markdown("---")

# --- BOTTOM GRID ---
col_left, col_right = st.columns(2)

# Volume por Tipo de Renda
with col_left:
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h2 style="font-family: 'Playfair Display', serif; font-size: 1.3rem; color: white; margin: 0;">
            Como o volume se distribui por renda?
        </h2>
        <p style="color: rgba(201,165,92,0.5); font-size: 0.65rem; text-transform: uppercase; 
                  letter-spacing: 0.12em; font-weight: 600;">
            Volume por Tipo de Renda
        </p>
    </div>
    """, unsafe_allow_html=True)

    renda = group_by_field(df, "tipo_renda")
    if not renda.empty:
        renda_top = renda.head(6)
        fig_renda = go.Figure(go.Bar(
            x=renda_top["value"],
            y=renda_top["label"],
            orientation="h",
            marker=dict(color=GOLD, line=dict(width=0)),
        ))
        fig_renda.update_layout(**PLOT_LAYOUT, height=320, showlegend=False,
                                yaxis=dict(autorange="reversed", categoryorder="total ascending"))
        st.plotly_chart(fig_renda, use_container_width=True)

# Distribuição por Faixa Etária
with col_right:
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h2 style="font-family: 'Playfair Display', serif; font-size: 1.3rem; color: white; margin: 0;">
            Quem compõe nossa carteira?
        </h2>
        <p style="color: rgba(201,165,92,0.5); font-size: 0.65rem; text-transform: uppercase; 
                  letter-spacing: 0.12em; font-weight: 600;">
            Distribuição por Faixa Etária
        </p>
    </div>
    """, unsafe_allow_html=True)

    age_dist = calculate_age_distribution(df)
    if not age_dist.empty:
        colors = [GOLD, GOLD_DARK, "#D4AF37", "#B8860B", "#DAA520", "#A07830"]
        fig_pie = go.Figure(go.Pie(
            labels=age_dist["faixa_etaria"],
            values=age_dist["quantidade"],
            hole=0.55,
            marker=dict(colors=colors[:len(age_dist)]),
            textinfo="label+percent",
            textfont=dict(color="white", size=11),
        ))
        fig_pie.update_layout(**PLOT_LAYOUT, height=350, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)
