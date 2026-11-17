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
| Testes automatizados | 11 testes concluídos, cobrindo cobertura, duplicatas, conflitos, datas, junção, integridade e navegação |
| Interface arquivada | Carregamento e troca entre EF24, EF25, EF26, pH e PM₁₀ sem chamada de API e sem exceção |

Os testes são executados com `python -m unittest test_metodo test_interface -v`. A verificação da interface usa Streamlit AppTest; não equivale a um ensaio de usabilidade com gestores. A disponibilidade permanente dos serviços externos e o comportamento em produção não foram certificados.

As consultas desta revisão reproduziram, ao arredondamento apresentado no artigo, os resultados numéricos centrais. Os JSON são os obtidos nesta revisão, e não respostas recuperadas das consultas antigas. As medições hídricas preservadas são as que os autores forneceram no ZIP.
