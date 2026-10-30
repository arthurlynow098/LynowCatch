"""LynowCatch local media engine."""
import ipaddress
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import uuid
import importlib.util
from urllib.parse import urlparse

MAX_BYTES = 500 * 1024 * 1024

def health():
    root = Path(os.environ.get('LOCALAPPDATA', '')) / 'Microsoft/WinGet/Packages'
    if not shutil.which('ffmpeg') and root.exists():
        for binary in root.glob('Gyan.FFmpeg_*/ffmpeg-*/bin/ffmpeg.exe'):
            os.environ['PATH'] = str(binary.parent) + os.pathsep + os.environ.get('PATH', '')
            break
    return dict(service='lynowcatch', version='0.2.0', ffmpeg=bool(shutil.which('ffmpeg')),
                ffprobe=bool(shutil.which('ffprobe')), ytdlp=importlib.util.find_spec('yt_dlp') is not None)

def validate_url(url):
    if not isinstance(url, str) or len(url) > 4096:
        raise ValueError('URL inválida')
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Use um endereço público começando com http:// ou https://')
    addresses = socket.getaddrinfo(parsed.hostname, parsed.port or (443 if parsed.scheme == 'https' else 80))
    if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
        raise ValueError('Use links públicos; endereços locais não são permitidos')
    return url

def options(data):
    fmt, quality = data.get('format', 'mp4'), str(data.get('quality', '1080'))
    if fmt not in ('mp4', 'mp3', 'gif', 'original') or quality not in ('480', '720', '1080', '2160'):
        raise ValueError('Formato ou qualidade inválidos')
    start, duration = float(data.get('start') or 0), float(data.get('duration') or 0)
    if not 0 <= start <= 86400 or not 0 <= duration <= 3600:
        raise ValueError('Início: 0–86400 s; duração: 0–3600 s')
    if fmt == 'original' and (start or duration):
        raise ValueError('Escolha MP4, MP3 ou GIF para recortar')
    return fmt, quality, start, duration

def base_command():
    return [sys.executable, '-m', 'yt_dlp', '--ignore-config', '--no-playlist', '--no-warnings', '--socket-timeout', '30']

def preview(data):
    url = validate_url(data.get('url'))
    result = subprocess.run(base_command() + ['--skip-download', '--dump-single-json', '--', url],
                            capture_output=True, text=True, encoding='utf-8', timeout=60)
    if result.returncode:
        raise ValueError('Não foi possível consultar esse link. Confira se o conteúdo é público e está disponível.')
    info = json.loads(result.stdout)
    return {key: info.get(key) for key in ('title', 'duration', 'uploader', 'extractor')}

def download(data, output):
    url = validate_url(data.get('url'))
    fmt, quality, start, duration = options(data)
    tools = health()
    if fmt != 'original' and not (tools['ffmpeg'] and tools['ffprobe']):
        raise ValueError('FFmpeg e ffprobe são necessários. Instale-os e reinicie o motor.')
    ident = uuid.uuid4().hex
    target = Path(output) / ident
    target.mkdir(parents=True)
    try:
        cmd = base_command() + ['--restrict-filenames', '--max-filesize', '500M', '-o', str(target / 'media.%(ext)s')]
        if fmt == 'mp3':
            cmd += ['-x', '--audio-format', 'mp3', '--audio-quality', '0']
        elif fmt in ('mp4', 'gif'):
            cmd += ['-f', f'bv*[height<=?{quality}]+ba/b[height<=?{quality}]', '--merge-output-format', 'mp4', '--recode-video', 'mp4']
        result = subprocess.run(cmd + ['--', url], capture_output=True, text=True, timeout=600)
        if result.returncode:
            raise ValueError('A plataforma não permitiu o download. Confira o link ou atualize yt-dlp.')
        files = [p for p in target.iterdir() if p.is_file() and p.suffix not in ('.part', '.ytdl')]
        if len(files) != 1:
            raise ValueError('Nenhum arquivo completo disponível ou limite de tamanho excedido')
        file = files[0]
        if fmt == 'gif' or start or duration:
            converted = target / ('recorte.' + fmt)
            command = ['ffmpeg', '-y', '-ss', str(start), '-i', str(file)]
            if fmt == 'gif':
                command += ['-t', str(min(duration or 15, 15)), '-vf', 'fps=12,scale=480:-1:flags=lanczos', '-loop', '0']
            else:
                if duration:
                    command += ['-t', str(duration)]
                command += ['-vn', '-codec:a', 'libmp3lame'] if fmt == 'mp3' else ['-c:v', 'libx264', '-c:a', 'aac', '-movflags', '+faststart']
            subprocess.run(command + [str(converted)], check=True, capture_output=True, timeout=600)
            file.unlink()
            file = converted
        if file.stat().st_size > MAX_BYTES:
            raise ValueError('O resultado excedeu o limite de 500 MB')
        return dict(file='/files/' + ident + '/' + file.name, size=file.stat().st_size, name=file.name)
    except Exception:
        shutil.rmtree(target, ignore_errors=True)
        raise
