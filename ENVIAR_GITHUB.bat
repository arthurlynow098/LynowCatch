@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ===================================================
echo   Publicando todos os arquivos no GitHub
echo   Repositorio: arthurlynow098/LynowCatch
echo ===================================================
echo.

:: 1. Inicializa o Git se ainda nao foi inicializado
git init

:: 2. Configura a branch principal como main
git branch -M main

:: 3. Configura a URL remota do GitHub
git remote remove origin 2>nul
git remote add origin https://github.com/arthurlynow098/LynowCatch.git

:: 4. Adiciona todos os arquivos do projeto (respeitando o .gitignore)
git add .

:: 5. Cria o commit com a arvore de arquivos completa
git commit -m "feat: adicionar arquivos completos do projeto LynowCatch"

:: 6. Envia para o GitHub substituindo o commit do arquivo zip
echo.
echo Enviando arquivos para o GitHub...
git push -u origin main --force

echo.
echo ===================================================
echo   Concluido! Verifique em:
echo   https://github.com/arthurlynow098/LynowCatch
echo ===================================================
pause
