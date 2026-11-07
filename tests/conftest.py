"""
conftest.py - preparacao que vale para TODOS os testes.

Regra do projeto: nenhum teste pode apagar, mover ou esvaziar nada de
verdade. Esta fixture e a rede de seguranca: se algum teste esquecer de
trocar a funcao perigosa por uma falsa, ele FALHA com uma mensagem clara
em vez de mexer na Lixeira do computador de quem roda os testes.
"""
import pytest


@pytest.fixture(autouse=True)
def bloquear_acoes_destrutivas(monkeypatch):
    def proibido(*args, **kwargs):
        raise AssertionError("Teste tentou mexer no disco de verdade (Lixeira). Use monkeypatch.")

    monkeypatch.setattr("faxineira.limpeza.send2trash", proibido)
    monkeypatch.setattr("faxineira.limpeza.esvaziar_lixeira", proibido)
