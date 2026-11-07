# Etapa 1 — Base do projeto

**Objetivo:** deixar a "casca" do projeto no padrão do api_cadastro antes de mexer no código.
**Resultado:** `.gitignore` completo, `pytest.ini` e `tests/` como pacote; 10 testes continuam passando.

## Passo a passo (o que foi feito e como)

### 1. `.gitignore`
Antes só ignorava `__pycache__/`, `*.pyc` e `.pytest_cache/`. Agora também cobre ambiente virtual (`.venv/`, `venv/`), `.env`, pastas de editor e lixo do sistema (`Thumbs.db`, `.DS_Store`). `PLANO.md` fica de fora do Git, como no api_cadastro: o plano é rascunho local, a história oficial está em `docs/`.

**Por quê:** o projeto não tem segredos hoje, mas `.env` entra no padrão para ninguém commitar uma chave por descuido no futuro.

### 2. `pytest.ini`
```ini
[pytest]
pythonpath = .
testpaths = tests
```
- `pythonpath = .` faz `from faxineira...` funcionar a partir da raiz, sem depender de onde o pytest é chamado.
- `testpaths = tests` diz onde procurar testes.

### 3. `tests/__init__.py`
Arquivo vazio que transforma `tests/` em pacote. Evita conflito quando dois arquivos de teste têm o mesmo nome em pastas diferentes.

## Verificação
| Checagem | Resultado |
|---|---|
| `pytest` | 10 passaram |
