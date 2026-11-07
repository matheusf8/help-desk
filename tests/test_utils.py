from faxineira.utils import formatar_bytes, calcular_percentual


def test_formatar_bytes_pequeno():
    assert formatar_bytes(500) == "500 B"


def test_formatar_bytes_kb():
    assert formatar_bytes(1536) == "1.5 KB"


def test_formatar_bytes_gb():
    assert formatar_bytes(5 * 1024**3) == "5.0 GB"


def test_formatar_bytes_negativo_da_erro():
    try:
        formatar_bytes(-1)
        assert False, "deveria ter levantado ValueError"
    except ValueError:
        pass


def test_calcular_percentual_normal():
    assert calcular_percentual(50, 200) == 25.0


def test_calcular_percentual_total_zero():
    assert calcular_percentual(10, 0) == 0.0


# --- confirmar e linha (interativas: o input() e trocado por respostas combinadas) ---

import pytest

from faxineira.utils import confirmar, linha


@pytest.mark.parametrize("resposta, esperado", [("s", True), ("SIM", True), ("n", False), ("nao", False), ("não", False)])
def test_confirmar_aceita_sim_e_nao(monkeypatch, resposta, esperado):
    monkeypatch.setattr("builtins.input", lambda *args: resposta)

    assert confirmar("Apagar?") is esperado


def test_confirmar_pergunta_de_novo_se_a_resposta_for_estranha(monkeypatch):
    respostas = iter(["talvez", "", "s"])
    monkeypatch.setattr("builtins.input", lambda *args: next(respostas))

    assert confirmar("Apagar?") is True


def test_linha_tem_o_tamanho_pedido():
    assert linha("-", 10) == "-" * 10
