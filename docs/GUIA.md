# Guia do LynowCatch

## Primeiro uso
Execute INICIAR.bat com Python instalado. O iniciador prepara o ambiente virtual `.venv`. Instale FFmpeg e ffprobe para MP4, MP3 e GIF. Abra http://localhost:8765 e confira Conexão. Ao usar a versão local, o endereço do motor é preenchido automaticamente.

## Downloads
Cole um link por linha, até 20 por adição. Escolha um perfil ou ajuste formato e resolução. Links iguais com as mesmas opções são ignorados se já estiverem aguardando ou processando. Para guardar o arquivo no local escolhido pelo navegador, clique em Salvar quando terminar.

## Trechos e GIFs
Abra Recortar um trecho. Início e duração são números em segundos; campos vazios significam início zero e duração completa. Para GIF, duração vazia significa 15 segundos. Não se aplica ao formato Original. O vídeo completo é baixado antes do recorte, portanto o trecho escolhido não reduz necessariamente o tráfego de rede.

## Prévia
Consultar primeiro link busca título, autor e duração. A consulta pode levar até 60 segundos no motor. As informações variam por plataforma e não garantem o download.

## Pausa e falhas
Pausar impede os próximos itens de começarem. O atual termina normalmente. Falhas aparecem no próprio item, com a opção Tentar novamente. Fechar a aba não encerra um trabalho já enviado. A fila não é restaurada ao recarregar.

## Histórico e arquivos
O histórico é local ao navegador e limitado a 100 registros. Use a busca para filtrar links e Exportar CSV para obter um relatório de todos os registros. Repetir cria uma nova tarefa com as opções anteriores. Os arquivos ficam em `web/files/<identificador>/`. Limpar histórico não os exclui. Para liberar espaço, encerre trabalhos ativos e exclua as pastas de resultados que não precisa mais.

## Solução de problemas
| Sintoma | O que verificar |
|---|---|
| Motor desconectado | Execute o iniciador e abra a interface em localhost:8765. |
| Porta ocupada | Já pode haver um motor ativo; abra o endereço local e verifique sua versão em Conexão. |
| FFmpeg ausente | Instale Gyan.FFmpeg pelo WinGet e reinicie o motor. Confirme também ffprobe. |
| yt-dlp ausente | Execute `.venv\Scripts\python.exe -m pip install -r requirements.txt`. |
| Plataforma mudou | Atualize com `.venv\Scripts\python.exe -m pip install -U yt-dlp`. |
| Link do histórico falhou | Confira se o motor está ativo e o arquivo ainda existe. |
| Conteúdo indisponível | Confira visibilidade pública, região, validade do link e suporte do extrator. |
| Tempo limite | Tente um vídeo menor ou menos qualidade. |

Use somente conteúdo próprio, de domínio público ou autorizado. O motor deve permanecer restrito ao seu computador.
