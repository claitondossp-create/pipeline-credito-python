"""
Página 2 — Saúde e Risco (Crédito & Risco)
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.database import query_application_data, query_all_application_data
from utils.calculations import (
    calculate_taxa_inadimplencia,
    calculate_age_distribution,
    generate_risk_heatmap,
    get_top_critical_segments,
    count_contratos,
)

st.set_page_config(page_title="Saúde e Risco", page_icon="⚠️", layout="wide")

# CSS
CSS_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
if os.path.exists(CSS_PATH):
    with open(CSS_PATH) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#999", size=12),
    margin=dict(l=20, r=20, t=30, b=20),
)

GOLD = "#C9A55C"
META = 8.0  # Meta de inadimplência

# Pegar filtros
filters = st.session_state.get("filters", {
    "year": "todos", "month": "todos", "gender": "todos",
    "contractType": "todos", "ageRange": "todos",
})


@st.cache_data(ttl=60)
def load_data(filter_key):
    return query_application_data(filters)


df = load_data(str(filters))

if df.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
    st.stop()

inadimplencia = calculate_taxa_inadimplencia(df)
total_contratos = count_contratos(df)
inadimplentes = int((df["alvo_inadimplencia"] == 1).sum()) if "alvo_inadimplencia" in df.columns else 0

# --- HEADER ---
st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <h1 style="font-family: 'Playfair Display', serif; font-size: 2rem; color: white; margin: 0;">
        Saúde e Risco
    </h1>
    <p style="color: rgba(201,165,92,0.6); font-size: 0.7rem; text-transform: uppercase; 
              letter-spacing: 0.15em; font-weight: 600; margin-top: 0.3rem;">
        Análise de Inadimplência
    </p>
</div>
""", unsafe_allow_html=True)

# --- TOP ROW ---
col_gauge, col_badges = st.columns([1, 2])

with col_gauge:
    st.markdown("""
    <div style="margin-bottom: 0.5rem;">
        <h3 style="font-family: 'Playfair Display', serif; font-size: 1.2rem; color: white;">Indicador Geral</h3>
        <p style="color: rgba(201,165,92,0.5); font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.12em;">
            Taxa de inadimplência vs Meta
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Gauge Chart
    if inadimplencia <= 5:
        gauge_color = "#22C55E"
    elif inadimplencia <= 8:
        gauge_color = "#EAB308"
    else:
        gauge_color = "#EF4444"

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=inadimplencia,
        number=dict(suffix="%", font=dict(size=36, color="white")),
        delta=dict(reference=META, suffix="%", decreasing=dict(color="#22C55E"), increasing=dict(color="#EF4444")),
        gauge=dict(
            axis=dict(range=[0, 15], tickfont=dict(color="#666"), dtick=3),
            bar=dict(color=gauge_color),
            bgcolor="rgba(201,165,92,0.05)",
            bordercolor="rgba(201,165,92,0.2)",
            steps=[
                dict(range=[0, 5], color="rgba(34,197,94,0.1)"),
                dict(range=[5, 8], color="rgba(234,179,8,0.1)"),
                dict(range=[8, 15], color="rgba(239,68,68,0.1)"),
            ],
            threshold=dict(line=dict(color=GOLD, width=3), thickness=0.8, value=META),
        ),
    ))
    fig_gauge.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#999"),
        height=280, margin=dict(l=30, r=30, t=30, b=10),
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Stats
    st.markdown(f"""
    <div style="border-top: 1px solid rgba(201,165,92,0.15); padding-top: 0.8rem; margin-top: 0.5rem;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
            <span style="color: #999; font-size: 0.8rem;">Total Contratos:</span>
            <span style="color: white; font-weight: bold; font-size: 0.8rem;">{total_contratos:,}</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span style="color: #999; font-size: 0.8rem;">Inadimplentes:</span>
            <span style="color: #EF4444; font-weight: bold; font-size: 0.8rem;">{inadimplentes:,}</span>
        </div>
    </div>
    """.replace(",", "."), unsafe_allow_html=True)

with col_badges:
    st.markdown("""
    <div style="margin-bottom: 0.8rem;">
        <h3 style="font-family: 'Playfair Display', serif; font-size: 1.2rem; color: white;">
            Indicadores de Risco Relativo
        </h3>
        <p style="color: rgba(201,165,92,0.5); font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.12em;">
            Status por dimensão de análise
        </p>
    </div>
    """, unsafe_allow_html=True)

    b1, b2 = st.columns(2)
    with b1:
        st.markdown("""
        <div style="background: linear-gradient(to right, rgba(34,197,94,0.08), transparent);
                    border: 1px solid rgba(34,197,94,0.25); border-radius: 12px; padding: 1rem; margin-bottom: 0.8rem;">
            <p style="color: #999; font-size: 0.65rem; text-transform: uppercase; margin: 0;">Risco Baixo</p>
            <p style="color: #22C55E; font-size: 1.1rem; font-weight: bold; margin: 0.2rem 0;">Superior Assalariado</p>
            <p style="color: #666; font-size: 0.7rem; margin: 0;">Taxa: 2.1% | Volume Seguro</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background: linear-gradient(to right, rgba(239,68,68,0.08), transparent);
                    border: 1px solid rgba(239,68,68,0.25); border-radius: 12px; padding: 1rem;">
            <p style="color: #999; font-size: 0.65rem; text-transform: uppercase; margin: 0;">Risco Alto</p>
            <p style="color: #EF4444; font-size: 1.1rem; font-weight: bold; margin: 0.2rem 0;">Fundamental Empresário</p>
            <p style="color: #666; font-size: 0.7rem; margin: 0;">Taxa: 12.5% | Ação Imediata</p>
        </div>
        """, unsafe_allow_html=True)

    with b2:
        st.markdown("""
        <div style="background: linear-gradient(to right, rgba(234,179,8,0.08), transparent);
                    border: 1px solid rgba(234,179,8,0.25); border-radius: 12px; padding: 1rem; margin-bottom: 0.8rem;">
            <p style="color: #999; font-size: 0.65rem; text-transform: uppercase; margin: 0;">Risco Médio</p>
            <p style="color: #EAB308; font-size: 1.1rem; font-weight: bold; margin: 0.2rem 0;">Médio Autônomo</p>
            <p style="color: #666; font-size: 0.7rem; margin: 0;">Taxa: 6.1% | Monitoramento</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background: linear-gradient(to right, rgba(201,165,92,0.08), transparent);
                    border: 1px solid rgba(201,165,92,0.25); border-radius: 12px; padding: 1rem;">
            <p style="color: #999; font-size: 0.65rem; text-transform: uppercase; margin: 0;">Meta Global</p>
            <p style="color: #C9A55C; font-size: 1.1rem; font-weight: bold; margin: 0.2rem 0;">{META}% Inadimplência</p>
            <p style="color: #666; font-size: 0.7rem; margin: 0;">Objetivo: Abaixo de {META}% em todos segmentos</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# --- HEATMAP ---
st.markdown("""
<div style="margin-bottom: 1rem;">
    <h2 style="font-family: 'Playfair Display', serif; font-size: 1.5rem; color: white; margin: 0;">
        Onde está concentrado o risco?
    </h2>
    <p style="color: rgba(201,165,92,0.5); font-size: 0.65rem; text-transform: uppercase; 
              letter-spacing: 0.12em; font-weight: 600;">
        Matriz de Calor: Escolaridade × Tipo de Renda
    </p>
</div>
""", unsafe_allow_html=True)

heatmap_data = generate_risk_heatmap(df)

if not heatmap_data.empty:
    fig_heat = go.Figure(go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns.tolist(),
        y=heatmap_data.index.tolist(),
        colorscale=[
            [0, "rgba(34,197,94,0.3)"],
            [0.5, "rgba(234,179,8,0.5)"],
            [1, "rgba(239,68,68,0.8)"],
        ],
        text=[[f"{v:.1f}%" for v in row] for row in heatmap_data.values],
        texttemplate="%{text}",
        textfont=dict(size=10, color="white"),
        hovertemplate="Escolaridade: %{y}<br>Renda: %{x}<br>Inadimplência: %{z:.1f}%<extra></extra>",
        colorbar=dict(title="Taxa %", tickfont=dict(color="#999"), titlefont=dict(color=GOLD)),
    ))
    fig_heat.update_layout(
        **PLOT_LAYOUT, height=380,
        xaxis=dict(tickfont=dict(size=9, color="#999"), tickangle=-45),
        yaxis=dict(tickfont=dict(size=10, color="#999")),
    )
    st.plotly_chart(fig_heat, use_container_width=True)
else:
    st.info("Sem dados para o heatmap.")

st.markdown("---")

# --- BOTTOM ROW ---
col_seg, col_age = st.columns(2)

with col_seg:
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h2 style="font-family: 'Playfair Display', serif; font-size: 1.3rem; color: white; margin: 0;">
            Quais segmentos exigem atenção?
        </h2>
        <p style="color: rgba(201,165,92,0.5); font-size: 0.65rem; text-transform: uppercase; 
                  letter-spacing: 0.12em; font-weight: 600;">
            Top 5 Segmentos Mais Críticos
        </p>
    </div>
    """, unsafe_allow_html=True)

    segments = get_top_critical_segments(df)
    if not segments.empty:
        for idx, row in segments.iterrows():
            taxa = row["taxa_inadimplencia"]
            if taxa >= 10:
                color = "#EF4444"
            elif taxa >= 7:
                color = "#EAB308"
            else:
                color = "#22C55E"

            rank = segments.index.get_loc(idx) + 1
            st.markdown(f"""
            <div style="background: rgba(0,0,0,0.3); border: 1px solid rgba(201,165,92,0.1);
                        border-radius: 10px; padding: 0.8rem 1rem; margin-bottom: 0.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.2rem; font-weight: 900; color: rgba(201,165,92,0.3);">#{rank}</span>
                        <span style="font-size: 0.8rem; font-weight: bold; color: white;">{row['segmento']}</span>
                    </div>
                    <span style="font-size: 1rem; font-weight: 900; color: {color};">{taxa:.2f}%</span>
                </div>
                <div style="display: flex; gap: 1rem; font-size: 0.7rem; color: #666;">
                    <span>Contratos: {int(row['qtd_contratos']):,}</span>
                    <span>Volume: R$ {row['volume_exposto']/1000:.0f}k</span>
                </div>
            </div>
            """.replace(",", "."), unsafe_allow_html=True)
    else:
        st.info("Sem dados de segmentos críticos.")

with col_age:
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h2 style="font-family: 'Playfair Display', serif; font-size: 1.3rem; color: white; margin: 0;">
            Como a idade influencia?
        </h2>
        <p style="color: rgba(201,165,92,0.5); font-size: 0.65rem; text-transform: uppercase; 
                  letter-spacing: 0.12em; font-weight: 600;">
            Taxa de Inadimplência por Faixa Etária
        </p>
    </div>
    """, unsafe_allow_html=True)

    age_risk = calculate_age_distribution(df)
    if not age_risk.empty:
        fig_age = go.Figure(go.Bar(
            x=age_risk["taxa_inadimplencia"],
            y=age_risk["faixa_etaria"],
            orientation="h",
            marker=dict(color="#EF4444", line=dict(width=0)),
            text=[f"{v:.1f}%" for v in age_risk["taxa_inadimplencia"]],
            textposition="outside",
            textfont=dict(color="#EF4444", size=11),
        ))
        fig_age.update_layout(
            **PLOT_LAYOUT, height=300, showlegend=False,
            yaxis=dict(autorange="reversed", categoryorder="array",
                       categoryarray=age_risk["faixa_etaria"].tolist()),
            xaxis=dict(title="Taxa de Inadimplência (%)"),
        )
        st.plotly_chart(fig_age, use_container_width=True)
    else:
        st.info("Sem dados por faixa etária.")
