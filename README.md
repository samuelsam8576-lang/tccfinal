# EcoRadar — revisão para o TCC

Código e material suplementar do estudo de Dâmaris Fermino Farias e Sam Barbosa sobre associações exploratórias entre partículas atmosféricas estimadas e parâmetros hídricos medidos em três estações SIMQUA do rio Paraíba do Sul.

## Baixar o projeto reproduzível

O arquivo **EcoRadar_TCC_Revisado_Com_Suplementar.zip** reúne a aplicação, os três CSV hídricos, as respostas JSON das APIs, os arquivos derivados e as instruções completas. Baixe o ZIP deste repositório, extraia a pasta `EcoRadar_TCC_Revisado` e abra o terminal nela.

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

A aplicação abre a execução arquivada e permite selecionar EF24 (Pindamonhangaba), EF25 (Santa Branca) ou EF26 (Queluz). A água vem de medições SIMQUA; PM e meteorologia são estimativas de modelos. O Random Forest estima turbidez contemporânea e não foi validado para recomendações ou previsão futura.

## Reproduzir tabelas e métricas sem rede

```bash
python -m pip install -r requirements-reproducao.txt
python reproduzir_artigo.py --offline
python -m unittest test_metodo test_interface -v
```

`suplementar/LEIA_ME.md` descreve a função dos JSON, CSV, metadados e hashes. `RESPOSTAS_BANCA.md` reúne as respostas às questões apresentadas na banca.

## Período e resultados

O período é 1º de janeiro a 7 de abril de 2026. A análise reúne 82.947 registros SIMQUA, 291 linhas diárias integradas e 96 coeficientes de Spearman descritivos, com 25 a 90 pares. Não há valores-p, intervalos de confiança ou correção por múltiplas comparações.

O Random Forest obteve MAE de 28,49 NTU e R² de −0,891 no teste cronológico. A referência pela média do treino obteve MAE de 24,52 NTU e R² de −0,213. O modelo não demonstrou ganho preditivo neste recorte.

Fontes: [CETESB SIMQUA](https://simqua.cetesb.sp.gov.br/), [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api) e [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api). Os CSV hídricos usados na reprodução são os fornecidos pelos autores; as respostas JSON de ar e clima correspondem à consulta de conferência registrada no suplemento.
