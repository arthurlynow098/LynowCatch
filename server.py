"""Servidor HTTP do LynowCatch, restrito ao computador local."""
import http.server
import json
import subprocess
import threading
import os
import socket
from pathlib import Path
from lynowcatch.engine import health, preview, download

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'web/files'
ORIGINS = ('http://localhost:8765', 'http://127.0.0.1:8765', 'https://octocatch-arthur.mellowclove17.chatgpt.site')
DOWNLOAD_LOCK = threading.Lock()

class LocalServer(http.server.ThreadingHTTPServer):
    allow_reuse_address = False

    def server_bind(self):
        if os.name == 'nt':
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / 'web'), **kwargs)

    def end_headers(self):
        origin = self.headers.get('Origin', '')
        if origin in ORIGINS:
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Vary', 'Origin')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Access-Control-Allow-Private-Network', 'true')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

    def reply(self, status, data):
        payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/health':
            return self.reply(200, health())
        return super().do_GET()

    def do_POST(self):
        if self.path not in ('/api/download', '/api/preview'):
            return self.reply(404, {'error': 'Rota inexistente'})
        if self.headers.get('Origin', '') not in ORIGINS:
            return self.reply(403, {'error': 'Origem não autorizada'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length < 16000:
                raise ValueError('Requisição inválida')
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError('Envie um objeto JSON')
            if self.path == '/api/preview':
                return self.reply(200, preview(data))
            if not DOWNLOAD_LOCK.acquire(blocking=False):
                return self.reply(409, {'error': 'Motor ocupado. Aguarde o download atual.'})
            try:
                result = download(data, OUT)
            finally:
                DOWNLOAD_LOCK.release()
            return self.reply(200, result)
        except (ValueError, TypeError, KeyError) as error:
            return self.reply(400, {'error': str(error)})
        except subprocess.TimeoutExpired:
            return self.reply(504, {'error': 'Tempo limite excedido. Tente um conteúdo menor.'})
        except Exception:
            return self.reply(500, {'error': 'Falha no processamento. Verifique as dependências e o link.'})

def main():
    print('LynowCatch: http://localhost:8765 — Ctrl+C para encerrar', flush=True)
    LocalServer(('127.0.0.1', 8765), Handler).serve_forever()

if __name__ == '__main__':
    main()
