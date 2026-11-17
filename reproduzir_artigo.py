"""Importação auditável e reprodução do artigo. Sem rede com --offline.

python reproduzir_artigo.py
python reproduzir_artigo.py --offline
python reproduzir_artigo.py --atualizar --saida nova_execucao
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
from datetime import date, timedelta, datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

import numpy as np
import pandas as pd
import scipy
import sklearn
from ecoradar_metodo import (ESTACOES, INDICADORES, FUSO, obter_json_auditavel,
                            ler_csv_estudo, limpar_medicoes, integrar,
                            correlacoes_descritivas, avaliar_turbidez, gravar_json, resumo_sha)

ROOT = Path(__file__).resolve().parent


def importar(pasta_json, offline=False, atualizar=False):
    ares, climas = [], []
    consultas = []
    inicio, fim = date(2026, 1, 1), date(2026, 4, 7)
    for codigo, info in ESTACOES.items():
        blocos = []
        cursor = inicio
        while cursor <= fim:
            fim_bloco = min(cursor + timedelta(days=59), fim)
            params = {"latitude": info["lat"], "longitude": info["lon"], "hourly": "pm2_5,pm10",
                      "start_date": str(cursor), "end_date": str(fim_bloco), "timezone": FUSO}
            url = "https://air-quality-api.open-meteo.com/v1/air-quality?" + urlencode(params)
            nome = f"{codigo}_ar_{cursor}_{fim_bloco}.json"
            consultas.append({"arquivo": nome, "url": url, "tipo": "ar modelado CAMS", "municipio": info["municipio"]})
            caminho = pasta_json / nome
            dados = carregar(caminho, url, offline, atualizar)
            h = dados["hourly"]
            if dados.get("hourly_units", {}).get("pm2_5") != "μg/m³":
                raise ValueError("Unidade atmosférica inesperada")
            tabela = pd.DataFrame({"hora": pd.to_datetime(h["time"]), "pm25": h["pm2_5"], "pm10": h["pm10"]})
            blocos.append(tabela)
            cursor = fim_bloco + timedelta(days=1)
        horas = pd.concat(blocos).drop_duplicates("hora")
        horas["data"] = horas.hora.dt.normalize()
        ar = horas.groupby("data").agg(pm25=("pm25", "mean"), pm10=("pm10", "mean"),
                                      horas_pm25=("pm25", "count"), horas_pm10=("pm10", "count")).reset_index()
        # Contagens horárias documentam disponibilidade, não 24 sensores independentes.
        ar["municipio"] = info["municipio"]
        ares.append(ar)
        params = {"latitude": info["lat"], "longitude": info["lon"], "start_date": str(inicio),
                  "end_date": str(fim), "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max", "timezone": FUSO}
        url = "https://archive-api.open-meteo.com/v1/archive?" + urlencode(params)
        nome = f"{codigo}_clima_{inicio}_{fim}.json"
        consultas.append({"arquivo": nome, "url": url, "tipo": "meteorologia histórica modelada", "municipio": info["municipio"]})
        d = carregar(pasta_json / nome, url, offline, atualizar)["daily"]
        clima = pd.DataFrame({"data": pd.to_datetime(d["time"]), "temp_max_openmeteo": d["temperature_2m_max"],
                              "temp_min_openmeteo": d["temperature_2m_min"], "chuva_openmeteo": d["precipitation_sum"],
                              "vento_max_openmeteo": d["wind_speed_10m_max"], "municipio": info["municipio"]})
        climas.append(clima)
        print(f"{codigo}: ar {len(ar)} dias; clima {len(clima)} dias", flush=True)
    gravar_json(pasta_json.parent / "consultas.json", consultas)
    return pd.concat(ares, ignore_index=True), pd.concat(climas, ignore_index=True)


def carregar(caminho, url, offline, atualizar):
    if offline:
        if not caminho.is_file():
            raise FileNotFoundError(f"JSON ausente no modo offline: {caminho}")
        meta = json.loads(caminho.with_suffix(".meta.json").read_text(encoding="utf-8"))
        if meta["url"] != url or meta["sha256"] != resumo_sha(caminho):
            raise ValueError(f"Cache alterado ou consulta incompatível: {caminho.name}")
        return json.loads(caminho.read_text(encoding="utf-8"))
    return obter_json_auditavel(url, caminho, atualizar=atualizar)


def salvar_csv(df, caminho):
    df.to_csv(caminho, index=False, encoding="utf-8-sig", float_format="%.12g", date_format="%Y-%m-%d")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--atualizar", action="store_true")
    parser.add_argument("--saida", type=Path, default=ROOT / "suplementar")
    args = parser.parse_args()
    if args.offline and args.atualizar:
        parser.error("--offline e --atualizar são incompatíveis")
    saida = args.saida.resolve()
    saida.mkdir(parents=True, exist_ok=True)
    bruto, agua = ler_csv_estudo(ROOT / "data")
    ar, clima = importar(saida / "json_bruto", args.offline, args.atualizar)
    base = integrar(ar, agua, clima)
    base["origem_agua"] = "CSV SIMQUA fornecido pelos autores; sem nova autenticação da coleta"
    base["origem_ar"] = "Open-Meteo / CAMS Global; estimativa de modelo em coordenada municipal"
    base["origem_clima"] = "Open-Meteo Historical Weather API; estimativa meteorológica"
    base["fuso"] = FUSO
    for codigo, info in ESTACOES.items():
        mask = base.estacao == codigo
        base.loc[mask, "latitude_consulta"] = info["lat"]
        base.loc[mask, "longitude_consulta"] = info["lon"]
    estatisticas, cobertura = [], []
    limpo = limpar_medicoes(bruto)
    for codigo, g in limpo.groupby("estacao"):
        for indicador in INDICADORES:
            estatisticas.append({"estacao": codigo, "municipio": ESTACOES[codigo]["municipio"],
                                 "indicador": indicador, "n_valido": g[indicador].notna().sum(), "mediana": g[indicador].median()})
            cobertura.append({"estacao": codigo, "indicador": indicador,
                              "dias_elegiveis": int(agua.loc[agua.estacao == codigo, indicador].notna().sum())})
    correlacoes, pares = correlacoes_descritivas(base)
    metricas, previsoes, imputacao = avaliar_turbidez(base)
    for nome, tabela in {"agua_diaria.csv": agua, "ar_diario.csv": ar, "clima_diario.csv": clima,
                         "base_diaria_integrada.csv": base, "estatisticas_simqua.csv": pd.DataFrame(estatisticas),
                         "cobertura_diaria.csv": pd.DataFrame(cobertura), "correlacoes_spearman.csv": correlacoes,
                         "pareamentos_spearman_datas.csv": pares, "metricas_modelo_turbidez.csv": metricas,
                         "previsoes_teste_turbidez.csv": previsoes, "imputacao_treino.csv": imputacao}.items():
        salvar_csv(tabela, saida / nome)
    gravar_json(saida / "ambiente.json", {"python": platform.python_version(), "pandas": pd.__version__,
                                         "numpy": np.__version__, "scipy": scipy.__version__, "scikit_learn": sklearn.__version__,
                                         "data_execucao_utc": datetime.now(timezone.utc).isoformat(), "modo_offline": args.offline})
    entradas = []
    for p in sorted((ROOT / "data").glob("*.csv")):
        entradas.append({"caminho": str(p.relative_to(ROOT)), "sha256": resumo_sha(p), "bytes": p.stat().st_size})
    for p in sorted(saida.rglob("*")):
        if p.is_file() and p.name != "manifesto.json":
            entradas.append({"caminho": str(p.relative_to(saida)), "sha256": resumo_sha(p), "bytes": p.stat().st_size})
    gravar_json(saida / "manifesto.json", {"escopo": "Dados de entrada e saídas desta execução; caminhos data/ são relativos à raiz do projeto",
                                         "periodo": ["2026-01-01", "2026-04-07"], "arquivos": entradas})
    print(metricas.to_string(index=False))
    print(f"Base {len(base)} linhas; {len(correlacoes)} coeficientes; {len(pares)} pareamentos; saída {saida}")


if __name__ == "__main__":
    main()
