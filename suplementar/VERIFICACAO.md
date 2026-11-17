# Verificação da revisão de entrega

Data: 17/11/2026. As verificações abaixo foram executadas no ambiente registrado em `ambiente.json`.

| Verificação | Resultado |
| --- | --- |
| Importação histórica de ar e clima | Nove respostas HTTP bem-sucedidas, preservadas com metadados e hash |
| Reprodução sem rede | Concluída com os JSON arquivados |
| Leitura efetiva da interface | Os três CSV locais foram concatenados: 82.947 registros e 291 linhas diárias |
| Controle de cobertura da água | Dias de turbidez elegível: EF24 = 63, EF25 = 27, EF26 = 90 |
| Coeficientes da Tabela 3 | 96; 25 a 90 pares por coeficiente; os 24 de turbidez são negativos |
| Pareamentos de calendário | 5.568 pares exportados; datas hídricas correspondem a t + lag exato |
| Avaliação do RF | 132 observações de treino e 48 de teste; MAE 28,49, RMSE 36,02, R² −0,891 |
| Referência pela média do treino | MAE 24,52, RMSE 28,85, R² −0,213 |
| Sensibilidade de árvores | 5 configurações em 3 dobras cronológicas dentro do treino; 350 teve MAE média 56,14 NTU, mas a referência por média alcançou 53,17 NTU |
| Testes automatizados | Não executados nesta conferência: a importação dos módulos parou por ausência de `plotly` e `streamlit`; não houve asserções. Existem 12 casos nos arquivos de teste. |
| Interface arquivada | Não revalidada por `AppTest` nesta conferência, pois `streamlit` não está instalado. |

Para executar a suíte, instale `requirements.txt` e rode `python -m unittest test_metodo test_interface -v`. Nesta conferência, o comando terminou antes da execução dos casos: `test_metodo` falhou ao importar `plotly` e `test_interface` falhou ao importar `streamlit`. Portanto, não se afirma aprovação dos testes automatizados nem da interface. A verificação da interface com Streamlit AppTest também não equivale a um ensaio de usabilidade com gestores. A disponibilidade permanente dos serviços externos e o comportamento em produção não foram certificados.

As consultas desta revisão reproduziram, ao arredondamento apresentado no artigo, os resultados numéricos centrais. Os JSON são os obtidos nesta revisão, e não respostas recuperadas das consultas antigas. As medições hídricas preservadas são as que os autores forneceram no ZIP.

A comparação entre números de árvores é uma análise de sensibilidade, não evidência de ótimo global. As dobras são temporais e restritas ao treino externo; o conjunto final de teste não é utilizado para escolher o número de árvores. O Random Forest continuou abaixo da referência simples na MAE média das dobras.
