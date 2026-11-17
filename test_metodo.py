"""Testes de riscos metodológicos, executáveis sem internet."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

from ecoradar_metodo import (agregar_agua_diaria, integrar, correlacoes_descritivas,
                             ler_csv_estudo, comparar_arvores_turbidez)
from ecoradar_interface import carregar_execucao
from reproduzir_artigo import carregar

ROOT = Path(__file__).resolve().parent


class ProtocoloTest(unittest.TestCase):
    def agua(self, n, estacao="EF24"):
        return pd.DataFrame({"momento": pd.date_range("2026-01-02", periods=n, freq="5min"),
                             "estacao": estacao, "municipio": "Teste", "turbidez": 10., "ph": 7.,
                             "oxigenio_dissolvido": 5., "condutividade": 50.})

    def test_limite_cobertura_por_variavel(self):
        df = self.agua(216)
        df.loc[0, "ph"] = -1
        resultado = agregar_agua_diaria(df).iloc[0]
        self.assertEqual(resultado.turbidez, 10.)
        self.assertTrue(np.isnan(resultado.ph))
        self.assertEqual(resultado.n_ph, 215)

    def test_duplicatas_nao_aumentam_cobertura(self):
        df = self.agua(215)
        resultado = agregar_agua_diaria(pd.concat([df, df.iloc[:1]])).iloc[0]
        self.assertTrue(np.isnan(resultado.turbidez))
        self.assertEqual(resultado.n_turbidez, 215)

    def test_conflito_no_mesmo_instante_e_rejeitado(self):
        df = self.agua(216)
        extra = df.iloc[:1].copy()
        extra["turbidez"] = 20
        with self.assertRaisesRegex(ValueError, "conflitantes"):
            agregar_agua_diaria(pd.concat([df, extra]))

    def test_estacoes_nao_se_misturam(self):
        df = pd.concat([self.agua(215, "A"), self.agua(215, "B")])
        r = agregar_agua_diaria(df)
        self.assertEqual(len(r), 2)
        self.assertTrue(r.turbidez.isna().all())

    def test_chave_invalida_e_bloqueada(self):
        df = self.agua(216)
        df.loc[0, "momento"] = pd.NaT
        with self.assertRaisesRegex(ValueError, "ausente"):
            agregar_agua_diaria(df)

    def test_sem_correspondencia_municipal_nao_gera_media_regional(self):
        ar = pd.DataFrame({"municipio": ["A"], "data": [pd.Timestamp("2026-01-01")], "pm25": [2]})
        agua = pd.DataFrame({"estacao": ["EF24"], "municipio": ["B"], "data": [pd.Timestamp("2026-01-01")], "ph": [7]})
        self.assertTrue(integrar(ar, agua, pd.DataFrame()).empty)

    def test_defasagem_usa_calendario_e_nao_linha_seguinte(self):
        base = pd.DataFrame({"estacao": "E", "municipio": "M", "data": pd.to_datetime(["2026-01-01", "2026-01-03"]),
                             "pm25": [1, 2], "pm10": [2, 3], "turbidez": [4, 5], "ph": [7, 7],
                             "oxigenio_dissolvido": [5, 6], "condutividade": [10, 20]})
        c, p = correlacoes_descritivas(base)
        self.assertTrue((c[c.lag_dias == 1].n == 0).all())
        self.assertTrue(((p.data_agua - p.data_ar).dt.days == p.lag_dias).all())

    def test_modo_offline_nao_tenta_rede_e_rejeita_falta(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("urllib.request.urlopen", side_effect=AssertionError("não deve acessar rede")):
                with self.assertRaises(FileNotFoundError):
                    carregar(Path(tmp) / "ausente.json", "https://exemplo", True, False)

    def test_arquivos_reais_e_contagens_do_artigo(self):
        bruto, agua = ler_csv_estudo(ROOT / "data")
        self.assertEqual(len(bruto), 82947)
        self.assertEqual(len(agua), 291)
        self.assertEqual(agua.groupby("estacao").turbidez.count().to_dict(), {"EF24": 63, "EF25": 27, "EF26": 90})

    def test_integridade_e_resultados_reproduzidos(self):
        base, corr, metricas, previsoes = carregar_execucao(ROOT)
        self.assertEqual(len(corr), 96)
        self.assertTrue((corr[corr.indicador == "turbidez"].rho < 0).all())
        self.assertEqual((int(corr.n.min()), int(corr.n.max())), (25, 90))
        self.assertEqual(len(previsoes), 48)
        self.assertEqual(str(previsoes.data.min().date()), "2026-03-10")
        self.assertEqual(str(previsoes.data.max().date()), "2026-04-07")
        rf = metricas.loc[metricas.modelo == "Random Forest"].iloc[0]
        self.assertAlmostEqual(rf.mae, 28.49, places=2)
        self.assertAlmostEqual(rf.r2, -0.891, places=3)
        self.assertGreater(rf.mae, metricas.loc[metricas.modelo == "Média do treino", "mae"].iloc[0])

    def test_sensibilidade_arvores_usa_dobras_cronologicas(self):
        linhas = []
        for dia, data in enumerate(pd.date_range("2026-01-01", periods=50, freq="D")):
            for municipio in ("A", "B"):
                x = float(dia + (municipio == "B"))
                linhas.append({"data": data, "municipio": municipio, "turbidez": 10 + .4*x + dia % 7,
                               "x1": x, "x2": x % 5})
        resumo, detalhe = comparar_arvores_turbidez(pd.DataFrame(linhas), ["x1", "x2"])
        rf = resumo[resumo.modelo == "Random Forest"]
        self.assertEqual(rf.arvores.tolist(), [50, 100, 200, 350, 500])
        self.assertEqual(len(detalhe), 18)  # 5 modelos + referência em cada uma das 3 dobras
        for _, grupo in detalhe.groupby("dobra"):
            self.assertEqual(grupo.datas_validacao.nunique(), 1)
            self.assertEqual(grupo.datas_validacao.iloc[0], 10)
            self.assertLess(grupo.fim_treino.max(), grupo.inicio_validacao.min())


if __name__ == "__main__":
    unittest.main()
