"""
Página 1 — Panorama Executivo (Visão Geral)
"""
import streamlit as st
import plotly.graph_objects as go
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.database import query_application_data
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

# Cores e Estilos
TEAL = "#04BDAC"
GOLD_TEXT = "#D4AF37"
BG_COLOR = "#011114"

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#888", size=11, family="Inter"),
    margin=dict(l=0, r=0, t=20, b=20),
    xaxis=dict(showgrid=False, zeroline=False, showline=True, linecolor="#333"),
    yaxis=dict(showgrid=False, zeroline=False, showline=False),
)

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

# --- HEADER (Oculto visualmente pois o layout é focado nos cards) ---
# st.title("Panorama Executivo") 

# --- CARDS HTML CORRIGIDOS ---
def card_html(icon, title, value, badge_text, badge_color="rgba(4, 189, 172, 0.2)"):
    return f"""
    <div class="custom-card">
        <div>
            <div class="card-icon">{icon}</div>
            <div class="card-title">{title}</div>
            <div class="card-value">{value}</div>
        </div>
        <div class="card-badge">{badge_text}</div>
    </div>
    """

col1, col2, col3, col4 = st.columns(4)

with col1:
    val_fmt = f"R$ {vol['total_volume']:,.0f}".replace(",", ".")
    st.markdown(card_html("💵", "VOLUME TOTAL", val_fmt, f"{eficiencia:.1f}%"), unsafe_allow_html=True)

with col2:
    ticket_fmt = f"R$ {ticket:,.0f}".replace(",", ".")
    st.markdown(card_html("🏷️", "TICKET MÉDIO", ticket_fmt, "Médio"), unsafe_allow_html=True)

with col3:
    st.markdown(card_html("📄", "TOTAL DE CONTRATOS", str(total), "Contratos"), unsafe_allow_html=True)

with col4:
    inad_fmt = f"{inadimplencia:.2f}%"
    st.markdown(card_html("⚠️", "TAXA INADIMPLÊNCIA", inad_fmt, "Atenção"), unsafe_allow_html=True)


# --- GRÁFICO PRINCIPAL ---
st.markdown("""
<div class="chart-container">
    <div class="section-title">Qual a evolução do nosso volume estratégico?</div>
    <div class="section-subtitle">EVOLUÇÃO DO VOLUME AO LONGO DO TEMPO</div>
</div>
""", unsafe_allow_html=True)

evo = calculate_temporal_evolution(df)

if not evo.empty:
    fig_evo = go.Figure()

    # Linha Suave (Spline)
    fig_evo.add_trace(go.Scatter(
        x=evo["label"], y=evo["volume"],
        mode="lines+markers",
        name="Volume",
        line=dict(color="#E0C068", width=2, shape='spline', smoothing=1.3),
        marker=dict(size=6, color="#E0C068", line=dict(width=1, color="#111")),
    ))
    
    fig_evo.update_layout(
        **PLOT_LAYOUT,
        height=400,
        hovermode="x unified",
        xaxis=dict(
            tickfont=dict(color="#666"), 
            showgrid=False
        ),
        yaxis=dict(
            visible=True, 
            tickfont=dict(color="#666"),
            tickprefix="R$ "
        ),
        showlegend=False
    )
    st.plotly_chart(fig_evo, use_container_width=True)
else:
    st.info("Sem dados temporais para exibir.")

# --- OUTROS GRÁFICOS (mantidos simples por enquanto) ---
st.markdown("<br>", unsafe_allow_html=True)
c_left, c_right = st.columns(2)

with c_left:
    st.markdown('<div class="section-title" style="font-size:1.2rem">Volume por Renda</div>', unsafe_allow_html=True)
    renda = group_by_field(df, "tipo_renda")
    if not renda.empty:
        fig_r = go.Figure(go.Bar(
            x=renda.head(5)["value"], y=renda.head(5)["label"], orientation='h',
            marker=dict(color="#E0C068")
        ))
        fig_r.update_layout(**PLOT_LAYOUT, height=250, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_r, use_container_width=True)

with c_right:
    st.markdown('<div class="section-title" style="font-size:1.2rem">Faixa Etária</div>', unsafe_allow_html=True)
    age = calculate_age_distribution(df)
    if not age.empty:
        fig_p = go.Figure(go.Pie(
            labels=age["faixa_etaria"], values=age["quantidade"], hole=0.7,
            marker=dict(colors=["#E0C068", "#C9A55C", "#8B7355", "#5C4D38"])
        ))
        fig_p.update_layout(**PLOT_LAYOUT, height=250, showlegend=False)
        st.plotly_chart(fig_p, use_container_width=True)
