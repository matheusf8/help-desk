# Decisões técnicas

Registro do **porquê** de cada escolha. É o material para responder "por que você fez assim?" na entrevista.

| # | Decisão | Motivo | Alternativa e quando usaria |
|---|---|---|---|
| 1 | **Python puro, sem Docker** | O programa precisa mexer no Windows de verdade (AppData, registro, Lixeira). Contêiner isola isso de propósito. | Docker, se fosse uma API ou serviço que não depende da máquina. |
| 2 | **Tudo vai para a Lixeira (`send2trash`)** | Errou? A pessoa recupera. É como arrastar o arquivo com o mouse. | Apagar direto (`os.remove`): mais simples e sem volta, perigoso demais para uma ferramenta de limpeza. |
| 3 | **Confirmação antes de qualquer limpeza** | Nenhuma ação destrutiva sem um "sim" explícito. | Modo `--sim` automático para quem já confia, com *dry-run* (simulação) antes. |
| 4 | **AppData: confirmar pasta por pasta** | A comparação com os programas instalados é uma heurística e pode errar. Uma pergunta por pasta dá chance de recusar a duvidosa. | Uma pergunta só para tudo (mais rápido, mais arriscado). |
| 5 | **Camadas: tela / leitura / escrita / apoio** | Cada arquivo com uma responsabilidade: fácil de ler, testar e trocar. | Tudo em um arquivo só (rápido de escrever, difícil de testar). |
| 6 | **`diagnostico.py` só lê** | As opções 1 a 5 são seguras por construção: o arquivo não tem nenhuma função que apague. | — |
| 7 | **`eh_protegido()` no código, não só no texto** (etapa 3) | "Nunca mexe em Windows, drivers..." era só uma frase na tela. Agora o código recusa. | Lista de caminhos protegidos (ex.: `C:\Program Files`) em vez de nomes. |
| 8 | **Duas listas de nomes protegidos: parcial e exata** | Nome curto como `amd` casaria com qualquer palavra que tenha essas letras. | Expressões regulares (mais poderosas, mais difíceis de ler). |
| 9 | **`eh_protegido` olha só o nome do item, não o caminho** | Olhando o caminho, tudo dentro de `Windows\Temp` ficaria protegido e a limpeza de Temp pararia de funcionar. | — |
| 10 | **Trava em dois pontos** (lista de suspeitas e `mandar_para_lixeira`) | Defesa em camadas: se uma falhar, a outra segura. | Só uma checagem (mais simples, um ponto único de falha). |
| 11 | **`mandar_para_lixeira` devolve `(sucesso, falhas)`** | Arquivo em uso é normal no Windows. Devolver as duas listas permite avisar sem o programa quebrar. | Levantar exceção no primeiro erro (interrompe a limpeza no meio). |
| 12 | **Fluxo de limpeza em lote numa função só** (etapa 2) | Temp e Chrome tinham cópias do mesmo fluxo e ficaram diferentes (bug). Um lugar = uma regra. | — |
| 13 | **`main.py` importa o menu só depois de checar o Windows** | O pacote importa `winreg`; em outro sistema quebraria antes da mensagem amigável. | Capturar `ImportError`. |
| 14 | **Testes com `tmp_path` e `monkeypatch`** | Testar limpeza sem apagar nada de verdade: pastas de mentira e Lixeira falsa. | Máquina virtual de teste (pesado para este tamanho). |
| 15 | **Fixture `autouse` que proíbe a Lixeira real** | Se um teste futuro esquecer o `monkeypatch`, ele falha em vez de mexer na Lixeira de quem roda. | Confiar na atenção de quem escreve o teste. |
| 16 | **`colorama` iniciado dentro de `executar()`** | Importar um módulo não deve mudar o terminal; atrapalha teste. | Iniciar no topo do arquivo (como era na v1). |
| 17 | **Texto de tela sem acento** | Terminal do Windows pode mostrar acento errado dependendo da página de código. | `chcp 65001` / UTF-8 no terminal. |
| 18 | **Itens mais arriscados ficaram para a v2** | Registro, serviços, firewall e `DISM` podem quebrar o Windows. Só entram com backup e teste. | — |
