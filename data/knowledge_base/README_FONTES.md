# Inventário de fontes e procedência — Sprint 4

| Documento | Papel | Publicação no GitHub |
|---|---|---|
| `contexto_operacional.json` | Estado e operações SIMULADAS de GW-03/GW-09 etc. | Sim, identificado como simulação |
| `01_faq_operacional.md`, `02_procedimentos_academicos.md` | FAQ/procedimentos acadêmicos, NÃO fabricante | Sim |
| `03_condominios_politica_referencia.md` | Questões sobre condomínio; não é regimento real | Sim |
| `04_tarifas_sem_valores.md` | Registra ausência de tarifa real | Sim |
| `05_manuais_produto_pendentes.md` | Escopo da referência técnica e limites | Sim |
| `06_hca_g2_referencia_tecnica.md` | Resumo AUTORAL acadêmico com links a fabricante e referências por página | Sim |
| `hca_g2_local/GW_HCA-G2_User-Manual-PT.pdf` | Manual HCA G2 V1.5, 70 páginas, importação local | **Não** (restrição expressa no manual) |
| `hca_g2_local/GW_HCA-G2_Datasheet-PT.pdf` | Ficha técnica HCA G2, 2 páginas, importação local | **Não** |
| `hca_g2_local/Mapa MODBUS_HCA G2.pdf` | Mapa Modbus recebido do grupo, 9 páginas; procedência oficial não confirmada | **Não** |

Página oficial de downloads: https://br.goodwe.com/download-hca-g2-series

Manual oficial PT: https://br.goodwe.com/Ftp/Downloads/User%20Manual/GW_HCA-G2_User-Manual-PT.pdf

**Limite importante:** modelo de carregador (GW7K-HCA-20 etc.) é diferente de identificador de estação simulada (GW-09 etc.). Os PDFs locais são importados por `python scripts/importar_hca_g2.py --origem "CAMINHO_DOS_PDFS"`. Em seguida execute a indexação. A interface apresenta arquivo e página; dados do corpus original continuam identificados como simulação. Requer nova avaliação após ampliar a base. A consulta ao repositório público não inclui arquivos completos de terceiros.
