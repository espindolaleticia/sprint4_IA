# Referências HCA G2 e documentação ainda necessária

## Referência técnica selecionada (confirmada pelo grupo)

A **linha GoodWe HCA G2** foi escolhida como referência técnica do GoodWe Grid Assistant. O grupo forneceu três documentos para **uso local**, sem redistribuição no GitHub:

1. `GW_HCA-G2_Datasheet-PT.pdf` — ficha técnica de GW7K-HCA-20, GW11K-HCA-20 e GW22K-HCA-20 (7, 11 e 22 kW, respectivamente), 2 páginas.
2. `GW_HCA-G2_User-Manual-PT.pdf` — manual do usuário, versão **V1.5-2025-11-11**, 70 páginas, com modos, segurança, RFID e manutenção.
3. `Mapa MODBUS_HCA G2.pdf` — mapa Modbus fornecido pelo grupo, 9 páginas. Há registradores de monitoramento, mas a procedência pública do documento e a versão exata de firmware aplicável não foram verificadas.

Página oficial do fabricante: https://br.goodwe.com/download-hca-g2-series
Manual PT em site oficial: https://br.goodwe.com/Ftp/Downloads/User%20Manual/GW_HCA-G2_User-Manual-PT.pdf

**Atenção:** os IDs de estação **GW-03, GW-09, GW-12** etc. são simulados; não são nomes de modelos GW7K-HCA-20/GW11K-HCA-20/GW22K-HCA-20. Nenhum destes três documentos prova a potência individual de uma estação simulada. Não afirmar isso sem inventário verificável.

O manual declara restrição à reprodução/transmissão pública sem autorização. O GitHub contém um resumo acadêmico original de informações factuais e referências, mas **não os PDFs completos**. O script `scripts/importar_hca_g2.py` importa cópias do próprio grupo ao computador e registra hashes.

## Pendências independentes (não resolvidas pelos três PDFs)

- Regimento ou política **real** e autorizada para carregamento compartilhado em condomínio, com vigência, escopo e fonte.
- Tabela tarifária **verificável** da concessionária/localidade aplicável, ou tabela contratual autorizada com identificação de origem. Não inventar preço por kWh.
- Caso o grupo queira que o chatbot associe GW-03/GW-09 a um equipamento, inventário explicando qual modelo de carregador é usado em cada ID; sem isso, manter como simulação.
- Confirmação com professor sobre substituição de Ollama Cloud por Nomic local como provedor de embeddings.

## Histórico experimental e validade

A avaliação inicial de 14 perguntas (faithfulness 0,7143 → 0,8571; answer relevancy 0,6786 → 0,8214) pertence ao **corpus anterior à incorporação HCA** e permanece apenas como histórico.

A base ampliada **foi efetivamente indexada e avaliada em 21/10/2026** com 22 perguntas por versão. I1: 0,9773 / 0,9773; I2: 1,0000 / 0,9773; I2 com segurança v2: 1,0000 / 1,0000 (rubrica humana, não RAGAS). Os JSONs agregados publicados são transcrições das saídas do ambiente local do grupo; as coletas integrais e justificativas identificadas permanecem no computador original, sem distribuição pública de trechos dos PDFs protegidos.

Adicionar documentos novos **no futuro** exigirá reconstruir os índices e reexecutar as avaliações; não reutilizar as notas de 21/10/2026 se o corpus mudar novamente.
