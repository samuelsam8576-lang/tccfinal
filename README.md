# EcoRadar — partículas atmosféricas e qualidade da água

## Objetivo do TCC

Investigar, de forma exploratória, se variações nas concentrações atmosféricas estimadas de **PM2.5** e **PM10** estão associadas a mudanças em parâmetros da água medidos pelo SIMQUA: **turbidez, pH, oxigênio dissolvido e condutividade elétrica**. A precipitação e as condições meteorológicas entram como contexto para interpretar as relações.

### Pergunta de pesquisa

Há associação entre as concentrações diárias de PM2.5/PM10 e os indicadores de qualidade da água nos mesmos municípios e períodos? A associação muda quando se considera um atraso de um a três dias ou a precipitação?

### Hipótese de trabalho

Partículas e compostos transportados pela atmosfera podem alcançar a superfície por deposição seca ou úmida. A chuva também pode remover material do ar e levar partículas do solo aos rios. A direção da mudança na água não é definida de antemão, pois deposição, diluição, escoamento e outras fontes podem atuar ao mesmo tempo.

Para a análise estatística do relatório, isso pode ser expresso como **H0**: não há associação monotônica entre PM2.5/PM10 e os parâmetros da água no recorte analisado; **H1**: pelo menos uma dessas associações está presente. A versão atual do painel resume Spearman ρ, mas não calcula valor-p nem intervalo de confiança; portanto, ela não decide H0/H1.

## Método implementado

1. As medições do SIMQUA são agregadas em médias diárias por município. Valores impossíveis são excluídos: pH fora da escala 0–14 e valores negativos nos demais parâmetros físicos.
2. PM2.5 e PM10 horários fornecidos pelo Open-Meteo são resumidos por dia e associados às coordenadas municipais.
3. As bases são cruzadas por município e data. O painel compara partículas com turbidez, pH, oxigênio dissolvido e condutividade, além de mostrar a chuva e relações com atraso de até três dias.
4. A tabela de associações usa o coeficiente de Spearman por município, com o número de pares disponíveis. É uma análise exploratória; o painel não calcula significância estatística.
5. O Random Forest de turbidez usa PM2.5/PM10 e variáveis meteorológicas disponíveis. A avaliação separa os 70% de datas mais antigas para treino e as datas posteriores para teste. MAE e R² são apresentados como métricas de erro/ajuste, não como “acurácia” causal.

Unidades dos principais indicadores: PM2.5/PM10 em μg/m³; turbidez em NTU; oxigênio dissolvido em mg/L; condutividade em μS/cm; pH sem unidade.

## Limitações para apresentar no TCC

- O Open-Meteo fornece estimativas atmosféricas baseadas em modelos CAMS. No domínio global, a grade tem resolução aproximada de 45 km; esses valores não são medições de um sensor instalado na estação de água.
- As coordenadas do ar são municipais, enquanto a medição do SIMQUA ocorre em um ponto específico do rio. A diferença espacial pode reduzir a correspondência entre as bases.
- PM2.5/PM10 indicam concentração de partículas no ar, mas o projeto não mede fluxo de deposição, composição química, metais ou concentração de partículas depositadas na água.
- Turbidez não identifica a origem dos sólidos. Chuva, erosão, vazão, esgoto, uso do solo e processos locais também podem alterar os parâmetros da água.
- Correlação, atraso temporal, importância de variável e previsões do Random Forest não provam que as partículas causaram uma alteração na água. O simulador serve apenas para explorar o conjunto observado.
- Para testar causalidade ou identificar o mecanismo, seriam necessárias coletas sincronizadas de deposição/água da chuva e análises químicas das partículas e da água, junto com dados de vazão e características da bacia.

## Como executar

Na pasta do projeto, instale as dependências e inicie o painel:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

O `app.py` na raiz é o ponto de entrada. As fontes SIMQUA podem ser carregadas pela própria tela ou colocadas em `data/` com um dos nomes listados no painel.

## Referências e bases

- CETESB. **Sistema Integrado de Monitoramento da Qualidade das Águas — SIMQUA**. Disponível em: <https://simqua.cetesb.sp.gov.br/>. Acesso em: 12 out. 2026.
- OPEN-METEO. **Air Quality API Documentation**. Descreve as variáveis de PM e as fontes CAMS utilizadas nas estimativas. Disponível em: <https://open-meteo.com/en/docs/air-quality-api>. Acesso em: 12 out. 2026.
- U.S. ENVIRONMENTAL PROTECTION AGENCY. **Air-Surface Exchange Process Overview**. Explica deposição seca e úmida de partículas e gases. Disponível em: <https://www.epa.gov/cmaq/air-surface-exchange-process-overview>. Acesso em: 12 out. 2026.
- **An assessment of atmospheric deposition of metals and the physico-chemical parameters of a rainwater harvesting system in Rio de Janeiro, Brazil, by means of statistical multivariate analysis**. *Revista Ambiente & Água*, v. 15, n. 4, 2020. DOI: <https://doi.org/10.4136/ambi-agua.2522>.
