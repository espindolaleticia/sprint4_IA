# Perguntas frequentes - operação acadêmica simulada
## Onde consultar status de estações
O GoodWe Grid Assistant utiliza os registros em contexto_operacional.json para informar status operacional SIMULADO de estações. O arquivo não tem conexão com dispositivos reais nem monitora telemetria em tempo real.
## Como interpretar consumo e faturamento
A energia de uma sessão pode ser expressa em kWh. O registro de sessão envolve identificação do usuário, estação, início, fim, consumo energético e valor cobrado. O faturamento da base operacional é simulado. O documento não possui tarifa monetária contratual por kWh, nem permite deduzir esse preço sem dados adicionais.
## Como lidar com informações ausentes
Se não existir registro da tensão de entrada, corrente, firmware, modelo exato, potência nominal ou especificação do fabricante na base, o sistema deve informar ausência de evidência documental e não apresentar números inventados.
## Como registrar problemas de uma estação
O registro de ocorrência pode identificar estação, horário, sintoma, prioridade e necessidade de encaminhamento. Questões de segurança e liberação técnica devem ser encaminhadas a pessoal habilitado.
