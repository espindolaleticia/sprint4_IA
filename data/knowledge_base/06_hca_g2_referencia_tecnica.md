# Linha GoodWe HCA G2 — referência técnica pública e alcance
## Escopo, modelos e limites
A linha de carregadores CA **GoodWe HCA G2** é utilizada neste projeto como **família de referência técnica**. Os modelos aplicáveis são GW7K-HCA-20 (7 kW), GW11K-HCA-20 (11 kW) e GW22K-HCA-20 (22 kW), conforme a ficha de dados e o manual do fabricante. Essas potências são **potências nominais de MODELOS**, não medidas operacionais. Os identificadores de estação simulada GW-03, GW-09, GW-12 etc. **não têm modelo HCA atribuído** e não se pode deduzir sua potência nominal com esses identificadores.

Fonte pública: https://br.goodwe.com/download-hca-g2-series ; https://br.goodwe.com/carregadores-hca-g2-goodwe . Documento técnico do grupo: `GW_HCA-G2_Datasheet-PT.pdf`, pág. 2; `GW_HCA-G2_User-Manual-PT.pdf`, manual versão V1.5-2025-11-11, páginas 5 e 10 do arquivo (seção 1.1 e seção 3.1).

## Operação e segurança (não é instrução de intervenção)
O modelo HCA G2 permite autenticação por aplicativo, RFID ou início automático; a documentação apresenta modos de carregamento, monitoramento e integração com sistemas fotovoltaicos. O fabricante requer profissionais treinados e determina desligamento e isolamento antes de manutenção. O chatbot **não deve fornecer instruções para manipular equipamentos energizados**.

Fonte: manual GoodWe HCA G2 PT, versão V1.5, pág. 7 do PDF (segurança) e pág. 10 (funcionalidades). Referência pública: https://br.goodwe.com/Ftp/Downloads/User%20Manual/GW_HCA-G2_User-Manual-PT.pdf .

## Modbus: referência de registradores, não telemetria em tempo real
O mapa Modbus **fornecido pelo grupo** descreve registradores de exemplo: **10015** (potência de carregamento), **10016** (energia da sessão) e **10017** (estado operacional); há também endereços para tensões, correntes e falhas. A procedência/autorização pública desse mapa e sua compatibilidade com versões de firmware específicas **não estão verificadas**. Consultar o documento local para precisão de unidades, escala e revisão. Não usar estes endereços para acionar um dispositivo real, alterar parâmetros ou inferir valores atuais.

Fonte: `Mapa MODBUS_HCA G2.pdf`, páginas 1 (histórico de revisão) e 3 (endereços 10015–10017); documento fornecido pelo grupo, não identificado como fonte pública oficial.

## Separação entre dados simulados e referência de fabricante
`contexto_operacional.json` continua sendo o cenário simulado original. As especificações de HCA G2 não devem ser aplicadas à GW-03/GW-09 sem inventário que comprove a correspondência. Não há tarifa contratual, regulamento real do condomínio nem telemetria conectada comprovados nesta entrega.
