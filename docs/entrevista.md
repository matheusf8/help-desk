# Roteiro de entrevista: Help Desk — Faxineira de PC

Responda **com as suas palavras**: estas são só a base. Fórmula: **o que fiz → onde está no código → como chego no resultado**. Se alguma resposta abaixo não fizer sentido para você, abra o arquivo citado e leia antes de usar.

## Pitch de 1 minuto
> "Fiz uma ferramenta de suporte técnico em **Python** que roda no Windows e ajuda a **diagnosticar e limpar** o computador por um menu numerado. A parte de diagnóstico só **lê**: espaço em disco, pastas maiores, o que abre junto com o Windows. A de limpeza mexe em Temp, cache do Chrome e restos de programa desinstalado.
> O que mais me preocupei foi **não apagar nada que não devia**: tudo vai para a **Lixeira**, nada é apagado direto, toda limpeza pede **confirmação**, e itens do Windows, drivers e antivírus são **recusados pelo código**, não só pela tela.
> Separei o código em camadas: tela, leitura, escrita e apoio. E escrevi **54 testes** que não tocam no disco de verdade, usando pastas de mentira e uma Lixeira falsa.
> O que melhoraria: um **log** do que foi movido, um modo de **simulação** e proteger também por caminho."

## Perguntas e respostas curtas

### Design
1. **Como você organizou o código e por quê?**
   Em camadas: `menu.py` (tela), `diagnostico.py` (só lê), `limpeza.py` (escreve), `utils.py` (apoio). Cada arquivo tem uma responsabilidade, então dá para testar `limpeza` sem simular tela e trocar a tela sem mexer na lógica. (`docs/arquitetura.md`)
2. **Por que `diagnostico.py` e `limpeza.py` são separados?**
   Para que as opções de diagnóstico sejam seguras *por construção*: o arquivo não tem nenhuma função que apague. Quem lê o código vê isso de cara.
3. **Por que não usou Docker?**
   O programa precisa mexer no Windows de verdade (AppData, registro, Lixeira). Docker isola o contêiner do computador de propósito, então não ajudaria.
4. **Para que serve o dicionário `ACOES` no menu?**
   Liga cada número do menu à função certa. Evita um `if/elif` gigante: o programa consulta o dicionário.
5. **Por que `main.py` importa o menu só depois de checar o sistema?**
   Porque o pacote importa `winreg`, que só existe no Windows. Em outro sistema, importar antes quebraria com um erro de módulo antes da mensagem amigável.

### Segurança
6. **Como garante que não apaga nada importante?**
   Em camadas: (1) lista antes, (2) pede confirmação, (3) manda para a Lixeira e não apaga, (4) `eh_protegido()` recusa nomes como Windows, Microsoft, drivers, antivírus, WebView. A confirmação do AppData é pasta por pasta porque a comparação com programas instalados é uma heurística e pode errar.
7. **O que é `eh_protegido` e por que olha só o nome do item?**
   É a lista de nomes que o programa nunca move. Se olhasse o caminho inteiro, tudo dentro de `C:\Windows\Temp` ficaria protegido por estar numa pasta chamada Windows, e a limpeza de Temp pararia de funcionar.
8. **Por que duas listas, parcial e exata?**
   Nome curto como `amd` casaria com qualquer palavra que tenha essas três letras. Para nomes curtos só vale igualdade exata.
9. **Por que a trava está em dois lugares?**
   Defesa em camadas: ela filtra a lista de suspeitas e também fica dentro de `mandar_para_lixeira`, que é a última barreira. Se outra função deixar passar algo delicado, ainda assim ele não vai.
10. **Qual é o maior risco que ainda existe?**
    A heurística do AppData errar: um programa portátil pode parecer "resto". Por isso é pasta por pasta e vai para a Lixeira. Outro: a opção 9 esvazia a Lixeira **inteira**, não só o que o programa moveu. (`docs/seguranca.md`)

### Testes
11. **Como testar um programa que apaga arquivos sem apagar nada?**
    Pastas de mentira com `tmp_path`, variáveis de ambiente (`TEMP`, `APPDATA`) apontando para elas, e a Lixeira trocada por uma função falsa com `monkeypatch`. No teste só se verifica o que a função falsa **recebeu**.
12. **O que é o `conftest.py` com `autouse` que você criou?**
    Uma rede de segurança: troca `send2trash` e `esvaziar_lixeira` por funções que falham. Se um teste futuro esquecer de usar a versão falsa, ele quebra em vez de mexer na Lixeira real.
13. **Como sabe que os testes testam de verdade?**
    Quebrei o código de propósito, três vezes: tirei a trava de protegidos, limpei Temp sem perguntar e tirei o filtro do AppData. Um teste diferente falhou em cada caso. Depois restaurei.
14. **O que não está testado?**
    As funções que leem o registro do Windows (`itens_inicializacao`, `programas_instalados`) dependem da máquina. E os testes só rodam no Windows.

### Python
15. **Para que serve o `winreg`?**
    Biblioteca padrão para ler o registro do Windows. Uso para listar os programas instalados (`Uninstall`) e os itens que iniciam com o sistema (`Run`). Só leio, nunca altero.
16. **Por que `mandar_para_lixeira` devolve duas listas?**
    No Windows é normal um arquivo estar em uso. Devolver `(sucesso, falhas)` deixa a tela contar o que aconteceu sem o programa quebrar no meio.
17. **Qual foi o bug que você encontrou na própria versão 1?**
    A limpeza do Chrome não tratava lista vazia nem contava as falhas, e a de Temp tratava. Eram dois códigos copiados que ficaram diferentes. Juntei os dois numa função só.

## Perguntas que você deve ser capaz de fazer à empresa
- Como vocês fazem suporte remoto hoje? Têm algum script padrão?
- Existe processo de revisão de código para scripts que mexem em máquina de cliente?

## O que não falar
- Que a ferramenta é "100% segura". Diga que tem camadas de proteção e **riscos conhecidos** (a lista está em `docs/seguranca.md`).
- Que não usou IA. O projeto foi feito com apoio do Claude Code; o que você deve ser capaz de fazer é **explicar** cada parte acima.

## Treino sugerido
Sem olhar o código, explique em voz alta o caminho completo da opção 8 (restos do AppData), da leitura do registro até a pasta ir para a Lixeira. Depois confira com `docs/arquitetura.md`.
