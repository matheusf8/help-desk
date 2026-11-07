"""
menu.py - a TELA do programa: o menu, as perguntas e o loop principal.

Cada funcao "rodar_*" abaixo e UMA opcao do menu. Elas fazem sempre a
mesma coisa: 1) chamam uma funcao de diagnostico.py ou limpeza.py pra
fazer o trabalho de verdade, e 2) mostram o resultado na tela.
Ou seja: a "logica" (o que acontece) mora nos outros arquivos; aqui so
mora a "apresentacao" (o que o usuario ve). Se um dia a tela virar uma
pagina web, so este arquivo muda.
"""
import os
import sys

from colorama import Fore, Back, Style, init as colorama_init

from faxineira import diagnostico, limpeza
from faxineira.textos import BANNER, MENU, REGRAS_SEGURANCA
from faxineira.utils import formatar_bytes, imprimir_robo, confirmar, linha

VERDE = Fore.GREEN
TELA_PRETA = Back.BLACK


def limpar_tela() -> None:
    """Limpa o que esta escrito no terminal. 'cls' no Windows, 'clear' no resto."""
    os.system("cls" if os.name == "nt" else "clear")


def pintar_tela() -> None:
    """Deixa o fundo preto e o texto verde, estilo terminal de filme de hacker."""
    sys.stdout.write(TELA_PRETA + VERDE)
    limpar_tela()


def mostrar_resultado_movimento(sucesso: list, falhas: list) -> None:
    """
    Conta pro usuario o que aconteceu depois de mandar itens pra Lixeira.
    Falhar aqui e normal: um arquivo pode estar em uso por outro programa
    aberto naquele momento, ou ser um item protegido (veja limpeza.eh_protegido).
    """
    print(f">> {len(sucesso)} item(ns) mandado(s) pra Lixeira.")
    if falhas:
        print(f">> {len(falhas)} item(ns) nao puderam ser movidos (em uso ou protegidos - normal).")


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


def _limpar_em_lote_com_confirmacao(itens: list, pergunta: str) -> None:
    """
    O fluxo de seguranca das limpezas em lote (Temp e Chrome): primeiro
    MOSTRA quantos itens existem, depois PERGUNTA, e so limpa de verdade
    se a resposta for sim. As duas opcoes usam esta mesma funcao pra nao
    ficarem diferentes uma da outra (na v1 o Chrome nao tratava lista
    vazia nem as falhas).
    """
    print(f">> Encontrei {len(itens)} item(ns).")
    if not itens:
        return
    if not confirmar(pergunta):
        print(">> Cancelado, nada foi tocado.")
        return
    sucesso, falhas = limpeza.mandar_para_lixeira(itens)
    mostrar_resultado_movimento(sucesso, falhas)


def rodar_limpeza_temp() -> None:
    print(linha("-"))
    _limpar_em_lote_com_confirmacao(limpeza.itens_temp(), "Mandar tudo isso pra Lixeira?")
    print(linha("-"))


def rodar_limpeza_chrome() -> None:
    print(linha("-"))
    pasta = limpeza.pasta_cache_chrome()
    if pasta is None:
        print(">> Cache do Chrome nao encontrado nesta maquina.")
    else:
        _limpar_em_lote_com_confirmacao(limpeza.listar_itens_de(pasta), "Mandar o cache do Chrome pra Lixeira?")
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
            sucesso, _ = limpeza.mandar_para_lixeira([pasta])
            if sucesso:
                print(f"  >> '{pasta.name}' foi pra Lixeira.")
            else:
                print(f"  >> Nao consegui mover '{pasta.name}' (em uso ou protegida).")
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


def executar() -> None:
    """O loop principal: mostra o menu, espera o numero, roda a acao, repete."""
    # colorama_init liga o suporte a cores no terminal do Windows (sem isso,
    # os codigos de cor apareceriam como texto estranho em vez de colorir).
    colorama_init(autoreset=False)
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
