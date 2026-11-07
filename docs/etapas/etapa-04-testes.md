# Etapa 4 — Testes

**Objetivo:** testar o que apaga coisas (`limpeza.py`) e o fluxo de confirmação (`menu.py`), sem nunca tocar no disco de verdade.
**Resultado:** 54 testes passando (eram 10); os 3 bugs plantados de propósito foram pegos.

## Conceitos novos
| Conceito | Analogia |
|---|---|
| **`tmp_path`** | uma pasta de mentira que o pytest cria e apaga sozinho, para treinar sem risco |
| **`monkeypatch`** | trocar uma peça por uma falsa só durante o teste (a Lixeira de mentira) |
| **Fixture `autouse`** | regra que vale para todos os testes sem ninguém precisar lembrar |
| **Espião (spy)** | função falsa que só anota se foi chamada e com o quê |
| **Teste de mutação manual** | quebrar o código de propósito para ver se algum teste reclama |

## Passo a passo (o que foi feito e como)

### 1. Rede de segurança: `tests/conftest.py`
Uma fixture `autouse` troca `send2trash` e `esvaziar_lixeira` por funções que **levantam erro**. Se um teste novo esquecer de trocar a peça perigosa por uma falsa, ele falha com "Teste tentou mexer no disco de verdade", em vez de mexer na Lixeira de quem roda os testes.

### 2. `tests/test_limpeza.py` (25 casos)
| Função | O que se garante |
|---|---|
| `listar_itens_de` | só o primeiro nível; pasta inexistente e arquivo no lugar de pasta devolvem `[]` |
| `eh_protegido` | nomes delicados protegidos; `Samdle` não (nome curto só vale exato); pastas de cima ignoradas |
| `mandar_para_lixeira` | cada item é enviado; item "em uso" vai para `falhas`; item protegido **nem é tentado** |
| `itens_temp` / `pastas_temp` | junta a Temp do usuário e a do Windows (variáveis `TEMP` e `windir` apontando para pastas de mentira) |
| `pasta_cache_chrome` | acha o cache, ou devolve `None` sem Chrome |
| `pastas_appdata_suspeitas` | só devolve o que não combina com programa instalado; ignora arquivo solto e item protegido; **só lista, não apaga** |
| `esvaziar_lixeira` | chama o Windows com os 3 flags (sem confirmação, sem barra, sem som), usando um "Windows" falso |

### 3. `tests/test_menu.py` (12 casos)
Aqui o que importa não é o texto, é a **regra: sem "sim", nada vai para a Lixeira.**
- Temp: cancelado não move; confirmado move; vazio nem pergunta.
- Chrome: não instalado; cache vazio nem pergunta (o bug da v1); falhas são contadas.
- AppData: pergunta **uma vez por pasta** e só move a aceita.
- Esvaziar a Lixeira: sem confirmação, não esvazia.
- Menu: as opções 1 a 9 têm ação; opção inválida avisa e `0` encerra.

### 4. `tests/test_utils.py`
Entraram `confirmar` (aceita `s`, `SIM`, `n`, `nao`, `não`; pergunta de novo se digitar outra coisa) e `linha`.

## Verificação
| Checagem | Resultado |
|---|---|
| `pytest` | 54 passaram |
| Bug plantado: tirar a checagem de protegido do `mandar_para_lixeira` | `test_mandar_para_lixeira_nao_tenta_item_protegido` falhou |
| Bug plantado: limpar Temp sem perguntar | `test_temp_sem_confirmacao_nao_move_nada` falhou |
| Bug plantado: tirar o filtro de protegidos das suspeitas do AppData | `test_appdata_suspeitas_so_devolve_o_que_nao_combina` falhou |

Depois de cada bug plantado o código foi restaurado e a suíte voltou a 54 verdes.

## Limites conscientes
- `diagnostico.py` continua testado só nas funções puras (`tamanho_pasta`, `maiores_pastas`). As que leem o registro do Windows (`itens_inicializacao`, `programas_instalados`) dependem da máquina e não têm teste.
- Os testes só rodam no Windows (o pacote importa `winreg`). Um CI precisaria de `windows-latest`.
- Não há teste que abra a tela de verdade; o fluxo é verificado pelas funções `rodar_*` e pelo loop com `input` trocado.
