# API local · v0.2.0

Base: `http://127.0.0.1:8765`. Respostas JSON em UTF-8. POST exige Origin autorizado e corpo com menos de 16000 bytes. Origens aceitas estão declaradas em `server.py`. Não há autenticação: o servidor deve continuar restrito ao loopback.

## GET /api/health
Retorna `service`, `version`, `ffmpeg`, `ffprobe` e `ytdlp` (os três últimos booleanos).

## POST /api/preview
Corpo: `{"url":"https://exemplo.com/video"}`. Retorna `title`, `duration` em segundos, `uploader` e `extractor`. Campos podem ser nulos. Tempo limite de 60 segundos.

## POST /api/download
```json
{"url":"https://exemplo.com/video","format":"mp4","quality":"1080","start":0,"duration":0}
```

| Campo | Valores |
|---|---|
| url | HTTP ou HTTPS público, sem credenciais, até 4096 caracteres |
| format | mp4, mp3, gif ou original; padrão mp4 |
| quality | 480, 720, 1080 ou 2160; padrão 1080 |
| start | Segundos entre 0 e 86400; padrão 0 |
| duration | Segundos entre 0 e 3600; zero significa completo, ou 15 s no GIF |

Original não aceita recorte. GIF usa no máximo 15 segundos. Retorno: `file` (caminho relativo), `size` (bytes), `name` (nome do arquivo). Faça GET no caminho `file` para obter o resultado. Um bloqueio global limita downloads a um por vez, inclusive com várias abas abertas.

## Erros
| HTTP | Significado |
|---|---|
| 400 | Corpo, endereço, opções ou conteúdo indisponíveis |
| 403 | Origin não autorizado |
| 404 | Rota inexistente |
| 409 | Motor ocupado com outro download |
| 500 | Falha inesperada de processamento ou dependência |
| 504 | Tempo limite do subprocesso |

Formato: `{"error":"Mensagem em português"}`. Não há API de cancelamento nem progresso por bytes. A prévia é síncrona, assim como o download.
