"""
Calculations — Port das funções de cálculo do JavaScript para Python/Pandas
"""
import pandas as pd
import numpy as np


def calculate_volume(df: pd.DataFrame) -> dict:
    """Calcula volume total e valor solicitado."""
    total_volume = df["valor_credito"].astype(float).sum() if "valor_credito" in df.columns else 0
    total_solicitado = df["valor_total_bem"].astype(float).sum() if "valor_total_bem" in df.columns else 0
    return {"total_volume": total_volume, "total_solicitado": total_solicitado}


def calculate_ticket_medio(df: pd.DataFrame) -> float:
    """Calcula ticket médio."""
    if df.empty or "valor_credito" not in df.columns:
        return 0
    return df["valor_credito"].astype(float).mean()


def count_contratos(df: pd.DataFrame) -> int:
    """Conta total de contratos."""
    return len(df)


def calculate_taxa_inadimplencia(df: pd.DataFrame) -> float:
    """Calcula taxa de inadimplência (%)."""
    if df.empty or "alvo_inadimplencia" not in df.columns:
        return 0
    inadimplentes = (df["alvo_inadimplencia"] == 1).sum()
    return (inadimplentes / len(df)) * 100


def calculate_taxa_eficiencia(df: pd.DataFrame) -> float:
    """Calcula taxa de eficiência (valor concedido / solicitado)."""
    if df.empty:
        return 0
    concedido = df["valor_credito"].astype(float).sum()
    solicitado = df["valor_total_bem"].astype(float).sum()
    if solicitado == 0:
        return 0
    return (concedido / solicitado) * 100


def calculate_risco_relativo(df_filtered: pd.DataFrame, df_global: pd.DataFrame) -> float:
    """Calcula risco relativo comparado à média global."""
    taxa_filtrada = calculate_taxa_inadimplencia(df_filtered)
    taxa_global = calculate_taxa_inadimplencia(df_global)
    if taxa_global == 0:
        return 0
    return taxa_filtrada / taxa_global


def calculate_temporal_evolution(df: pd.DataFrame, granularity: str = "auto") -> pd.DataFrame:
    """
    Calcula evolução temporal com granularidade dinâmica.
    granularity: 'auto', 'daily', 'monthly'
    """
    if df.empty or "data_registro" not in df.columns:
        return pd.DataFrame()

    df_work = df.copy()
    df_work["data_registro"] = pd.to_datetime(df_work["data_registro"], errors="coerce")
    df_work = df_work.dropna(subset=["data_registro"])

    if df_work.empty:
        return pd.DataFrame()

    # Determinar granularidade
    use_daily = granularity == "daily"
    if granularity == "auto":
        date_range = (df_work["data_registro"].max() - df_work["data_registro"].min()).days
        use_daily = date_range <= 60

    if use_daily:
        df_work["periodo"] = df_work["data_registro"].dt.strftime("%Y-%m-%d")
        df_work["label"] = df_work["data_registro"].dt.strftime("%d/%m")
    else:
        df_work["periodo"] = df_work["data_registro"].dt.strftime("%Y-%m")
        df_work["label"] = df_work["data_registro"].dt.strftime("%m/%Y")

    grouped = df_work.groupby("periodo").agg(
        label=("label", "first"),
        volume=("valor_credito", lambda x: x.astype(float).sum()),
        quantidade=("id_cliente_atual", "count"),
        inadimplentes=("alvo_inadimplencia", lambda x: (x == 1).sum()),
    ).reset_index()

    grouped = grouped.sort_values("periodo")
    grouped["taxa_inadimplencia"] = (grouped["inadimplentes"] / grouped["quantidade"]) * 100
    grouped["ticket_medio"] = grouped["volume"] / grouped["quantidade"]

    return grouped


def calculate_age_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula distribuição por faixa etária."""
    if df.empty or "faixa_etaria" not in df.columns:
        return pd.DataFrame()

    total = len(df)
    grouped = df.groupby("faixa_etaria").agg(
        quantidade=("id_cliente_atual", "count"),
        volume=("valor_credito", lambda x: x.astype(float).sum()),
        inadimplentes=("alvo_inadimplencia", lambda x: (x == 1).sum()),
    ).reset_index()

    grouped["percentual"] = (grouped["quantidade"] / total) * 100
    grouped["taxa_inadimplencia"] = (grouped["inadimplentes"] / grouped["quantidade"]) * 100

    # Ordem customizada
    ordem = ["<25", "25-35", "35-45", "45-60", "60+", ">60"]
    grouped["ordem"] = grouped["faixa_etaria"].apply(
        lambda x: ordem.index(x) if x in ordem else 99
    )
    grouped = grouped.sort_values("ordem").drop(columns=["ordem"])

    return grouped


def group_by_field(df: pd.DataFrame, field: str) -> pd.DataFrame:
    """Agrupa dados por campo e calcula métricas."""
    if df.empty or field not in df.columns:
        return pd.DataFrame()

    grouped = df.groupby(field).agg(
        value=("valor_credito", lambda x: x.astype(float).sum()),
        count=("id_cliente_atual", "count"),
        inadimplentes=("alvo_inadimplencia", lambda x: (x == 1).sum()),
    ).reset_index()

    grouped = grouped.rename(columns={field: "label"})
    grouped = grouped.sort_values("value", ascending=False)
    return grouped


def generate_risk_heatmap(df: pd.DataFrame, row_field: str = "escolaridade", col_field: str = "tipo_renda") -> pd.DataFrame:
    """Gera dados para heatmap de risco."""
    if df.empty or row_field not in df.columns or col_field not in df.columns:
        return pd.DataFrame()

    df_work = df.copy()
    df_work[row_field] = df_work[row_field].fillna("Não informado")
    df_work[col_field] = df_work[col_field].fillna("Não informado")

    grouped = df_work.groupby([row_field, col_field]).agg(
        total=("id_cliente_atual", "count"),
        inadimplentes=("alvo_inadimplencia", lambda x: (x == 1).sum()),
    ).reset_index()

    grouped["taxa"] = (grouped["inadimplentes"] / grouped["total"]) * 100

    # Pivotar para formato de heatmap
    pivot = grouped.pivot_table(
        index=row_field, columns=col_field, values="taxa", fill_value=0
    )

    return pivot


def get_top_critical_segments(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Identifica top N segmentos mais críticos (escolaridade + tipo renda)."""
    if df.empty:
        return pd.DataFrame()

    df_work = df.copy()
    df_work["segmento"] = (
        df_work["escolaridade"].fillna("N/A") + " + " + df_work["tipo_renda"].fillna("N/A")
    )

    grouped = df_work.groupby("segmento").agg(
        qtd_contratos=("id_cliente_atual", "count"),
        volume_exposto=("valor_credito", lambda x: x.astype(float).sum()),
        inadimplentes=("alvo_inadimplencia", lambda x: (x == 1).sum()),
    ).reset_index()

    grouped["taxa_inadimplencia"] = (grouped["inadimplentes"] / grouped["qtd_contratos"]) * 100
    grouped = grouped.sort_values("taxa_inadimplencia", ascending=False).head(n)

    return grouped
