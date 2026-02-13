"""
Pipeline Crédito — Dashboard Python (Streamlit)
Análise de crédito e risco com dados locais em SQLite
"""
import streamlit as st
import os
import sys

# Config
st.set_page_config(
    page_title="Pipeline Crédito — Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Injetar CSS customizado
CSS_PATH = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(CSS_PATH):
    with open(CSS_PATH) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Auto-setup do banco se não existir
sys.path.insert(0, os.path.dirname(__file__))
from utils.database import db_exists

if not db_exists():
    st.warning("⚠️ Banco de dados não encontrado. Configurando...")
    from setup_database import create_database
    create_database()
    st.success("✅ Banco criado com sucesso! Recarregue a página.")
    st.stop()

# --- SIDEBAR (Filtros Globais) ---
st.sidebar.markdown("# 💰 Pipeline Crédito")
st.sidebar.markdown("---")

from utils.database import get_year_range

min_year, max_year = get_year_range()

# Filtro de Ano
st.sidebar.markdown("##### 📅 Período")
use_all_years = st.sidebar.checkbox("Todos os anos", value=False)

if use_all_years:
    selected_year = "todos"
else:
    selected_year = str(st.sidebar.slider(
        "Ano",
        min_value=min_year,
        max_value=max_year,
        value=max_year,
        step=1,
    ))

# Filtro de Mês
MONTHS = [
    ("todos", "Todos"),
    ("1", "Janeiro"), ("2", "Fevereiro"), ("3", "Março"),
    ("4", "Abril"), ("5", "Maio"), ("6", "Junho"),
    ("7", "Julho"), ("8", "Agosto"), ("9", "Setembro"),
    ("10", "Outubro"), ("11", "Novembro"), ("12", "Dezembro"),
]
month_labels = [m[1] for m in MONTHS]
month_values = [m[0] for m in MONTHS]

if selected_year == "todos":
    selected_month = "todos"
    st.sidebar.selectbox("Mês", ["Todos (desabilitado para 'Todos os anos')"], disabled=True)
else:
    month_idx = st.sidebar.selectbox("Mês", range(len(month_labels)), format_func=lambda i: month_labels[i])
    selected_month = month_values[month_idx]

st.sidebar.markdown("---")
st.sidebar.markdown("##### 🎯 Segmentação")

# Gênero
GENDERS = [("todos", "Todos"), ("M", "Masculino"), ("F", "Feminino")]
gender_idx = st.sidebar.selectbox("Gênero", range(len(GENDERS)), format_func=lambda i: GENDERS[i][1])
selected_gender = GENDERS[gender_idx][0]

# Tipo de Contrato
CONTRACTS = [("todos", "Todos"), ("CASH LOANS", "Cash Loans"), ("REVOLVING LOANS", "Revolving Loans")]
contract_idx = st.sidebar.selectbox("Tipo de Contrato", range(len(CONTRACTS)), format_func=lambda i: CONTRACTS[i][1])
selected_contract = CONTRACTS[contract_idx][0]

# Faixa Etária
AGE_RANGES = [("todos", "Todas"), ("<25", "< 25 anos"), ("25-35", "25-35 anos"), ("35-45", "35-45 anos"), ("45-60", "45-60 anos"), ("60+", "60+ anos"), (">60", "> 60 anos")]
age_idx = st.sidebar.selectbox("Faixa Etária", range(len(AGE_RANGES)), format_func=lambda i: AGE_RANGES[i][1])
selected_age = AGE_RANGES[age_idx][0]

# Guardar filtros no session_state
st.session_state["filters"] = {
    "year": selected_year,
    "month": selected_month,
    "gender": selected_gender,
    "contractType": selected_contract,
    "ageRange": selected_age,
}

# --- PÁGINA PRINCIPAL ---
st.markdown("""
<div style="text-align: center; padding: 3rem 0 1rem 0;">
    <h1 style="font-size: 2.5rem; color: #C9A55C; margin-bottom: 0.5rem; 
               font-family: 'Playfair Display', serif; letter-spacing: 0.03em;">
        💰 Pipeline de Crédito
    </h1>
    <p style="color: rgba(201,165,92,0.6); font-size: 0.8rem; text-transform: uppercase; 
              letter-spacing: 0.15em; font-weight: 600;">
        Dashboard Analítico de Crédito e Risco
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Cards informativos
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background: rgba(201,165,92,0.05); border: 1px solid rgba(201,165,92,0.15); 
                border-radius: 16px; padding: 2rem; text-align: center;">
        <p style="font-size: 2.5rem; margin-bottom: 0.5rem;">📊</p>
        <h3 style="color: #C9A55C; font-size: 1rem; margin-bottom: 0.5rem;">Panorama Executivo</h3>
        <p style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">
            Volume, ticket médio, evolução temporal e distribuições
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: rgba(201,165,92,0.05); border: 1px solid rgba(201,165,92,0.15); 
                border-radius: 16px; padding: 2rem; text-align: center;">
        <p style="font-size: 2.5rem; margin-bottom: 0.5rem;">⚠️</p>
        <h3 style="color: #C9A55C; font-size: 1rem; margin-bottom: 0.5rem;">Saúde e Risco</h3>
        <p style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">
            Inadimplência, heatmaps e segmentos críticos
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background: rgba(201,165,92,0.05); border: 1px solid rgba(201,165,92,0.15); 
                border-radius: 16px; padding: 2rem; text-align: center;">
        <p style="font-size: 2.5rem; margin-bottom: 0.5rem;">🐍</p>
        <h3 style="color: #C9A55C; font-size: 1rem; margin-bottom: 0.5rem;">Feito em Python</h3>
        <p style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">
            Streamlit + Pandas + Plotly + SQLite
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")
st.markdown(
    '<p style="text-align: center; color: rgba(201,165,92,0.4); font-size: 0.7rem; letter-spacing: 0.1em;">'
    '← Use o menu lateral para navegar entre as páginas</p>',
    unsafe_allow_html=True,
)
