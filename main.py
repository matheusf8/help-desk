"""
HELP DESK - FAXINEIRA DE PC
Programa de suporte tecnico para limpar e diagnosticar um Windows 11.

Como o codigo esta organizado (a "arquitetura"):
  main.py              -> so cuida de TELA e MENU (o que aparece pro usuario)
  faxineira/diagnostico.py -> funcoes que so LEEM informacao (nunca apagam nada)
  faxineira/limpeza.py     -> funcoes que mexem em arquivo (sempre via Lixeira)
  faxineira/utils.py       -> ferramentas pequenas usadas pelos outros dois

Essa separacao tem um nome: cada arquivo cuida de UMA responsabilidade so.
Assim, se um dia quiser trocar a tela por uma pagina web (FastAPI, por
exemplo), so main.py muda - o resto continua igual.

Regra de seguranca numero 1 (sempre): nada e apagado direto.
Tudo vai primeiro pra Lixeira, e o usuario confirma antes de qualquer limpeza.
"""
import os
import sys

from colorama import Fore, Back, Style, init as colorama_init

from faxineira import diagnostico, limpeza
from faxineira.utils import formatar_bytes, imprimir_robo, confirmar, linha

# colorama_init liga o suporte a cores no terminal do Windows (sem isso,
# os codigos de cor apareceriam como texto estranho em vez de colorir).
colorama_init(autoreset=False)

VERDE = Fore.GREEN
TELA_PRETA = Back.BLACK


def limpar_tela() -> None:
    """Limpa o que esta escrito no terminal. 'cls' no Windows, 'clear' no resto."""
    os.system("cls" if os.name == "nt" else "clear")


def pintar_tela() -> None:
    """Deixa o fundo preto e o texto verde, estilo terminal de filme de hacker."""
    sys.stdout.write(TELA_PRETA + VERDE)
    limpar_tela()


# Arte feita so de texto (chamada de "ASCII art"). O 'r' antes das aspas
# (r""") significa "string crua" - evita que as barras invertidas \ da
# arte sejam interpretadas como comando especial do Python.
BANNER = r"""
 _   _ ____  _     ____    ____  _____ ____  _  __
| | | |  _ \| |   |  _ \  |  _ \| ____/ ___|| |/ /
| |_| | |_) | |   | |_) | | | | |  _| \___ \| ' /
|  _  |  __/| |___|  __/  | |_| | |___ ___) | . \
|_| |_|_|   |_____|_|     |____/|_____|____/|_|\_\

        F A X I N E I R A   D E   P C   v1.0
"""

REGRAS_SEGURANCA = """
[ REGRAS DE SEGURANCA DESTE SISTEMA ]

  > Nada e apagado direto. Tudo vai pra Lixeira primeiro.
  > A Lixeira so e esvaziada se VOCE confirmar, no final.
  > Nunca mexe em: Windows, drivers, antivirus, WebView2/EdgeCore.
  > Pasta/programa que o sistema nao reconhece: SEMPRE pergunta antes.
  > Diagnostico (opcoes 1 a 5) nunca apaga nada, so mostra informacao.
"""

MENU = """
   DIAGNOSTICO (so mostra, nao mexe em nada)
 1 - Espaco do disco C:
 2 - Tamanho das pastas de cada programa
 3 - Maiores pastas do usuario (Downloads, Documentos...)
 4 - Itens de inicializacao (o que abre sozinho com o Windows)
 5 - Ver regras de seguranca de novo

   LIMPEZA (sempre manda pra Lixeira primeiro)
 6 - Limpar Temp (%TEMP% e C:\\Windows\\Temp)
 7 - Limpar cache do Chrome
 8 - Procurar restos de programas desinstalados (AppData)
 9 - Esvaziar a Lixeira

 0 - Sair
"""


# ---------------------------------------------------------------------------
# Cada funcao "rodar_*" abaixo e UMA opcao do menu. Elas fazem a mesma
# coisa sempre: 1) chamam uma funcao de diagnostico.py ou limpeza.py pra
# fazer o trabalho de verdade, e 2) mostram o resultado bonito na tela.
# Ou seja: a "logica" (o que acontece) mora nos outros arquivos; aqui so
# mora a "apresentacao" (o que o usuario ve).
# ---------------------------------------------------------------------------


def rodar_diagnostico_disco() -> None:
    dados = diagnostico.espaco_disco()
    print(linha("-"))
    print(diagnostico.formatar_relatorio_espaco(dados))
    print(linha("-"))


def rodar_maiores_pastas_programas() -> None:
    print(linha("-"))
    print(">> Lendo Program Files, Program Files (x86) e ProgramData...")
    print(">> (pode demorar um pouco em discos cheios)")
    for nome, tamanho in diagnostico.maiores_pastas_programas():
        print(f"  {formatar_bytes(tamanho):>10}   {nome}")
    print(linha("-"))


def rodar_maiores_pastas_usuario() -> None:
    print(linha("-"))
    for nome, tamanho in diagnostico.maiores_pastas_usuario():
        print(f"  {formatar_bytes(tamanho):>10}   {nome}")
    print(linha("-"))


def rodar_itens_inicializacao() -> None:
    print(linha("-"))
    itens = diagnostico.itens_inicializacao()
    if not itens:
        print("  Nenhum item encontrado nas chaves de inicializacao lidas.")
    for item in itens:
        print(f"  - {item}")
    print(linha("-"))


def rodar_limpeza_temp() -> None:
    """
    Exemplo completo do fluxo de seguranca: primeiro MOSTRA quantos
    itens existem, depois PERGUNTA, e so limpa de verdade se a resposta
    for sim. As outras funcoes de limpeza seguem esse mesmo padrao.
    """
    itens = limpeza.itens_temp()
    print(linha("-"))
    print(f">> Encontrei {len(itens)} item(ns) em pastas de Temp.")
    if not itens:
        print(linha("-"))
        return
    if not confirmar("Mandar tudo isso pra Lixeira?"):
        print(">> Cancelado, nada foi tocado.")
        print(linha("-"))
        return
    sucesso, falhas = limpeza.mandar_para_lixeira(itens)
    print(f">> {len(sucesso)} item(ns) mandado(s) pra Lixeira.")
    if falhas:
        # Falhar aqui e normal: um arquivo de Temp pode estar sendo
        # usado por outro programa aberto naquele momento.
        print(f">> {len(falhas)} item(ns) estavam em uso e nao puderam ser movidos (normal).")
    print(linha("-"))


def rodar_limpeza_chrome() -> None:
    pasta = limpeza.pasta_cache_chrome()
    print(linha("-"))
    if pasta is None:
        print(">> Cache do Chrome nao encontrado nesta maquina.")
        print(linha("-"))
        return
    itens = limpeza.listar_itens_de(pasta)
    print(f">> Encontrei {len(itens)} item(ns) no cache do Chrome.")
    if confirmar("Mandar pra Lixeira?"):
        sucesso, falhas = limpeza.mandar_para_lixeira(itens)
        print(f">> {len(sucesso)} item(ns) mandado(s) pra Lixeira.")
    else:
        print(">> Cancelado.")
    print(linha("-"))


def rodar_restos_appdata() -> None:
    """
    Essa e a opcao mais delicada do programa, por isso confirma UMA
    pasta de cada vez (em vez de uma pergunta so pra tudo junto) - o
    "candidato" pode, as vezes, nao ser lixo de verdade.
    """
    print(linha("-"))
    print(">> Comparando pastas do AppData com os programas instalados...")
    suspeitas = limpeza.pastas_appdata_suspeitas()
    if not suspeitas:
        print(">> Nenhuma pasta suspeita encontrada.")
        print(linha("-"))
        return

    print(f">> {len(suspeitas)} pasta(s) nao bateram com nenhum programa instalado:")
    for i, pasta in enumerate(suspeitas, start=1):
        print(f"  [{i}] {pasta}")

    print("\n  Essas pastas PODEM ser de programas ja desinstalados, ou de algo")
    print("  que voce ainda usa mas o nome e diferente. Confirme uma por uma.")

    for pasta in suspeitas:
        if confirmar(f"Mandar '{pasta.name}' pra Lixeira?"):
            sucesso, falhas = limpeza.mandar_para_lixeira([pasta])
            if sucesso:
                print(f"  >> '{pasta.name}' foi pra Lixeira.")
            else:
                print(f"  >> Nao consegui mover '{pasta.name}' (talvez esteja em uso).")
    print(linha("-"))


def rodar_esvaziar_lixeira() -> None:
    """A unica acao do programa sem volta - por isso o aviso extra antes de perguntar."""
    print(linha("-"))
    print(">> Isso esvazia a Lixeira do Windows DE VERDADE. Depois disso, nao tem volta.")
    if confirmar("Tem certeza que quer esvaziar a Lixeira agora?"):
        limpeza.esvaziar_lixeira()
        print(">> Lixeira esvaziada.")
    else:
        print(">> Cancelado.")
    print(linha("-"))


# ACOES liga cada numero do menu a sua funcao correspondente.
# Isso evita escrever um "if escolha == '1': ... elif escolha == '2': ..."
# gigante - o programa so olha no dicionario qual funcao chamar.
ACOES = {
    "1": rodar_diagnostico_disco,
    "2": rodar_maiores_pastas_programas,
    "3": rodar_maiores_pastas_usuario,
    "4": rodar_itens_inicializacao,
    "5": lambda: print(REGRAS_SEGURANCA),
    "6": rodar_limpeza_temp,
    "7": rodar_limpeza_chrome,
    "8": rodar_restos_appdata,
    "9": rodar_esvaziar_lixeira,
}


def main() -> None:
    """O loop principal: mostra o menu, espera o numero, roda a acao, repete."""
    pintar_tela()
    print(VERDE + BANNER)
    imprimir_robo("Sistema iniciado. Analisando ambiente...", atraso=0.02)
    print(VERDE + REGRAS_SEGURANCA)

    while True:
        print(VERDE + MENU)
        escolha = input(VERDE + "Escolha uma opcao: " + Style.RESET_ALL + VERDE).strip()

        if escolha == "0":
            imprimir_robo("Encerrando sistema. Ate a proxima.", atraso=0.02)
            break

        acao = ACOES.get(escolha)
        if acao is None:
            print(Fore.RED + "Opcao invalida." + VERDE)
            continue

        acao()
        input(Fore.CYAN + "\n[ENTER para voltar ao menu] " + Style.RESET_ALL + VERDE)
        pintar_tela()
        print(VERDE + BANNER)

    print(Style.RESET_ALL)  # devolve o terminal pras cores normais ao sair


if __name__ == "__main__":
    # Essa linha garante que o programa so roda se for Windows (ele usa
    # winreg e Lixeira do Windows, que nao existem no Mac/Linux).
    if os.name != "nt":
        print("Este programa foi feito para Windows 11.")
        sys.exit(1)
    main()
