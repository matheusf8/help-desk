"""
diagnostico.py - funcoes de DIAGNOSTICO.

Regra deste arquivo inteiro: so LEEM informacao do computador.
Nenhuma funcao aqui apaga, move ou altera nada. Por isso as opcoes 1 a 5
do menu sao sempre seguras de usar, sem pedir confirmacao.
"""
import os
import shutil
import winreg
from pathlib import Path

from faxineira.utils import formatar_bytes, calcular_percentual


def espaco_disco(unidade: str = "C:\\") -> dict:
    """
    Pergunta pro Windows: quanto espaco tem no total, quanto ja foi
    usado e quanto ainda esta livre nesse disco.
    shutil.disk_usage ja vem pronto na biblioteca padrao do Python.
    """
    total, usado, livre = shutil.disk_usage(unidade)
    return {
        "total": total,
        "usado": usado,
        "livre": livre,
        "percentual_usado": calcular_percentual(usado, total),
    }


def tamanho_pasta(caminho: Path) -> int:
    """
    Soma o tamanho de TODOS os arquivos dentro de uma pasta, incluindo
    os que estao dentro de subpastas (por isso "recursivamente").

    rglob("*") e um jeito do Python de dizer "me da todo mundo que tem
    aqui dentro, nao importa quantas pastas de profundidade".
    """
    total = 0
    try:
        for item in caminho.rglob("*"):
            try:
                if item.is_file():
                    total += item.stat().st_size
            except (PermissionError, OSError):
                # Alguns arquivos do Windows sao protegidos e nao
                # deixam nem ver o tamanho. Nesses casos, so pula e
                # continua somando o resto - nao trava o programa.
                continue
    except (PermissionError, OSError):
        pass
    return total


def maiores_pastas(caminho_base: Path, limite: int = 10) -> list[tuple[str, int]]:
    """
    Olha dentro de uma pasta, calcula o tamanho de cada subpasta e
    devolve uma lista ordenada da maior pra menor.
    Exemplo de retorno: [("Steam", 40000000000), ("Discord", 500000000)]
    """
    if not caminho_base.exists():
        return []

    resultados = []
    for item in caminho_base.iterdir():
        if item.is_dir():
            resultados.append((item.name, tamanho_pasta(item)))

    # key=lambda par: par[1]  ->  ordena pelo segundo valor da tupla
    # (o tamanho), nao pelo nome. reverse=True = do maior pro menor.
    resultados.sort(key=lambda par: par[1], reverse=True)
    return resultados[:limite]


def maiores_pastas_programas(limite: int = 10) -> list[tuple[str, int]]:
    """
    Junta as pastas de 3 lugares onde programa instalado costuma morar
    (Program Files, Program Files (x86) e ProgramData) e devolve as
    maiores de todas juntas.
    """
    bases = [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")),
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")),
        Path(os.environ.get("ProgramData", r"C:\ProgramData")),
    ]
    todas = []
    for base in bases:
        todas.extend(maiores_pastas(base, limite=limite))

    todas.sort(key=lambda par: par[1], reverse=True)
    return todas[:limite]


def maiores_pastas_usuario(limite: int = 10) -> list[tuple[str, int]]:
    """Maiores pastas pessoais: Downloads, Documentos, Videos, etc."""
    pasta_usuario = Path.home()  # a pasta do usuario, tipo C:\Users\Matheus
    candidatas = ["Downloads", "Documents", "Desktop", "Videos", "Pictures", "OneDrive"]

    resultados = []
    for nome in candidatas:
        caminho = pasta_usuario / nome
        if caminho.exists():
            resultados.append((nome, tamanho_pasta(caminho)))

    resultados.sort(key=lambda par: par[1], reverse=True)
    return resultados[:limite]


def itens_inicializacao() -> list[str]:
    """
    Le a lista de programas que o Windows abre sozinho quando liga.
    Essa lista fica guardada no REGISTRO do Windows, numa chave chamada
    "Run" - e so uma gaveta de configuracao do sistema operacional.

    Importante: aqui a gente so LE (winreg.EnumValue). Em nenhum
    momento o codigo apaga ou muda essa chave.
    """
    chaves = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
    ]
    itens = []
    for raiz, caminho in chaves:
        try:
            with winreg.OpenKey(raiz, caminho) as chave:
                indice = 0
                while True:
                    try:
                        # EnumValue(chave, 0) pega o primeiro item, (chave, 1)
                        # o segundo, e assim por diante, ate nao ter mais
                        # (o que gera um erro OSError que a gente usa pra
                        # saber que a lista acabou).
                        nome, valor, _ = winreg.EnumValue(chave, indice)
                        itens.append(f"{nome}  ->  {valor}")
                        indice += 1
                    except OSError:
                        break
        except FileNotFoundError:
            continue
    return itens


def formatar_relatorio_espaco(dados: dict) -> str:
    """Pega o resultado de espaco_disco() e transforma em texto bonito pra tela."""
    return (
        f"Total:  {formatar_bytes(dados['total'])}\n"
        f"Usado:  {formatar_bytes(dados['usado'])} ({dados['percentual_usado']}%)\n"
        f"Livre:  {formatar_bytes(dados['livre'])}"
    )
