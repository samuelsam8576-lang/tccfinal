# Material suplementar do EcoRadar

Este diretório reúne a execução do artigo **Análise exploratória de associações entre material particulado atmosférico e parâmetros hídricos no Vale do Paraíba Paulista**, de Dâmaris Fermino Farias e Sam Barbosa.

Período dos dados: **01/01/2026 a 07/04/2026**, fuso `America/Sao_Paulo`.
Execução de conferência: **17/11/2026**. As nove respostas brutas foram obtidas novamente nesta data; não são arquivos recuperados das consultas antigas. As tabelas e métricas centrais foram reproduzidas com os mesmos valores arredondados do artigo.

Os CSV hídricos fornecidos pelos autores estão em `../data/`. Eles contêm 82.947 linhas no total, de três estações SIMQUA/CETESB do rio Paraíba do Sul: EF24 (Pindamonhangaba), EF25 (Santa Branca) e EF26 (Queluz). Os arquivos fornecidos são as entradas preservadas; a conferência numérica não reconstitui o procedimento original de exportação do portal.

## Arquivos e função

| Arquivo ou pasta | Conteúdo |
| --- | --- |
| `../app.py` | Interface Streamlit; inicia no modo arquivado quando o suplemento está presente |
| `../ecoradar_metodo.py` | Protocolo comum de controle de cobertura, integração e análise |
| `../reproduzir_artigo.py` | Importação por API, captura de JSON e reprodução das tabelas |
| `../requirements-reproducao.txt` | Versões da execução numérica |
| `../test_metodo.py` e `../test_interface.py` | Verificações de cobertura, duplicidades, calendário, integração e resultados |
| `../data/simqua_*.csv` | Três entradas hídricas de cinco minutos |
| `json_bruto/*.json` | Nove respostas da API: seis blocos de ar e três séries meteorológicas |
| `json_bruto/*.meta.json` | URL, horário UTC da consulta, status HTTP, hash e contagem da resposta correspondente |
| `consultas.json` | Relação explícita das consultas e municípios |
| `agua_diaria.csv` | Médias hídricas, contagens e cobertura por variável e estação |
| `ar_diario.csv` | Médias de PM e contagens de valores horários disponíveis |
| `clima_diario.csv` | Chuva acumulada, temperaturas máxima e mínima, vento máximo |
| `base_diaria_integrada.csv` | 291 linhas: 97 datas × 3 estações, com ausências mantidas |
| `estatisticas_simqua.csv` | Contagens e medianas usadas na Tabela 1 |
| `cobertura_diaria.csv` | Dias elegíveis usados na Tabela 2 |
| `correlacoes_spearman.csv` | 96 coeficientes, tamanhos de amostra e defasagens da Tabela 3 |
| `pareamentos_spearman_datas.csv` | 5.568 pares efetivamente usados, com data do ar e da água |
| `metricas_modelo_turbidez.csv` | Métricas, períodos e tamanhos dos conjuntos da Tabela 4 |
| `previsoes_teste_turbidez.csv` | 48 valores observados, estimativas do RF e referência no teste |
| `imputacao_treino.csv` | Medianas ajustadas exclusivamente no treino |
| `ambiente.json` | Versões e horário da última reprodução |
| `manifesto.json` | Lista de entradas e saídas com tamanho e SHA-256 |

`previsoes_teste_turbidez.csv` mantém o nome por compatibilidade, mas contém **estimativas contemporâneas**, sem previsão de dias futuros.

## Reprodução sem acesso à internet

Na raiz do projeto, com Python 3.12:

```bash
python -m pip install -r requirements-reproducao.txt
python reproduzir_artigo.py --offline
```

No Windows, execute os comandos no PowerShell a partir da pasta interna `EcoRadar_TCC_Revisado` (a que contém `reproduzir_artigo.py`). Os JSON são lidos explicitamente em UTF-8 para preservar corretamente unidades e caracteres acentuados.

O modo offline exige os nove JSON e seus metadados com hashes compatíveis. Ele não tenta a API nem gera valores substitutos. A reprodução grava as saídas derivadas e atualiza o registro de execução, mas preserva os JSON brutos.

Para conferir os testes e abrir a interface:

```bash
python -m pip install -r requirements.txt
python -m unittest test_metodo test_interface -v
python -m streamlit run app.py
```

## Importação automatizada

Uma execução faz as consultas, valida os vetores, preserva as respostas brutas, converte JSON em tabelas, agrega as séries e exporta os resultados. Não é necessário copiar os valores manualmente.

```bash
python reproduzir_artigo.py
```

Se o cache da mesma URL já existe e seu hash é válido, ele é reutilizado. Para consultar novamente, crie uma execução separada, preservando a versão do artigo:

```bash
python reproduzir_artigo.py --atualizar --saida nova_execucao
```

O intervalo do artigo é fixo no script. Alterá-lo requer revisar as entradas SIMQUA e gerar outra análise; uma rotina diária não amplia automaticamente esse estudo. Para operação contínua, um agendador pode executar a mesma rotina, com intervalos parametrizados e validação dos novos arquivos. Esta entrega não ativa um serviço periódico nem promete integração oficial homologada com o SIMQUA.

A importação hídrica permanece por CSV exportado do SIMQUA. Não foi implementado um cliente para uma API pública documentada de séries do SIMQUA. Isso não significa que nenhum serviço interno exista. Os três CSV são lidos automaticamente; na interface, todos os `data/simqua_*.csv` são concatenados e as duplicatas não aumentam a cobertura.

Para gerar a Figura 5, execute `python gerar_figura_teste.py` (Matplotlib nas dependências de reprodução). A saída fica em `suplementar/figuras/`.

## Interpretação e limites

- Água: registros medidos; ar e meteorologia: estimativas de modelos. Simulação não significa que a água foi gerada artificialmente.
- Uma média hídrica só é elegível com pelo menos 216 instantes válidos e distintos, em 288 previstos por dia e variável.
- PM é consultado nas coordenadas municipais. A grade global CAMS tem cerca de 45 km; não corresponde a um sensor de PM junto à estação hídrica.
- As 96 correlações são descritivas. Não há valores-p, intervalos de confiança, teste de hipótese ou controle de descobertas falsas. Não selecionar picos como achados confirmados.
- As combinações compartilham séries, partículas e datas; 24 sinais negativos de turbidez não representam 24 replicações independentes.
- A chuva pode remover PM do ar e mobilizar sedimentos para a água. Essa é uma explicação plausível para o sinal inverso, não um mecanismo comprovado neste conjunto.
- O RF estima turbidez do mesmo dia. Treino 02/01–09/03/2026; teste 10/03–07/04/2026. MAE 28,49 NTU, pior que a referência de 24,52 NTU; não é validado para recomendação ambiental.
- As 350 árvores são uma escolha fixa do ensaio, sem busca de hiperparâmetros. Não há evidência de que esse número seja ótimo.

## Fontes

- [CETESB SIMQUA](https://simqua.cetesb.sp.gov.br/): identificação das estações e fonte informada dos CSV.
- [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api) e Copernicus Atmosphere Monitoring Service (CAMS): estimativas de partículas.
- [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api): meteorologia histórica modelada.
- [USGS Surface Runoff and the Water Cycle](https://www.usgs.gov/water-science-school/science/surface-runoff-and-water-cycle) e [US EPA Air-Surface Exchange](https://www.epa.gov/cmaq/air-surface-exchange-process-overview): contexto dos mecanismos, sem validação causal do estudo.

Os direitos e condições de reutilização das fontes permanecem com seus respectivos provedores. O pacote não atribui uma nova licença aos dados de terceiros.
