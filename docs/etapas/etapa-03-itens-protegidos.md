# Etapa 3 — Trava de itens protegidos

**Objetivo:** fazer o código cumprir a regra que a tela promete: "Nunca mexe em Windows, drivers, antivírus, WebView2/EdgeCore".
**Resultado:** `eh_protegido()` em `limpeza.py`, usada em dois pontos; a promessa virou garantia.

## O problema
Na v1 a frase estava só em `REGRAS_SEGURANCA` (texto). Nada no código impedia, por exemplo, que a pasta `Microsoft` do AppData fosse oferecida como "resto de programa desinstalado" e mandada para a Lixeira se a pessoa confirmasse sem ler direito. Regra que só existe no texto da tela é uma promessa; regra no código é uma garantia.

## Passo a passo (o que foi feito e como)

### 1. A lista de nomes protegidos
Em `faxineira/limpeza.py`:
- `NOMES_PROTEGIDOS_PARCIAIS`: basta o nome **conter** a palavra (`windows`, `microsoft`, `webview`, `edgecore`, `msedge`, `defender`, `antivirus`, `driver`).
- `NOMES_PROTEGIDOS_EXATOS`: o nome precisa ser **igual** (`amd`, `intel`, `nvidia`, `realtek`).

**Por que duas listas?** Nome curto como `amd` casaria com qualquer pasta que tenha essas três letras no meio. Exato evita falso positivo; parcial pega variações (`Microsoft Edge`, `WebView2Runtime`).

### 2. `eh_protegido(caminho)`
Olha **só o nome do próprio item**, não as pastas de cima. Se olhasse o caminho inteiro, tudo dentro de `C:\Windows\Temp` viraria "protegido" só por estar numa pasta chamada Windows, e a limpeza de Temp pararia de funcionar.

### 3. Duas barreiras
| Onde | O que faz |
|---|---|
| `pastas_appdata_suspeitas()` | Nem **mostra** pastas protegidas como suspeitas. |
| `mandar_para_lixeira()` | **Recusa** item protegido: ele cai em `falhas`, sem chamar o `send2trash`. |

A segunda é a **última barreira**: mesmo que outra função deixe passar um item delicado, ele não vai para a Lixeira. É o princípio de "defesa em camadas": não depender de um único ponto estar certo.

### 4. Mensagem na tela
`menu.mostrar_resultado_movimento()` diz "em uso ou protegidos", porque quem vê "falhou" não sabe qual dos dois foi.

## Limites conscientes
- É uma lista de **palavras**, não uma prova de que o item é seguro. Item fora da lista continua passando pela confirmação do usuário.
- Um arquivo de Temp com `windows` ou `microsoft` no nome nunca é limpo. Preferi errar para o lado seguro.
- Não protege pelo **caminho** (ex.: `C:\Program Files`). O programa já não lista essas pastas para limpeza; só as lê no diagnóstico.

## Verificação
| Checagem | Resultado |
|---|---|
| `pytest` | 10 passaram (os testes novos desta função vêm na etapa 4) |
| `eh_protegido` na mão | `Microsoft` → sim, `AMD` → sim, `Samdle` → não, `Windows\Temp\abc.tmp` → não, `Discord` → não |
