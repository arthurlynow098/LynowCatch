# Arquitetura

## Componentes
- `web/index.html`: apresentação, sem build obrigatório. O recorte CSS da imagem oculta os cantos brancos sem mudar o PNG original.
- `web/app.js`: fila em memória, perfis, validação básica, histórico e exportação CSV.
- `server.py`: HTTP, CORS, limite de corpo, serialização e exclusão mútua de downloads.
- `lynowcatch/engine.py`: validação de endereço e opções, execução dos subprocessos, recorte e organização da saída.

## Estado
A fila fica em memória no navegador. Histórico, tema, endereço e preferências usam localStorage. Os arquivos existem independentemente dos registros e são persistidos em web/files. O servidor não executa banco de dados.

## Processamento
A URL é validada antes de executar yt-dlp. Esquemas alternativos, credenciais e resolução inicial para endereços não globais são rejeitados. Opções são passadas como lista de argumentos, sem shell. O download tem limite de 600 segundos. Recorte e GIF usam FFmpeg, com limite adicional de 600 segundos. Ao ocorrer uma exceção, a pasta gerada daquela operação é removida; um resultado maior que 500 MB é rejeitado.

## Restrições
O filtro de DNS inicial não cobre redirecionamentos, alterações de DNS ou todas as requisições feitas por extratores. O projeto é destinado a uso pessoal com links confiáveis, não à hospedagem pública. CORS é uma restrição do navegador, não autenticação. Não há cotas acumuladas, limpeza automática, isolamento dos subprocessos ou cancelamento pelo cliente.

## Evolução possível
Jobs assíncronos com identificador, progresso real de transferência, cancelamento do subprocesso e recuperação de fila exigem uma próxima evolução do protocolo. Não são recursos da versão atual.
