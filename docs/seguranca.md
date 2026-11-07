# Segurança

O que o programa protege, como, e o que **ainda não** protege. Ferramenta de limpeza mexe no computador de outra pessoa: o risco não é invasão, é **apagar o que não devia**.

## Regras e onde elas moram no código

| Regra | Onde é garantida |
|---|---|
| Nada é apagado direto: tudo vai para a Lixeira | `limpeza.mandar_para_lixeira()` usa `send2trash`; não existe `os.remove` nem `shutil.rmtree` no projeto |
| Nenhuma limpeza sem confirmação | `menu.py`: `_limpar_em_lote_com_confirmacao()`, `rodar_restos_appdata()` e `rodar_esvaziar_lixeira()` chamam `confirmar()` antes (testado em `test_menu.py`) |
| AppData: uma pergunta por pasta | `rodar_restos_appdata()` pergunta dentro do `for` |
| Diagnóstico nunca altera nada | `diagnostico.py` não tem função de escrita (só `winreg.EnumValue`, `QueryValueEx`, `shutil.disk_usage`, `iterdir`, `stat`) |
| Nunca mexe em Windows, drivers, antivírus, WebView2/EdgeCore | `limpeza.eh_protegido()`, usada na lista de suspeitas **e** dentro de `mandar_para_lixeira()` |
| Só a opção 9 não tem volta | `esvaziar_lixeira()`; o menu avisa antes e pede confirmação |

## Revisão feita na reestruturação

| Achado | Gravidade | O que foi feito |
|---|---|---|
| A regra de itens protegidos existia só como texto na tela | Média | Virou código (`eh_protegido`) e tem teste (etapa 3 e 4) |
| Limpeza do Chrome pedia confirmação mesmo sem itens e escondia as falhas | Baixa | Unificada com a de Temp (etapa 2) |
| Nenhum teste cobria o arquivo que apaga coisas | Média | 25 testes em `test_limpeza.py` e 12 em `test_menu.py` (etapa 4) |
| Risco de um teste futuro esvaziar a Lixeira de verdade | Média | Fixture `autouse` em `conftest.py` que proíbe `send2trash` e `esvaziar_lixeira` reais |

## Riscos que restam (conhecidos)

- **A heurística do AppData pode errar.** Ela compara o nome da pasta com os nomes de "Aplicativos instalados" por trecho de texto. Programa portátil, jogo de launcher ou app com nome diferente no registro aparece como "suspeito" mesmo em uso. Por isso a confirmação é pasta por pasta e o item vai para a Lixeira, não é apagado.
- **A lista de protegidos é por palavra, não por prova.** O que não está na lista passa pela confirmação, mas só ela segura.
- **A opção 9 esvazia a Lixeira inteira**, inclusive o que a pessoa jogou lá antes de usar o programa, não só o que o programa moveu.
- **Item grande demais para a Lixeira.** O Windows pode apagar de vez um item maior que o limite configurado da Lixeira. Não testei esse caso; vale conferir o tamanho da Lixeira antes de limpar algo muito grande.
- **Sem registro (log) do que foi movido.** Depois, a única forma de saber é abrir a Lixeira.
- **Sem modo de simulação (*dry-run*).** Hoje a pessoa vê quantos itens vão, mas não a lista completa antes de aceitar.
- **A limpeza de `C:\Windows\Temp` pode falhar sem permissão de administrador.** Os itens caem em "não puderam ser movidos", o que é seguro.

## Próximos passos de segurança
1. Gravar um `limpeza.log` com data, caminho e resultado de cada item movido.
2. Opção de ver a lista completa antes de confirmar (*dry-run*).
3. Proteger também por **caminho** (`Program Files`, `System32`), além do nome.
4. Para a v2 (registro, serviços, firewall): backup `.reg` automático antes de qualquer edição, já previsto no roadmap.
