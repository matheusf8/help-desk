"""
HELP DESK - FAXINEIRA DE PC
Programa de suporte tecnico para limpar e diagnosticar um Windows 11.

Este arquivo e so a PORTA DE ENTRADA: confere se e Windows e chama o menu.
Como o codigo esta organizado (a "arquitetura"):
  main.py                  -> porta de entrada
  faxineira/menu.py        -> TELA e MENU (o que aparece pro usuario)
  faxineira/textos.py      -> banner, menu e regras (so texto)
  faxineira/diagnostico.py -> funcoes que so LEEM informacao (nunca apagam nada)
  faxineira/limpeza.py     -> funcoes que mexem em arquivo (sempre via Lixeira)
  faxineira/utils.py       -> ferramentas pequenas usadas pelos outros

Cada arquivo cuida de UMA responsabilidade so. Mais detalhes em docs/arquitetura.md.

Regra de seguranca numero 1 (sempre): nada e apagado direto.
Tudo vai primeiro pra Lixeira, e o usuario confirma antes de qualquer limpeza.
"""
import os
import sys


def main() -> None:
    # Este programa usa winreg e a Lixeira do Windows, que nao existem
    # no Mac/Linux. Por isso so segue se for Windows. O import do menu
    # fica depois da checagem porque o pacote faxineira importa winreg:
    # em outro sistema ele quebraria antes de mostrar esta mensagem.
    if os.name != "nt":
        print("Este programa foi feito para Windows 11.")
        sys.exit(1)

    from faxineira.menu import executar
    executar()


if __name__ == "__main__":
    main()
