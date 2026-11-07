"""
textos.py - todo texto grande que aparece na tela.

Fica separado do menu.py de proposito: se um dia precisar mudar uma frase
ou o desenho do banner, so este arquivo muda. Aqui nao tem logica nenhuma,
so texto.
"""

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
