"""
Database — Conexão e queries SQLite
"""
import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "credito.db")


def get_connection():
    """Retorna conexão SQLite."""
    return sqlite3.connect(DB_PATH)


def db_exists():
    """Verifica se o banco existe."""
    return os.path.exists(DB_PATH)


def query_application_data(filters: dict = None) -> pd.DataFrame:
    """
    Busca dados de application_data com filtros opcionais.
    
    filters: {
        'year': str ('todos' ou '2023'),
        'month': str ('todos' ou '1'-'12'),
        'gender': str ('todos' ou 'M'/'F'),
        'contractType': str ('todos' ou valor),
        'ageRange': str ('todos' ou valor),
    }
    """
    conn = get_connection()
    
    query = "SELECT * FROM application_data WHERE 1=1"
    params = []
    
    if filters:
        # Filtro de ano
        year = filters.get("year", "todos")
        if year and year != "todos":
            query += " AND data_registro >= ? AND data_registro <= ?"
            params.extend([f"{year}-01-01", f"{year}-12-31"])
            
            # Filtro de mês (só se ano específico)
            month = filters.get("month", "todos")
            if month and month != "todos":
                m = int(month)
                start = f"{year}-{m:02d}-01"
                if m == 12:
                    end = f"{int(year)+1}-01-01"
                else:
                    end = f"{year}-{m+1:02d}-01"
                # Substituir os filtros de ano pelo intervalo mais restrito
                query = "SELECT * FROM application_data WHERE data_registro >= ? AND data_registro < ?"
                params = [start, end]
        
        # Gênero
        gender = filters.get("gender", "todos")
        if gender and gender != "todos":
            query += " AND genero = ?"
            params.append(gender)
        
        # Tipo contrato
        contract = filters.get("contractType", "todos")
        if contract and contract != "todos":
            query += " AND tipo_contrato = ?"
            params.append(contract)
        
        # Faixa etária
        age = filters.get("ageRange", "todos")
        if age and age != "todos":
            query += " AND faixa_etaria = ?"
            params.append(age)
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def query_all_application_data() -> pd.DataFrame:
    """Busca todos os dados sem filtro (para cálculos globais)."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM application_data", conn)
    conn.close()
    return df


def query_previous_application() -> pd.DataFrame:
    """Busca dados de previous_application."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM previous_application", conn)
    conn.close()
    return df


def get_year_range() -> tuple:
    """Retorna (min_year, max_year) dos dados."""
    conn = get_connection()
    result = conn.execute(
        "SELECT MIN(substr(data_registro, 1, 4)), MAX(substr(data_registro, 1, 4)) FROM application_data WHERE data_registro IS NOT NULL"
    ).fetchone()
    conn.close()
    if result and result[0]:
        return int(result[0]), int(result[1])
    return 2000, 2023
