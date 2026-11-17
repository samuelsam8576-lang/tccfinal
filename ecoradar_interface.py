"""Visualização offline da execução científica arquivada, sem novos dados fictícios."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from ecoradar_metodo import resumo_sha

NOMES = {"pm25": "PM₂,₅ (μg/m³)", "pm10": "PM₁₀ (μg/m³)", "turbidez": "Turbidez (NTU)",
         "ph": "pH (sem unidade)", "oxigenio_dissolvido": "Oxigênio dissolvido (mg/L)",
         "condutividade": "Condutividade (μS/cm)"}


def carregar_execucao(root):
    pasta = Path(root) / "suplementar"
    manifesto = json.loads((pasta / "manifesto.json").read_text(encoding="utf-8"))
    for item in manifesto["arquivos"]:
        p = (Path(root) / item["caminho"]) if item["caminho"].startswith("data/") else (pasta / item["caminho"])
        if not p.is_file() or resumo_sha(p) != item["sha256"]:
            raise ValueError(f"Arquivo ausente ou alterado: {item['caminho']}; reproduza a análise")
    base = pd.read_csv(pasta / "base_diaria_integrada.csv", parse_dates=["data"])
    correlacoes = pd.read_csv(pasta / "correlacoes_spearman.csv")
    metricas = pd.read_csv(pasta / "metricas_modelo_turbidez.csv")
    previsoes = pd.read_csv(pasta / "previsoes_teste_turbidez.csv", parse_dates=["data"])
    return base, correlacoes, metricas, previsoes


def exibir_execucao_arquivada(root):
    st.title("EcoRadar")
    st.subheader("Análise exploratória e simulação de turbidez")
    try:
        base, corr, metricas, previsoes = carregar_execucao(root)
    except Exception as exc:
        st.error(f"A execução arquivada não pôde ser validada: {exc}")
        return
    st.warning("Protótipo acadêmico. Os resultados não autorizam decisões operacionais nem demonstram causalidade. "
               "As simulações estimam turbidez contemporânea e não antecipam dias futuros.")
    st.caption("Água: medições dos CSV SIMQUA fornecidos. Ar: estimativas CAMS/Open-Meteo em grade de cerca de 45 km, "
               "nas coordenadas municipais. Meteorologia: estimativas históricas Open-Meteo. "
               "Execução histórica fixa de 01/01/2026 a 07/04/2026, sem atualização em tempo real.")
    consultas = json.loads((Path(root) / "suplementar" / "consultas.json").read_text())
    metas = [json.loads((Path(root) / "suplementar" / "json_bruto" / Path(c["arquivo"]).with_suffix(".meta.json")).read_text()) for c in consultas]
    st.caption("JSON consultados em UTC: " + min(m["consultado_em_utc"] for m in metas) + " a " + max(m["consultado_em_utc"] for m in metas))
    estacao = st.selectbox("Estação da série e das correlações", sorted(base.estacao.unique()))
    g = base[base.estacao == estacao].copy()
    periodo = st.date_input("Período exibido", value=(g.data.min().date(), g.data.max().date()),
                            min_value=g.data.min().date(), max_value=g.data.max().date())
    if len(periodo) != 2:
        st.info("Selecione as duas datas do intervalo.")
        return
    g = g[g.data.between(pd.Timestamp(periodo[0]), pd.Timestamp(periodo[1]))]
    indicador = st.selectbox("Indicador hídrico", ["turbidez", "ph", "oxigenio_dissolvido", "condutividade"], format_func=NOMES.get)
    pm = st.selectbox("Partícula atmosférica estimada", ["pm25", "pm10"], format_func=NOMES.get)
    validos = g[["data", pm, indicador]].dropna()
    c1, c2, c3 = st.columns(3)
    c1.metric("Dias com pares válidos", len(validos))
    c2.metric("Dias sem par válido", len(g) - len(validos))
    c3.metric("Cobertura mínima da água", "216/288 (75%)")
    st.caption("A cobertura é aplicada separadamente a cada variável. Lacunas não equivalem a zero. "
               "As correlações usam somente pares completos, sem imputação.")
    t1, t2, t3, t4 = st.tabs(["Séries e dispersão", "96 associações descritivas", "Avaliação da simulação", "Dados e fontes"])
    with t1:
        for variavel in [pm, indicador]:
            # Inclui as datas ausentes no eixo e não conecta lacunas.
            serie = g.set_index("data").reindex(pd.date_range(periodo[0], periodo[1], freq="D"))
            serie.index.name = "data"
            fig = px.line(serie.reset_index(), x="data", y=variavel, markers=True,
                          title=f"{estacao} · {NOMES[variavel]}", labels={variavel: NOMES[variavel], "data": "Data local"})
            fig.update_traces(connectgaps=False)
            st.plotly_chart(fig, width="stretch")
        if len(validos) >= 5:
            rho = validos[pm].corr(validos[indicador], method="spearman")
            st.metric("Spearman ρ no mesmo dia e no filtro exibido", f"{rho:.3f}")
            st.plotly_chart(px.scatter(validos, x=pm, y=indicador, hover_data=["data"],
                                      labels=NOMES, title=f"{estacao} · n = {len(validos)} pares válidos"), width="stretch")
        else:
            st.info("Menos de cinco pares válidos; coeficiente não apresentado.")
        st.caption("O sinal indica apenas uma associação no recorte. Chuva, vazão e fontes locais podem influenciar as duas séries.")
    with t2:
        st.write("A tabela abaixo conserva o período completo do artigo: 01/01 a 07/04/2026, independentemente do filtro de datas acima.")
        st.warning("96 combinações correlacionadas entre si. Sem valores-p, intervalos de confiança ou correção por "
                   "múltiplas comparações. Picos isolados podem ocorrer por acaso; não são evidência estatística confirmatória.")
        st.caption("3 estações × 2 partículas × 4 indicadores × 4 defasagens = 96 coeficientes. "
                   "PM no dia t é pareado com água em t + lag exato; dias ausentes não são substituídos.")
        st.dataframe(corr[corr.estacao == estacao], hide_index=True, width="stretch")
        st.download_button("Baixar todos os coeficientes", corr.to_csv(index=False), "correlacoes_spearman.csv", "text/csv")
    with t3:
        st.write("Avaliação regional conjunta do artigo, com as três estações e período completo; não muda com os filtros das séries.")
        st.caption("Treino: 02/01–09/03/2026, 132 observações em 67 datas. Teste: 10/03–07/04/2026, 48 observações em 29 datas. "
                   "Datas inteiras permanecem no mesmo conjunto; imputação pela mediana somente do treino. 350 árvores, "
                   "min_samples_leaf=2 e semente 42, sem alegação de otimização.")
        st.dataframe(metricas[["modelo", "mae", "rmse", "r2", "n_treino", "n_teste"]].rename(
            columns={"mae": "MAE (NTU)", "rmse": "RMSE (NTU)", "r2": "R²"}), hide_index=True, width="stretch")
        rf = metricas.loc[metricas.modelo == "Random Forest"].iloc[0]
        ref = metricas.loc[metricas.modelo == "Média do treino"].iloc[0]
        if rf.mae >= ref.mae or rf.r2 < 0:
            st.error("O Random Forest não superou a referência e não foi validado para uso operacional. "
                     "A interface não gera recomendações ambientais a partir desse modelo.")
        st.caption("MAE e RMSE medem erro em NTU; menor é melhor. R² negativo indica erro quadrático maior que o "
                   "da média do próprio teste, usada apenas para interpretar a métrica. A referência disponível "
                   "para prever sem acessar o teste é a média do treino. Nenhuma métrica é uma acurácia percentual.")
        fig = px.scatter(previsoes, x="turbidez", y="rf_turbidez", color="estacao", hover_data=["data"],
                         labels={"turbidez": "Turbidez observada (NTU)", "rf_turbidez": "Turbidez estimada (NTU)"},
                         title="Teste cronológico · estimativa do mesmo dia")
        vmin = float(previsoes[["turbidez", "rf_turbidez"]].min().min())
        vmax = float(previsoes[["turbidez", "rf_turbidez"]].max().max())
        fig.add_shape(type="line", x0=vmin, y0=vmin, x1=vmax, y1=vmax)
        st.plotly_chart(fig, width="stretch")
    with t4:
        st.dataframe(g, hide_index=True, width="stretch")
        st.download_button("Baixar recorte diário", g.to_csv(index=False), f"{estacao}_diario.csv", "text/csv")
        st.write("CSV é a tabela importada/exportada. JSON é a resposta estruturada das APIs, preservada antes "
                 "de converter os vetores de datas e valores em DataFrames e CSV. JSON também registra URLs, "
                 "horários de coleta e hashes. Não é uma segunda medição independente.")
        st.markdown("[Código e material suplementar](https://github.com/samuelsam8576-lang/tccfinal)")
        st.json(consultas, expanded=False)
