"""Protocolo compartilhado pelo painel e pela reprodução do artigo.

As correlações são estritamente descritivas. Não calcula significância.
"""
from __future__ import annotations

import json
import hashlib
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

FUSO = "America/Sao_Paulo"
MIN_LEITURAS = 216
INDICADORES = ["ph", "turbidez", "oxigenio_dissolvido", "condutividade"]
ESTACOES = {
    "EF24": {"municipio": "Pindamonhangaba", "lat": -22.9246, "lon": -45.4613,
             "arquivo": "simqua_ef24_pindamonhangaba_app.csv", "sep": ";",
             "formato": "%d/%m/%Y %H:%M", "url": "https://simqua.cetesb.sp.gov.br/estacao/19/"},
    "EF25": {"municipio": "Santa Branca", "lat": -23.3963, "lon": -45.8832,
             "arquivo": "simqua_ef25_santa_branca_app.csv", "sep": ",",
             "formato": "%Y-%m-%d %H:%M:%S", "url": "https://simqua.cetesb.sp.gov.br/estacao/22/"},
    "EF26": {"municipio": "Queluz", "lat": -22.5312, "lon": -44.7782,
             "arquivo": "simqua_ef26_queluz_app.csv", "sep": ",",
             "formato": "%Y-%m-%d %H:%M:%S", "url": "https://simqua.cetesb.sp.gov.br/estacao/21/"},
}


def resumo_sha(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def gravar_json(caminho: Path, dados) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    tmp = caminho.with_suffix(caminho.suffix + ".tmp")
    tmp.write_text(json.dumps(dados, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    tmp.replace(caminho)


def obter_json_auditavel(url: str, destino: Path, atualizar=False) -> dict:
    """Cache explícito por URL, tentativas limitadas, erro visível e resposta bruta.

    O cache não muda uma falha em resposta vazia e não inventa valores.
    """
    meta_path = destino.with_suffix(".meta.json")
    if destino.exists() and meta_path.exists() and not atualizar:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta.get("url") == url and meta.get("sha256") == resumo_sha(destino):
            return json.loads(destino.read_text(encoding="utf-8"))
    erro = None
    for tentativa in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "EcoRadar-TCC/2026"})
            with urllib.request.urlopen(req, timeout=40) as resposta:
                conteudo = resposta.read()
                status = resposta.status
            dados = json.loads(conteudo)
            if not isinstance(dados, dict) or dados.get("error"):
                raise ValueError(f"Resposta inválida da API: {dados}")
            # Uma resposta sem série não conta como sucesso de importação.
            bloco = dados.get("hourly", dados.get("daily", {}))
            if not bloco.get("time"):
                raise ValueError("A API respondeu sem datas para o intervalo solicitado")
            n = len(bloco["time"])
            if any(not isinstance(v, list) or len(v) != n for v in bloco.values()):
                raise ValueError("Séries da API têm comprimentos incompatíveis")
            destino.parent.mkdir(parents=True, exist_ok=True)
            tmp = destino.with_suffix(".tmp")
            tmp.write_bytes(conteudo)
            tmp.replace(destino)
            gravar_json(meta_path, {"url": url, "consultado_em_utc": datetime.now(timezone.utc).isoformat(),
                                  "status_http": status, "sha256": resumo_sha(destino),
                                  "fuso": FUSO, "n_tempos": n})
            return dados
        except Exception as exc:
            erro = exc
            if tentativa < 2:
                time.sleep(tentativa + 1)
    raise RuntimeError(f"Falha na importação após 3 tentativas: {url}: {erro}") from erro


def limpar_medicoes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in INDICADORES + ["temperatura_agua", "precipitacao_agua", "nivel", "vazao"]:
        if col in df:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ".", regex=False), errors="coerce")
            if col == "ph":
                df.loc[~df[col].between(0, 14), col] = np.nan
            else:
                df.loc[df[col] < 0, col] = np.nan
    return df


def agregar_agua_diaria(df: pd.DataFrame) -> pd.DataFrame:
    """216 instantes distintos válidos por variável, estação e dia local.

    Duplicatas idênticas não contam duas vezes. Valores conflitantes para a
    mesma chave são rejeitados, para não depender da ordem dos arquivos.
    """
    if df.empty:
        return pd.DataFrame()
    df = limpar_medicoes(df)
    if not {"estacao", "municipio", "momento"}.issubset(df):
        raise ValueError("A água exige estação, município e momento de medição")
    if df[["estacao", "municipio", "momento"]].isna().any().any():
        raise ValueError("Identificação ou data de medição ausente")
    chaves = ["estacao", "municipio", "momento"]
    metricas = [c for c in INDICADORES + ["temperatura_agua", "precipitacao_agua", "nivel", "vazao"] if c in df]
    df = df[chaves + metricas].drop_duplicates()
    if df.duplicated(chaves).any():
        raise ValueError("Medições conflitantes para a mesma estação e instante")
    # Datas sem offset dos CSV fornecidos são assumidas como hora local.
    if df["momento"].dt.tz is not None:
        df["momento"] = df["momento"].dt.tz_convert(FUSO).dt.tz_localize(None)
    df["data"] = df["momento"].dt.normalize()
    g = df.groupby(["estacao", "municipio", "data"], sort=True)
    medias = g[metricas].mean()
    contagens = g[metricas].count()
    for col in metricas:
        medias[col] = medias[col].where(contagens[col] >= MIN_LEITURAS)
        medias[f"n_{col}"] = contagens[col]
        medias[f"cobertura_{col}"] = contagens[col] / 288
    return medias.reset_index()


def ler_csv_estudo(pasta: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    brutos = []
    for codigo, info in ESTACOES.items():
        df = pd.read_csv(pasta / info["arquivo"], sep=info["sep"], encoding="utf-8-sig", dtype=str)
        df["momento"] = pd.to_datetime(df["data"], format=info["formato"], errors="raise")
        if set(df["estacao"].dropna()) != {codigo} or set(df["municipio"].dropna()) != {info["municipio"]}:
            raise ValueError(f"Identificação incompatível no arquivo de {codigo}")
        df["arquivo_origem"] = info["arquivo"]
        brutos.append(df)
    bruto = pd.concat(brutos, ignore_index=True)
    return bruto, agregar_agua_diaria(bruto)


def integrar(ar: pd.DataFrame, agua: pd.DataFrame, clima: pd.DataFrame) -> pd.DataFrame:
    if ar.empty or agua.empty:
        return pd.DataFrame()
    chaves = ["municipio", "data"]
    if ar.duplicated(chaves).any() or clima.duplicated(chaves).any():
        raise ValueError("Ar ou clima duplicado por município e data")
    base = agua.merge(ar, on=chaves, how="inner", validate="many_to_one")
    if not clima.empty:
        base = base.merge(clima, on=chaves, how="left", validate="many_to_one")
    return base.sort_values(["estacao", "data"]).reset_index(drop=True)


def correlacoes_descritivas(base: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    linhas, pareamentos = [], []
    for estacao, g in base.groupby("estacao"):
        for pm in ["pm25", "pm10"]:
            for indicador in INDICADORES:
                for lag in range(4):
                    ar = g[["data", pm]].rename(columns={"data": "data_ar", pm: "valor_pm"})
                    agua = g[["data", indicador]].rename(columns={"data": "data_agua", indicador: "valor_agua"})
                    ar["data_agua"] = ar["data_ar"] + pd.Timedelta(days=lag)
                    pares = ar.merge(agua, on="data_agua", validate="one_to_one").dropna(subset=["valor_pm", "valor_agua"])
                    n = len(pares)
                    rho = pares["valor_pm"].corr(pares["valor_agua"], method="spearman") if n >= 5 else np.nan
                    identificacao = {"estacao": estacao, "municipio": g["municipio"].iloc[0],
                                     "particula": pm, "indicador": indicador, "lag_dias": lag}
                    linhas.append({**identificacao, "rho": rho, "n": n,
                                   "interpretacao": "Descritivo; sem teste de significância e sem ajuste por chuva"})
                    for k, v in identificacao.items():
                        pares[k] = v
                    pareamentos.append(pares)
    return pd.DataFrame(linhas), pd.concat(pareamentos, ignore_index=True) if pareamentos else pd.DataFrame()


def comparar_arvores_turbidez(treino: pd.DataFrame, features: list[str],
                             valores_arvores=(50, 100, 200, 350, 500),
                             n_splits=3, test_size=10):
    """Compara árvores por validação temporal dentro do conjunto de treino.

    Todas as linhas de uma data ficam na mesma dobra. A imputação é ajustada
    em cada treino da dobra; o teste cronológico final não participa da escolha.
    Também calcula uma referência pela média do treino em cada dobra.
    """
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    from sklearn.model_selection import TimeSeriesSplit

    if treino.empty or "data" not in treino or "turbidez" not in treino:
        raise ValueError("A validação temporal exige treino com data e turbidez")
    valores_arvores = tuple(int(n) for n in valores_arvores)
    if not valores_arvores or any(n < 1 for n in valores_arvores):
        raise ValueError("Os números de árvores devem ser inteiros positivos")
    datas = np.sort(pd.to_datetime(treino["data"].dropna().unique()))
    if len(datas) < (n_splits + 1) * test_size:
        raise ValueError("Datas insuficientes para as dobras temporais solicitadas")

    cv = TimeSeriesSplit(n_splits=n_splits, test_size=test_size)
    linhas = []
    for dobra, (idx_tr, idx_val) in enumerate(cv.split(datas), start=1):
        datas_tr, datas_val = datas[idx_tr], datas[idx_val]
        tr = treino[treino["data"].isin(datas_tr)].copy()
        val = treino[treino["data"].isin(datas_val)].copy()
        medianas = tr[features].median()
        if medianas.isna().any():
            raise ValueError("Atributo sem valores de treino na validação temporal")

        referencia = np.full(len(val), tr["turbidez"].mean())
        linhas.append({
            "modelo": "Média do treino", "arvores": np.nan, "dobra": dobra,
            "n_treino": len(tr), "n_validacao": len(val),
            "datas_treino": tr["data"].nunique(), "datas_validacao": val["data"].nunique(),
            "fim_treino": str(tr["data"].max().date()),
            "inicio_validacao": str(val["data"].min().date()),
            "fim_validacao": str(val["data"].max().date()),
            "MAE": mean_absolute_error(val["turbidez"], referencia),
            "RMSE": float(np.sqrt(mean_squared_error(val["turbidez"], referencia))),
            "R2": r2_score(val["turbidez"], referencia),
        })
        for n_arvores in valores_arvores:
            modelo = RandomForestRegressor(n_estimators=n_arvores, min_samples_leaf=2,
                                           random_state=42, n_jobs=1)
            modelo.fit(tr[features].fillna(medianas), tr["turbidez"])
            previsto = modelo.predict(val[features].fillna(medianas))
            linhas.append({
                "modelo": "Random Forest", "arvores": n_arvores, "dobra": dobra,
                "n_treino": len(tr), "n_validacao": len(val),
                "datas_treino": tr["data"].nunique(), "datas_validacao": val["data"].nunique(),
                "fim_treino": str(tr["data"].max().date()),
                "inicio_validacao": str(val["data"].min().date()),
                "fim_validacao": str(val["data"].max().date()),
                "MAE": mean_absolute_error(val["turbidez"], previsto),
                "RMSE": float(np.sqrt(mean_squared_error(val["turbidez"], previsto))),
                "R2": r2_score(val["turbidez"], previsto),
            })

    detalhe = pd.DataFrame(linhas)
    resumo = detalhe.groupby(["modelo", "arvores"], dropna=False, as_index=False).agg(
        MAE_medio=("MAE", "mean"), MAE_dp=("MAE", "std"),
        RMSE_medio=("RMSE", "mean"), RMSE_dp=("RMSE", "std"),
        R2_medio=("R2", "mean"), R2_dp=("R2", "std"),
        dobras=("dobra", "count"),
    )
    resumo["ordem"] = resumo["arvores"].fillna(0)
    resumo = resumo.sort_values("ordem").drop(columns="ordem").reset_index(drop=True)
    return resumo, detalhe


def avaliar_turbidez(base: pd.DataFrame):
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    features = ["pm25", "pm10", "temp_max_openmeteo", "temp_min_openmeteo", "vento_max_openmeteo", "chuva_openmeteo"]
    dados = base.dropna(subset=["turbidez"]).sort_values(["data", "municipio"]).reset_index(drop=True)
    datas = np.sort(dados["data"].unique())
    if len(datas) < 6 or len(dados) < 20:
        raise ValueError("Amostra insuficiente para a avaliação cronológica")
    corte = pd.Timestamp(datas[int(len(datas) * .7)])
    tr = dados[dados.data < corte].copy()
    te = dados[dados.data >= corte].copy()
    sensibilidade_resumo, sensibilidade_detalhe = comparar_arvores_turbidez(tr, features)
    medianas = tr[features].median()
    if medianas.isna().any():
        raise ValueError("Atributo sem valores de treino; não é possível imputar")
    modelo = RandomForestRegressor(n_estimators=350, min_samples_leaf=2, random_state=42, n_jobs=1)
    modelo.fit(tr[features].fillna(medianas), tr.turbidez)
    previsto = modelo.predict(te[features].fillna(medianas))
    te["rf_turbidez"] = previsto
    te["referencia_media_treino"] = tr.turbidez.mean()
    metricas = []
    for nome, valores in [("Random Forest", previsto), ("Média do treino", te.referencia_media_treino)]:
        metricas.append({"modelo": nome, "mae": mean_absolute_error(te.turbidez, valores),
                         "rmse": float(np.sqrt(mean_squared_error(te.turbidez, valores))),
                         "r2": r2_score(te.turbidez, valores), "n_treino": len(tr), "n_teste": len(te),
                         "datas_treino": tr.data.nunique(), "datas_teste": te.data.nunique(),
                         "inicio_treino": str(tr.data.min().date()), "fim_treino": str(tr.data.max().date()),
                         "inicio_teste": str(te.data.min().date()), "fim_teste": str(te.data.max().date()),
                         "referencia_ntu": tr.turbidez.mean(), "alvo": "turbidez contemporânea; sem horizonte futuro"})
    return (pd.DataFrame(metricas), te,
            pd.DataFrame({"atributo": features, "mediana_treino": medianas.values}),
            sensibilidade_resumo, sensibilidade_detalhe)
