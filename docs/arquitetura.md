# Arquitetura

Como o código está dividido e por quê. A regra que guia tudo: **cada arquivo cuida de uma responsabilidade só.**

## Camadas

```mermaid
flowchart TD
    M[main.py<br/>porta de entrada] --> MENU[faxineira/menu.py<br/>tela, perguntas e loop]
    MENU --> T[faxineira/textos.py<br/>banner, menu, regras]
    MENU --> D[faxineira/diagnostico.py<br/>só LÊ]
    MENU --> L[faxineira/limpeza.py<br/>mexe em arquivo, sempre via Lixeira]
    MENU --> U[faxineira/utils.py<br/>funções puras e entrada do usuário]
    D --> U
    L --> S[(send2trash<br/>Lixeira do Windows)]
    D --> W[(winreg<br/>registro do Windows)]
    L --> W
```

| Camada | Arquivo | Pode fazer | Não pode fazer |
|---|---|---|---|
| Entrada | `main.py` | checar se é Windows e chamar o menu | ter lógica de limpeza ou texto |
| Tela | `faxineira/menu.py` | imprimir, perguntar, decidir o fluxo | apagar arquivo por conta própria: sempre chama `limpeza` |
| Texto | `faxineira/textos.py` | guardar texto | ter lógica |
| Leitura | `faxineira/diagnostico.py` | ler disco, pastas e registro | apagar, mover ou alterar qualquer coisa |
| Escrita | `faxineira/limpeza.py` | mandar para a Lixeira, esvaziá-la | apagar direto; mexer em item protegido |
| Apoio | `faxineira/utils.py` | formatar bytes, calcular %, `confirmar` | depender do disco |

**A seta só vai para baixo:** `menu` conhece `limpeza`, mas `limpeza` não conhece `menu`. Por isso dá para testar `limpeza.py` sem simular tela nenhuma, e trocar a tela por uma página web mudaria só o `menu.py`.

## Fluxo de uma limpeza (opção 6, Temp)

```mermaid
sequenceDiagram
    participant U as Pessoa
    participant M as menu.py
    participant L as limpeza.py
    participant X as send2trash
    U->>M: digita 6
    M->>L: itens_temp()
    L-->>M: lista de arquivos (só lê)
    M->>U: "Encontrei N itens. Mandar pra Lixeira? [s/n]"
    alt responde n
        M-->>U: "Cancelado, nada foi tocado"
    else responde s
        M->>L: mandar_para_lixeira(itens)
        loop cada item
            L->>L: eh_protegido? então vai para "falhas"
            L->>X: send2trash(item)
        end
        L-->>M: (sucesso, falhas)
        M-->>U: "X mandado(s) pra Lixeira, Y não puderam ser movidos"
    end
```

Os três pontos de segurança estão na ordem: **listar** (só lê) → **confirmar** (pessoa decide) → **mandar para a Lixeira** (com a trava de protegidos).

## Estrutura de pastas

```
help/
├── main.py                  ← porta de entrada
├── faxineira/
│   ├── menu.py              ← funções rodar_*, ACOES e o loop executar()
│   ├── textos.py            ← BANNER, REGRAS_SEGURANCA, MENU
│   ├── diagnostico.py       ← espaço, pastas grandes, inicialização
│   ├── limpeza.py           ← Temp, cache do Chrome, AppData, Lixeira, eh_protegido
│   └── utils.py             ← formatar_bytes, calcular_percentual, confirmar...
├── tests/                   ← 54 testes (sem tocar no disco de verdade)
├── docs/                    ← esta documentação
├── pytest.ini
└── requirements.txt
```

## Por que não Docker
O programa precisa enxergar e mexer direto no Windows da pessoa (AppData, registro, Temp, Lixeira). Docker isola o contêiner do computador de propósito, então não serve aqui.

## Só funciona no Windows
`diagnostico.py` e `limpeza.py` importam `winreg`, que só existe no Windows. Por isso `main.py` checa `os.name` **antes** de importar o menu: em outro sistema a pessoa lê "Este programa foi feito para Windows 11" em vez de um erro de módulo.
