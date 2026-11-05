# Help Desk - Faxineira de PC

Ferramenta de suporte técnico em Python: roda direto no Windows da pessoa (via
PowerShell, clonando do GitHub) e ajuda a diagnosticar e limpar o computador,
passo a passo, com menu numerado.

Baseado num guia de faxina de PC (Windows 11) que já era usado manualmente —
este projeto automatiza as partes seguras dele.

## Por que não Docker?

O programa precisa enxergar e mexer direto no sistema (AppData, registro,
Temp). O Docker isola o contêiner do computador host de propósito — então
ele não serve aqui. É Python puro, rodando direto no Windows.

## Regra de segurança número 1

**Nada é apagado direto.** Toda limpeza manda o item para a Lixeira do
Windows primeiro — só é removido de verdade se a Lixeira for esvaziada, e
isso só acontece se o usuário confirmar explicitamente (opção 9).

## Como rodar

```powershell
cd "C:\caminho\para\help"
pip install -r requirements.txt
python main.py
```

## O que o menu faz

**Diagnóstico** (só leitura, nunca apaga nada):
1. Espaço do disco C:
2. Tamanho das pastas de cada programa instalado
3. Maiores pastas do usuário (Downloads, Documentos...)
4. Itens de inicialização (o que abre sozinho com o Windows)
5. Mostrar as regras de segurança de novo

**Limpeza** (sempre manda pra Lixeira, sempre pede confirmação):
6. Limpar Temp (`%TEMP%` e `C:\Windows\Temp`)
7. Limpar cache do Chrome
8. Procurar pastas de AppData que não batem com nenhum programa instalado
   hoje (possíveis restos de programa desinstalado) — mostra uma por uma e
   só move a que o usuário confirmar
9. Esvaziar a Lixeira (ação final, sem volta)

## Testes

```powershell
pytest
```

Os testes cobrem as funções puras (conversão de bytes, cálculo de
porcentagem, soma de tamanho de pasta, ordenação) — a parte do código que dá
pra testar sem precisar mexer de verdade no disco da máquina.

## Roadmap (v2)

Itens mais arriscados do guia original, deixados de fora da v1 de propósito:
- Editar chaves de registro de programas desinstalados (com backup `.reg`
  automático antes de qualquer edição)
- Desativar serviços do Windows (`sc config ... start= demand`)
- Desativar tarefas agendadas de apps
- Regras de firewall criadas por programas
- `DISM /Online /Cleanup-Image /StartComponentCleanup` (reduzir a pasta
  WinSxS)
- Varredura do Windows Defender via PowerShell

## Stack

Python 3 · colorama (tela estilo terminal) · send2trash (apagar sempre pra
Lixeira) · Pytest · winreg (biblioteca padrão do Python para registro do
Windows)

Desenvolvido com apoio do Claude Code.
