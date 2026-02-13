# Pipeline de Crédito — Dashboard Python 🐍

Dashboard analítico de crédito e risco, construído em **Python** com **Streamlit**, **Pandas**, **Plotly** e **SQLite**.

> Portfolio project — versão Python do dashboard React original.

## 🚀 Quick Start

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Popular o banco SQLite (executa apenas uma vez)
python setup_database.py

# 3. Iniciar o dashboard
streamlit run app.py
```

O banco SQLite será criado automaticamente em `data/credito.db` a partir dos CSVs na raiz do projeto.

## 📁 Estrutura

```
dashboard-python/
├── app.py                 ← Entrada principal + filtros
├── pages/
│   ├── 1_visao_geral.py   ← Panorama Executivo
│   └── 2_credito_risco.py ← Saúde e Risco
├── utils/
│   ├── database.py        ← Conexão SQLite + queries
│   └── calculations.py    ← Cálculos e agregações
├── assets/
│   └── style.css          ← Tema dark/gold premium
├── data/
│   └── credito.db         ← Banco SQLite (gerado)
├── setup_database.py      ← Script de importação CSV → SQLite
└── requirements.txt
```

## 📊 Funcionalidades

- **Filtros dinâmicos**: Ano, Mês, Gênero, Tipo de Contrato, Faixa Etária
- **Métricas**: Volume Total, Ticket Médio, Contratos, Taxa de Inadimplência
- **Gráficos**: Evolução temporal, distribuição por renda/idade, gauge de risco, heatmap
- **Segmentos Críticos**: Top 5 combinações escolaridade × renda com maior risco

## 🛠️ Stack

| Componente | Tecnologia   |
| ---------- | ------------ |
| Framework  | Streamlit    |
| Dados      | Pandas       |
| Gráficos   | Plotly       |
| Banco      | SQLite       |
| Linguagem  | Python 3.10+ |

## 📝 Licença

Projeto acadêmico/portfolio.
