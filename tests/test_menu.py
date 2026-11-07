"""
Testes de menu.py - o fluxo de CONFIRMACAO antes de qualquer limpeza.

O que importa aqui nao e o texto bonito da tela, e a regra: sem um "sim"
do usuario, nada vai pra Lixeira. Por isso trocamos as funcoes de
limpeza.py por falsas que anotam se foram chamadas, e o confirmar() por
uma resposta combinada.
"""
from pathlib import Path

import pytest

from faxineira import limpeza, menu


@pytest.fixture
def espiao(monkeypatch):
    """Anota cada chamada a mandar_para_lixeira e a esvaziar_lixeira."""
    chamadas = {"lixeira": [], "esvaziou": 0}

    def mandar(itens):
        chamadas["lixeira"].append(list(itens))
        return list(itens), []

    def esvaziar():
        chamadas["esvaziou"] += 1

    monkeypatch.setattr(limpeza, "mandar_para_lixeira", mandar)
    monkeypatch.setattr(limpeza, "esvaziar_lixeira", esvaziar)
    return chamadas


def responder(monkeypatch, *respostas):
    """Faz o confirmar() do menu devolver as respostas combinadas, na ordem."""
    fila = list(respostas)
    perguntas = []

    def falso_confirmar(pergunta):
        perguntas.append(pergunta)
        return fila.pop(0)

    monkeypatch.setattr(menu, "confirmar", falso_confirmar)
    return perguntas


# --- Temp --------------------------------------------------------------

def test_temp_sem_confirmacao_nao_move_nada(monkeypatch, espiao, capsys):
    monkeypatch.setattr(limpeza, "itens_temp", lambda: [Path("a.tmp")])
    responder(monkeypatch, False)

    menu.rodar_limpeza_temp()

    assert espiao["lixeira"] == []
    assert "Cancelado" in capsys.readouterr().out


def test_temp_confirmado_manda_para_lixeira(monkeypatch, espiao, capsys):
    itens = [Path("a.tmp"), Path("b.tmp")]
    monkeypatch.setattr(limpeza, "itens_temp", lambda: itens)
    responder(monkeypatch, True)

    menu.rodar_limpeza_temp()

    assert espiao["lixeira"] == [itens]
    assert "2 item(ns) mandado(s)" in capsys.readouterr().out


def test_temp_vazio_nem_pergunta(monkeypatch, espiao):
    monkeypatch.setattr(limpeza, "itens_temp", lambda: [])
    perguntas = responder(monkeypatch)

    menu.rodar_limpeza_temp()

    assert perguntas == []
    assert espiao["lixeira"] == []


# --- Chrome (era o bug da v1: nao tratava lista vazia) -----------------

def test_chrome_nao_instalado(monkeypatch, espiao, capsys):
    monkeypatch.setattr(limpeza, "pasta_cache_chrome", lambda: None)

    menu.rodar_limpeza_chrome()

    assert "nao encontrado" in capsys.readouterr().out
    assert espiao["lixeira"] == []


def test_chrome_cache_vazio_nem_pergunta(monkeypatch, espiao):
    monkeypatch.setattr(limpeza, "pasta_cache_chrome", lambda: Path("cache"))
    monkeypatch.setattr(limpeza, "listar_itens_de", lambda pasta: [])
    perguntas = responder(monkeypatch)

    menu.rodar_limpeza_chrome()

    assert perguntas == []


def test_chrome_conta_as_falhas(monkeypatch, capsys):
    monkeypatch.setattr(limpeza, "pasta_cache_chrome", lambda: Path("cache"))
    monkeypatch.setattr(limpeza, "listar_itens_de", lambda pasta: [Path("ok"), Path("em-uso")])
    monkeypatch.setattr(limpeza, "mandar_para_lixeira", lambda itens: ([itens[0]], [itens[1]]))
    responder(monkeypatch, True)

    menu.rodar_limpeza_chrome()

    saida = capsys.readouterr().out
    assert "1 item(ns) mandado(s)" in saida
    assert "1 item(ns) nao puderam ser movidos" in saida


# --- AppData: uma pasta de cada vez ------------------------------------

def test_appdata_confirma_pasta_por_pasta(monkeypatch, espiao):
    a, b = Path("AppData/Roaming/resto-a"), Path("AppData/Roaming/resto-b")
    monkeypatch.setattr(limpeza, "pastas_appdata_suspeitas", lambda: [a, b])
    perguntas = responder(monkeypatch, True, False)  # sim pra A, nao pra B

    menu.rodar_restos_appdata()

    assert len(perguntas) == 2  # perguntou uma vez por pasta
    assert espiao["lixeira"] == [[a]]  # so a A foi, e sozinha


def test_appdata_sem_suspeitas(monkeypatch, espiao, capsys):
    monkeypatch.setattr(limpeza, "pastas_appdata_suspeitas", lambda: [])

    menu.rodar_restos_appdata()

    assert "Nenhuma pasta suspeita" in capsys.readouterr().out


# --- Esvaziar a Lixeira (a unica acao sem volta) -----------------------

def test_esvaziar_lixeira_sem_confirmacao_nao_esvazia(monkeypatch, espiao):
    responder(monkeypatch, False)

    menu.rodar_esvaziar_lixeira()

    assert espiao["esvaziou"] == 0


def test_esvaziar_lixeira_confirmado_esvazia(monkeypatch, espiao):
    responder(monkeypatch, True)

    menu.rodar_esvaziar_lixeira()

    assert espiao["esvaziou"] == 1


# --- Menu principal ----------------------------------------------------

def test_todas_as_opcoes_de_1_a_9_tem_acao():
    assert sorted(menu.ACOES) == [str(n) for n in range(1, 10)]


def test_loop_avisa_opcao_invalida_e_sai_no_zero(monkeypatch, capsys):
    monkeypatch.setattr(menu, "pintar_tela", lambda: None)
    monkeypatch.setattr(menu, "imprimir_robo", lambda *args, **kwargs: None)
    digitado = iter(["x", "0"])
    monkeypatch.setattr("builtins.input", lambda *args: next(digitado))

    menu.executar()

    assert "Opcao invalida" in capsys.readouterr().out
