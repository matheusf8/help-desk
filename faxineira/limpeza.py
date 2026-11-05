"""
limpeza.py - funcoes de LIMPEZA.

Diferente do diagnostico.py, essas funcoes SIM mexem em arquivo de
verdade. Por isso a regra de seguranca numero 1 do projeto mora aqui:
NUNCA apagar direto. Tudo passa pela funcao mandar_para_lixeira(), que
usa a biblioteca send2trash pra mover pra Lixeira do Windows - exatamente
como se a pessoa tivesse arrastado o arquivo com o mouse.
"""
import os
import winreg
from pathlib import Path

from send2trash import send2trash


def listar_itens_de(caminho: Path) -> list[Path]:
    """
    Mostra o que tem dentro de uma pasta (so o primeiro nivel, sem
    entrar nas subpastas). Repara que essa funcao so OLHA - ela nao
    apaga nada, so devolve a lista pra quem chamou decidir o que fazer.
    """
    if not caminho.exists():
        return []
    try:
        return list(caminho.iterdir())
    except (PermissionError, OSError):
        return []


def mandar_para_lixeira(itens: list[Path]) -> tuple[list[Path], list[Path]]:
    """
    Pega uma lista de arquivos/pastas e manda cada um pra Lixeira.

    Alguns itens podem falhar (por exemplo, um arquivo que o Windows
    esta usando naquele momento nao pode ser movido). Por isso a funcao
    devolve DUAS listas: quem deu certo e quem deu errado, pra gente
    poder avisar o usuario direitinho sem o programa quebrar no meio.
    """
    sucesso, falhas = [], []
    for item in itens:
        try:
            send2trash(str(item))
            sucesso.append(item)
        except (PermissionError, OSError):
            falhas.append(item)
    return sucesso, falhas


def pastas_temp() -> list[Path]:
    """
    Onde o Windows guarda arquivo temporario (coisa que programa cria
    pra uso rapido e deveria apagar sozinho, mas nem sempre apaga).
    Sao dois lugares: a pasta Temp do usuario e a do Windows inteiro.
    """
    caminhos = [
        Path(os.environ.get("TEMP", "")),
        Path(os.environ.get("windir", r"C:\Windows")) / "Temp",
    ]
    return [c for c in caminhos if c and c.exists()]


def itens_temp() -> list[Path]:
    """Lista tudo que tem dentro das pastas de Temp, juntando as duas."""
    itens = []
    for pasta in pastas_temp():
        itens.extend(listar_itens_de(pasta))
    return itens


def pasta_cache_chrome() -> Path | None:
    """
    Caminho onde o Chrome guarda o cache (imagens e paginas que ele
    salva pra carregar mais rapido da proxima vez). Devolve None se o
    Chrome nao estiver instalado nessa maquina.
    """
    caminho = Path(os.environ.get("LOCALAPPDATA", "")) / "Google" / "Chrome" / "User Data" / "Default" / "Cache"
    return caminho if caminho.exists() else None


def programas_instalados() -> set[str]:
    """
    Le a lista de "Aplicativos instalados" do Windows (a mesma que
    aparece em Configuracoes > Aplicativos), direto do registro.

    Isso serve de "lista de comparacao" pra funcao de baixo
    (pastas_appdata_suspeitas) descobrir quais pastas de AppData ainda
    pertencem a um programa que existe, e quais sao resto de programa
    que ja foi desinstalado.
    """
    chaves = [
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]
    nomes = set()
    for raiz, caminho in chaves:
        try:
            with winreg.OpenKey(raiz, caminho) as chave_pai:
                # Cada programa instalado tem sua propria "subchave" aqui
                # dentro. A gente visita uma por uma e pega o nome dela.
                for i in range(winreg.QueryInfoKey(chave_pai)[0]):
                    subchave_nome = winreg.EnumKey(chave_pai, i)
                    try:
                        with winreg.OpenKey(chave_pai, subchave_nome) as subchave:
                            nome, _ = winreg.QueryValueEx(subchave, "DisplayName")
                            nomes.add(nome.lower())
                    except (FileNotFoundError, OSError):
                        # Algumas subchaves nao tem "DisplayName" (sao
                        # atualizacoes do sistema, nao programas de
                        # verdade). Simplesmente ignora e segue.
                        continue
        except FileNotFoundError:
            continue
    return nomes


def pastas_appdata_suspeitas() -> list[Path]:
    """
    Procura pastas dentro de AppData (Roaming e Local) cujo nome NAO
    aparece na lista de programas instalados hoje - ou seja, pastas que
    sobraram de algo que a pessoa ja desinstalou.

    Importante: essa funcao so DEVOLVE A LISTA de suspeitas. Ela nunca
    decide sozinha apagar nada - quem confirma, pasta por pasta, e o
    usuario no menu (olha a funcao rodar_restos_appdata em main.py).
    Isso evita apagar por engano a pasta de um programa que a pessoa
    ainda usa mas que tem um nome diferente no registro.
    """
    instalados = programas_instalados()
    bases = [
        Path(os.environ.get("APPDATA", "")),
        Path(os.environ.get("LOCALAPPDATA", "")),
    ]
    suspeitas = []
    for base in bases:
        if not base.exists():
            continue
        for item in base.iterdir():
            if not item.is_dir():
                continue
            nome = item.name.lower()
            # "combina" vira True se o nome da pasta aparecer dentro do
            # nome de algum programa instalado (ou vice-versa) - uma
            # comparacao simples, de proposito, pra v1.
            combina = any(nome in instalado or instalado in nome for instalado in instalados)
            if not combina:
                suspeitas.append(item)
    return suspeitas


def esvaziar_lixeira() -> None:
    """
    Esvazia a Lixeira do Windows DE VERDADE - depois disso nao da mais
    pra recuperar os arquivos. Por isso essa e a UNICA funcao do
    projeto que o main.py chama sem ter uma segunda chance: o pedido de
    confirmacao acontece antes, no menu.

    SHEmptyRecycleBinW e uma funcao do proprio Windows (nao do Python) -
    a gente so "liga" pra ela usando a biblioteca ctypes.
    """
    import ctypes

    SHERB_NOCONFIRMATION = 0x00000001  # nao mostrar a propria janela de confirmacao do Windows
    SHERB_NOPROGRESSUI = 0x00000002    # nao mostrar barra de progresso
    SHERB_NOSOUND = 0x00000004         # nao tocar o som de "lixeira esvaziada"
    flags = SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND
    ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, flags)
