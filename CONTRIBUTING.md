# Como contribuir

Prepare o ambiente descrito no README e use uma branch para a alteração. Não inclua `.venv`, arquivos baixados, logs, binários ou dados pessoais. Descreva o problema, a alteração observável e a validação executada.

Antes de propor uma mudança, execute:
```
python -m unittest discover -s tests -v
node --check web/app.js
```

Teste mudanças visuais em largura de desktop e celular. Mudanças no motor devem cobrir condições de erro e limpeza dos arquivos parciais. Testes automatizados não devem depender de downloads externos, autenticação ou serviços de plataforma.

Relatos de erro devem informar sistema operacional, versão Python, estado em /api/health e mensagem exibida. Remova tokens, links privados e informações pessoais dos registros.
