"""
Setup Database — Importa CSVs para SQLite local
Execute: python setup_database.py
"""
import sqlite3
import pandas as pd
import os
import sys

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "credito.db")

CSV_APPLICATION = os.path.join(DATA_DIR, "application_data_ptbr.csv")
CSV_PREVIOUS = os.path.join(DATA_DIR, "previous_application_ptbr.csv")


def create_database():
    """Cria o banco SQLite e importa os CSVs."""
    os.makedirs(DATA_DIR, exist_ok=True)

    # Verificar se os CSVs existem
    for csv_path in [CSV_APPLICATION, CSV_PREVIOUS]:
        if not os.path.exists(csv_path):
            print(f"[ERROR] Arquivo nao encontrado: {csv_path}")
            sys.exit(1)

    print("[INFO] Lendo CSVs...")

    # --- application_data ---
    df_app = pd.read_csv(CSV_APPLICATION)

    # Renomear colunas para snake_case minúsculo
    col_map_app = {
        "ID_CLIENTE_ATUAL": "id_cliente_atual",
        "ALVO_INADIMPLENCIA": "alvo_inadimplencia",
        "TIPO_CONTRATO": "tipo_contrato",
        "GENERO": "genero",
        "POSSUI_CARRO": "possui_carro",
        "POSSUI_IMOVEL": "possui_imovel",
        "QTD_FILHOS": "qtd_filhos",
        "RENDA_TOTAL": "renda_total",
        "VALOR_CREDITO": "valor_credito",
        "VALOR_ANUIDADE": "valor_anuidade",
        "VALOR_BENS": "valor_total_bem",
        "TIPO_ACOMPANHANTE": "tipo_acompanhante",
        "TIPO_RENDA": "tipo_renda",
        "ESCOLARIDADE": "escolaridade",
        "ESTADO_CIVIL": "estado_civil",
        "TIPO_MORADIA": "tipo_moradia",
        "IDADE_ANOS": "idade_anos",
        "FAIXA_ETARIA": "faixa_etaria",
        "DATA_REGISTRO_PTBR": "data_registro_raw",
    }
    # Aplicar renomeação (só colunas que existem)
    df_app = df_app.rename(columns={k: v for k, v in col_map_app.items() if k in df_app.columns})

    # Converter data DD/MM/YYYY -> YYYY-MM-DD
    if "data_registro_raw" in df_app.columns:
        df_app["data_registro"] = pd.to_datetime(
            df_app["data_registro_raw"], format="%d/%m/%Y", errors="coerce"
        ).dt.strftime("%Y-%m-%d")
        df_app = df_app.drop(columns=["data_registro_raw"])
    else:
        print("[WARN] Coluna DATA_REGISTRO_PTBR nao encontrada no CSV")

    print(f"  [OK] application_data: {len(df_app)} registros, {len(df_app.columns)} colunas")

    # --- previous_application ---
    df_prev = pd.read_csv(CSV_PREVIOUS)

    col_map_prev = {
        "ID_CLIENTE_ANTERIOR": "id_cliente_anterior",
        "ID_CLIENTE_ATUAL": "id_cliente_atual",
        "TIPO_CONTRATO": "tipo_contrato",
        "VALOR_ANUIDADE": "valor_anuidade",
        "VALOR_SOLICITADO": "valor_solicitado",
        "VALOR_CREDITO": "valor_credito",
        "VALOR_ENTRADA": "valor_entrada",
        "VALOR_BENS": "valor_bens",
        "STATUS_CONTRATO": "status_contrato",
        "CANAL_VENDA": "canal_venda",
        "CATEGORIA_BENS": "categoria_bens",
        "DATA_DECISAO_PTBR": "data_decisao_raw",
    }
    df_prev = df_prev.rename(columns={k: v for k, v in col_map_prev.items() if k in df_prev.columns})

    if "data_decisao_raw" in df_prev.columns:
        df_prev["data_decisao"] = pd.to_datetime(
            df_prev["data_decisao_raw"], format="%d/%m/%Y", errors="coerce"
        ).dt.strftime("%Y-%m-%d")
        df_prev = df_prev.drop(columns=["data_decisao_raw"])

    print(f"  [OK] previous_application: {len(df_prev)} registros, {len(df_prev.columns)} colunas")

    # --- Gravar no SQLite ---
    print(f"\n[INFO] Gravando em {DB_PATH}...")

    conn = sqlite3.connect(DB_PATH)
    df_app.to_sql("application_data", conn, if_exists="replace", index=False)
    df_prev.to_sql("previous_application", conn, if_exists="replace", index=False)

    # Criar indices para performance
    conn.execute("CREATE INDEX IF NOT EXISTS idx_app_data_registro ON application_data(data_registro)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_app_tipo_contrato ON application_data(tipo_contrato)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_app_genero ON application_data(genero)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_app_faixa_etaria ON application_data(faixa_etaria)")

    conn.commit()
    conn.close()

    print("[OK] Banco de dados criado com sucesso!")
    print(f"     Caminho: {DB_PATH}")


if __name__ == "__main__":
    create_database()
