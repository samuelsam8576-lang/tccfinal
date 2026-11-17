# Respostas às indicações da banca

As respostas abaixo acompanham o artigo revisado e os arquivos da execução de 17/11/2026. O resultado é um estudo exploratório com simulação computacional baseada em dados observados e modelados. Não houve geração de medições hídricas artificiais.

## Duas alterações prioritárias para evitar interpretação errada

**1. Identificar a natureza, o recorte e a qualidade de cada dado antes da leitura do gráfico.** A interface distingue água medida, ar modelado e estimativas do RF; mostra estação, período, unidade, cobertura e pares válidos. O corte de 216/288 leituras é aplicado por indicador. A junção exige município e data compatíveis, sem substituir uma falha por média regional. Os gráficos de associação passam pela seleção de uma estação; as lacunas não são ligadas como se fossem observações contínuas.

**2. Tornar os limites estatísticos e do modelo parte da apresentação dos resultados.** A versão de entrega retira o rótulo “acurácia estimada” baseado em 100 − MAPE e a interpretação automática de tendências como conclusões ambientais. Apresenta MAE, RMSE, R², datas de treino/teste e a referência simples. O RF não superou a média do treino e as recomendações automáticas foram bloqueadas. As 96 correlações permanecem descritivas e sem declaração de significância.

Essas alterações reduzem erros de leitura, mas ainda não certificam o sistema para uso oficial. Seriam necessárias validação institucional, ensaios com gestores e novas séries, além da rastreabilidade já implementada.

## Como automatizar a importação

O comando `python reproduzir_artigo.py` lê os três CSV, consulta ar e clima para o mesmo intervalo, salva cada resposta JSON bruta, valida as séries e converte os vetores em tabelas. Depois calcula médias, cobertura, junções, correlações e a avaliação do modelo, exportando CSV e um manifesto SHA-256. O modo `--offline` reproduz a execução arquivada. `--atualizar --saida nova_execucao` produz uma nova coleta sem substituir o conjunto do artigo.

Para atualizar continuamente a água, ainda é preciso obter novos CSV oficiais ou implementar uma integração autorizada com serviço documentado do provedor. Não foi inventado um endereço de API do SIMQUA. Uma tarefa agendada pode executar a rotina após a chegada de entradas válidas; a presente entrega não ativa coleta periódica.

## Por que manter 96 coeficientes sem valores-p

O desenho atual é descritivo e não testa formalmente hipóteses. Foram apresentadas todas as combinações de três estações, duas partículas, quatro parâmetros e quatro defasagens, com o n de cada uma. A multiplicidade favorece padrões aparentes, e as séries apresentam dependência temporal. Assim, um pico isolado ou o conjunto de sinais negativos não permite afirmar significância, deposição ou causalidade.

Uma análise confirmatória futura precisaria definir previamente a família de 96 comparações e as hipóteses; modelar chuva, vazão e sazonalidade; usar inferência que preserve a dependência temporal; e corrigir a multiplicidade, por exemplo por controle da taxa de falsas descobertas adequado à dependência. Acrescentar valores-p assintóticos e aplicar uma correção mecânica não resolveria, sozinho, a autocorrelação e a confusão meteorológica. A revisão explicita essa limitação; não afirma que realizou esses testes.

## O que a comparação de 96 coeficientes significa

O total é 3 estações × 2 variáveis de partículas × 4 parâmetros hídricos × 4 defasagens. Portanto, 96 não foi escolhido como parâmetro do algoritmo, nem é um número a partir do qual ele começa a errar. A multiplicidade aumenta o risco de padrões aparentes quando se destacam picos isolados; a análise segue descritiva.

## Por que testar 50, 100, 200, 350 e 500 árvores

A revisão acrescenta validação temporal de três dobras, com dez datas de validação em cada dobra dentro do conjunto de treino externo. Cada data fica inteira na dobra, e as medianas são calculadas apenas no treino de cada dobra. O teste final de 10/03 a 07/04/2026 continua separado.

Entre os cinco Random Forests, 350 árvores apresentou a menor MAE média (56,14 NTU); 200 árvores ficou próximo (56,31 NTU). A diferença é pequena diante dos desvios entre dobras. A referência pela média do treino obteve MAE médio de 53,17 NTU, melhor que todas as configurações avaliadas. Assim, o resultado documenta a comparação, mas não prova que 350 seja ótimo ou que o modelo seja útil para previsão.

## Por que mais PM pode coincidir com água menos turva

A explicação meteorológica mais plausível é a atuação conjunta da chuva e do escoamento. A precipitação pode remover partículas suspensas da atmosfera e, simultaneamente, transportar sedimentos do solo e de superfícies urbanas para o rio. Assim, dias mais chuvosos podem apresentar menos PM e maior turbidez. Em intervalos menos chuvosos pode haver menos remoção atmosférica e menor aporte de sedimentos, contribuindo para a associação inversa.

Essa interpretação é uma hipótese, não uma conclusão causal. Vazão, operação de barragens, tempo de transporte e ressuspensão também podem influenciar as séries; EF25 fica a jusante da barragem de Santa Branca. O período de janeiro ao início de abril não cobre um ciclo anual e não comprova sazonalidade. A hipótese inicial de deposição aumentando sólidos não foi demonstrada pelo estudo.

## Onde está o material suplementar

O pacote `EcoRadar_TCC_Revisado_Com_Suplementar.zip` está disponível no [repositório do EcoRadar](https://github.com/samuelsam8576-lang/tccfinal/tree/tcc-revisao-banca-2026-11) e pode ser baixado diretamente [neste link](https://github.com/samuelsam8576-lang/tccfinal/blob/tcc-revisao-banca-2026-11/EcoRadar_TCC_Revisado_Com_Suplementar.zip). Depois de extraí-lo, os três CSV hídricos ficam em `data/` e os arquivos da execução em `suplementar/`: nove respostas JSON e metadados, base diária integrada, 96 coeficientes, 5.568 pareamentos, métricas, predições, imputação, comparação das árvores e manifesto SHA-256. `suplementar/LEIA_ME.md` explica cada arquivo e a reprodução; `suplementar/VERIFICACAO.md` registra os resultados reproduzidos e informa que os 12 testes automatizados não foram executados nesta conferência por falta de Plotly e Streamlit.

## Onde entra o JSON

CSV é uma tabela de linhas e colunas. JSON é o formato estruturado retornado pelas APIs. Por exemplo, a resposta de ar contém `hourly.time`, `hourly.pm2_5` e `hourly.pm10`, além das unidades e coordenadas. O programa valida o comprimento dos vetores, converte-os em DataFrame, calcula médias diárias e grava CSV. A resposta original permanece em JSON para conferir a importação. JSON também registra metadados, consultas e hashes; não constitui uma medição adicional nem substitui os CSV SIMQUA.

## Por que a API não foi acessada

É preciso distinguir as fontes. O código consulta as APIs Open-Meteo para ar e meteorologia; nesta revisão, as consultas históricas foram executadas e as respostas arquivadas. A água SIMQUA foi importada por CSV fornecido pelos autores. O projeto não implementava um cliente homologado para uma API pública documentada de séries SIMQUA. A balneabilidade usa outro serviço REST, separado da amostra principal.

Não há logs das execuções antigas que permitam atribuir uma eventual tela sem dados a um motivo específico. Na versão revisada, falhas de consulta e de validação são exibidas; elas não são tratadas como zeros nem substituídas silenciosamente por outro município ou período.

## Qual é o período do modelo

- Entradas: 01/01–07/04/2026.
- Dias elegíveis de turbidez: 180 observações de estação e dia.
- Treino: 02/01–09/03/2026, 132 observações em 67 datas.
- Teste: 10/03–07/04/2026, 48 observações em 29 datas.
- Alvo: média diária de turbidez do mesmo dia dos atributos; não é previsão antecipada.
- RF: MAE 28,49 NTU, RMSE 36,02 NTU, R² −0,891.
- Referência pela média do treino: MAE 24,52 NTU, RMSE 28,85 NTU, R² −0,213.

O R² negativo compara o erro quadrático com a média do próprio teste. Essa média não é usada como preditor. A referência operacional de comparação do ensaio usa somente a média do treino, 65,52 NTU.

## Estações e demais ajustes

| Indicação | Tratamento na revisão |
| --- | --- |
| Estações | Quadro com EF24, EF25, EF26, rio, contexto do ponto e diferença entre coordenada municipal e hídrica |
| Material suplementar e Git | Seção de disponibilidade, endereço por revisão e arquivos realmente presentes |
| Resumo | Reescrito em português e inglês, distinguindo simulação, observação e estimativa |
| Siglas e unidades | Expansão na primeira ocorrência pertinente e quadro no Apêndice A |
| Tabelas | Citações no texto, ordem e legendas revistas; cada defasagem da Tabela 3 recebe coluna própria |
| Figura de modelo | Figura 5 apresenta dados do teste cronológico, substituindo a captura com “acurácia estimada” |
| 350 árvores | Escolha fixa do ensaio, sem alegação de ser o valor ótimo |
| Valores ausentes | Spearman sem imputação; no RF, medianas aprendidas apenas no treino |
| Aprovação | As correções respondem tecnicamente aos pontos apresentados; a avaliação final pertence à banca |
| Árvores do Random Forest | 350 teve a menor MAE média entre as cinco configurações testadas, mas a referência simples foi melhor; não há alegação de ótimo |

As capturas históricas restantes documentam a interface anterior. Os resultados científicos provêm das tabelas e saídas reproduzíveis, não da leitura de uma captura de tela.
