# Como rodar

Pré-requisitos: **Windows 11** e **Python 3.10+** (testado no 3.12). Nada de Docker, nada de banco, nada de `.env`.

## 1. Baixar e instalar
```powershell
git clone https://github.com/matheusf8/help-desk.git
cd help-desk
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Se o PowerShell reclamar de "execução de scripts desabilitada", rode `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` uma vez e tente de novo. (Ou pule o venv e use só `pip install -r requirements.txt`.)

## 2. Abrir o programa
```powershell
python main.py
```
Aparece o banner e o menu numerado. Digite o número da opção e `ENTER`. `0` sai.

| Opções | O que fazem | Mexe em algo? |
|---|---|---|
| 1 a 4 | espaço do disco, pastas dos programas, pastas do usuário, itens de inicialização | **não**, só leitura |
| 5 | mostra as regras de segurança | não |
| 6 | Temp (`%TEMP%` e `C:\Windows\Temp`) | pergunta; vai para a Lixeira |
| 7 | cache do Chrome | pergunta; vai para a Lixeira |
| 8 | restos de programas desinstalados no AppData | pergunta **uma pasta por vez**; vai para a Lixeira |
| 9 | esvazia a Lixeira | pergunta; **sem volta** |

**Primeira vez?** Rode só as opções 1 a 4. Elas não alteram nada e mostram onde o espaço está indo.

## 3. Rodar os testes
```powershell
pytest
```
Esperado: `54 passed`. Os testes **não** apagam nada de verdade: usam pastas de mentira e uma Lixeira falsa (veja [etapa 4](etapas/etapa-04-testes.md)).

## Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| `Este programa foi feito para Windows 11.` | rodou em Mac/Linux | o programa usa registro e Lixeira do Windows; só roda nele |
| `ModuleNotFoundError: colorama` ou `send2trash` | dependências não instaladas | `pip install -r requirements.txt` (com o venv ativo) |
| Cores estranhas, como `←[32m` | terminal antigo sem suporte a cores | use o Windows Terminal ou o PowerShell atual |
| "N itens não puderam ser movidos" | arquivo em uso por outro programa, ou item protegido | normal; feche o programa (ex.: Chrome) e repita, se quiser |
| Limpeza de `C:\Windows\Temp` quase não move nada | falta de permissão de administrador | abra o PowerShell como administrador, ou ignore |
| `pytest` não acha `faxineira` | rodou fora da pasta do projeto | entre na pasta `help-desk` e rode de lá (o `pytest.ini` cuida do resto) |
