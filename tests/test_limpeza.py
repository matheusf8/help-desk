"""
Testes de limpeza.py - o arquivo que mexe em arquivo de verdade.

Como testar sem apagar nada de verdade:
  - pastas de mentira com tmp_path (o pytest cria e apaga sozinho);
  - variaveis de ambiente (TEMP, APPDATA...) apontando pra essas pastas;
  - send2trash trocado por uma funcao falsa que so anota o que recebeu.
"""
import ctypes
from pathlib import Path
from types import SimpleNamespace

import pytest

from faxineira import limpeza

# A fixture autouse do conftest troca limpeza.esvaziar_lixeira por uma
# funcao que falha. Guardamos aqui a de verdade (importada antes das
# fixtures rodarem) pra testar ela com um Windows falso.
from faxineira.limpeza import esvaziar_lixeira as esvaziar_lixeira_real


@pytest.fixture
def lixeira_falsa(monkeypatch):
    """Troca o send2trash por um que so anota os caminhos recebidos."""
    recebidos = []
    monkeypatch.setattr(limpeza, "send2trash", lambda caminho: recebidos.append(caminho))
    return recebidos


# --- listar_itens_de ---------------------------------------------------

def test_listar_itens_de_devolve_so_o_primeiro_nivel(tmp_path: Path):
    (tmp_path / "a.txt").write_text("x")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "dentro.txt").write_text("y")

    nomes = sorted(item.name for item in limpeza.listar_itens_de(tmp_path))

    assert nomes == ["a.txt", "sub"]


def test_listar_itens_de_pasta_inexistente(tmp_path: Path):
    assert limpeza.listar_itens_de(tmp_path / "nao-existe") == []


def test_listar_itens_de_um_arquivo_em_vez_de_pasta(tmp_path: Path):
    arquivo = tmp_path / "solto.txt"
    arquivo.write_text("x")

    assert limpeza.listar_itens_de(arquivo) == []


# --- eh_protegido ------------------------------------------------------

@pytest.mark.parametrize("nome", ["Microsoft", "Windows Defender", "WebView2Runtime", "AMD", "NVIDIA", "msedge.exe"])
def test_eh_protegido_nomes_delicados(nome):
    assert limpeza.eh_protegido(Path("C:/qualquer/lugar") / nome)


@pytest.mark.parametrize("nome", ["Discord", "Samdle", "resto-de-jogo", "abc123.tmp"])
def test_eh_protegido_nomes_comuns_passam(nome):
    assert not limpeza.eh_protegido(Path("C:/qualquer/lugar") / nome)


def test_eh_protegido_ignora_as_pastas_de_cima():
    # Dentro da pasta Windows\Temp, o arquivo comum NAO e protegido so
    # por causa do nome da pasta onde ele esta.
    assert not limpeza.eh_protegido(Path("C:/Windows/Temp/abc.tmp"))


# --- mandar_para_lixeira -----------------------------------------------

def test_mandar_para_lixeira_manda_cada_item(lixeira_falsa, tmp_path: Path):
    itens = [tmp_path / "a", tmp_path / "b"]

    sucesso, falhas = limpeza.mandar_para_lixeira(itens)

    assert sucesso == itens
    assert falhas == []
    assert lixeira_falsa == [str(tmp_path / "a"), str(tmp_path / "b")]


def test_mandar_para_lixeira_item_em_uso_vai_para_falhas(monkeypatch, tmp_path: Path):
    def so_o_segundo_falha(caminho):
        if caminho.endswith("em-uso"):
            raise PermissionError("arquivo em uso")

    monkeypatch.setattr(limpeza, "send2trash", so_o_segundo_falha)
    livre, em_uso = tmp_path / "livre", tmp_path / "em-uso"

    sucesso, falhas = limpeza.mandar_para_lixeira([livre, em_uso])

    assert sucesso == [livre]
    assert falhas == [em_uso]


def test_mandar_para_lixeira_nao_tenta_item_protegido(lixeira_falsa, tmp_path: Path):
    protegido = tmp_path / "Microsoft"

    sucesso, falhas = limpeza.mandar_para_lixeira([protegido])

    assert sucesso == []
    assert falhas == [protegido]
    assert lixeira_falsa == []  # o send2trash nem foi chamado


def test_mandar_para_lixeira_lista_vazia():
    assert limpeza.mandar_para_lixeira([]) == ([], [])


# --- pastas_temp / itens_temp ------------------------------------------

def test_itens_temp_junta_temp_do_usuario_e_do_windows(monkeypatch, tmp_path: Path):
    temp_usuario = tmp_path / "temp_usuario"
    windir = tmp_path / "windir"
    (windir / "Temp").mkdir(parents=True)
    temp_usuario.mkdir()
    (temp_usuario / "u.tmp").write_text("x")
    (windir / "Temp" / "w.tmp").write_text("x")
    monkeypatch.setenv("TEMP", str(temp_usuario))
    monkeypatch.setenv("windir", str(windir))

    nomes = sorted(item.name for item in limpeza.itens_temp())

    assert nomes == ["u.tmp", "w.tmp"]


def test_pastas_temp_ignora_pasta_que_nao_existe(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("TEMP", str(tmp_path / "nao-existe"))
    monkeypatch.setenv("windir", str(tmp_path / "tambem-nao"))

    assert limpeza.pastas_temp() == []


# --- pasta_cache_chrome ------------------------------------------------

def test_pasta_cache_chrome_encontrada(monkeypatch, tmp_path: Path):
    cache = tmp_path / "Google" / "Chrome" / "User Data" / "Default" / "Cache"
    cache.mkdir(parents=True)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    assert limpeza.pasta_cache_chrome() == cache


def test_pasta_cache_chrome_sem_chrome_instalado(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    assert limpeza.pasta_cache_chrome() is None


# --- pastas_appdata_suspeitas ------------------------------------------

def test_appdata_suspeitas_so_devolve_o_que_nao_combina(monkeypatch, tmp_path: Path):
    roaming = tmp_path / "Roaming"
    local = tmp_path / "Local"
    roaming.mkdir()
    local.mkdir()
    for nome in ["Discord", "ResIduoDeJogo", "Microsoft"]:
        (roaming / nome).mkdir()
    (roaming / "arquivo-solto.txt").write_text("x")  # arquivo nao conta, so pasta
    monkeypatch.setenv("APPDATA", str(roaming))
    monkeypatch.setenv("LOCALAPPDATA", str(local))
    monkeypatch.setattr(limpeza, "programas_instalados", lambda: {"discord", "git"})

    nomes = [pasta.name for pasta in limpeza.pastas_appdata_suspeitas()]

    # Discord combina com um programa instalado; Microsoft e protegida;
    # arquivo solto nao e pasta. Sobra so o resto de jogo.
    assert nomes == ["ResIduoDeJogo"]


def test_appdata_suspeitas_nunca_apaga_nada(monkeypatch, tmp_path: Path):
    roaming = tmp_path / "Roaming"
    roaming.mkdir()
    (roaming / "ResIduoDeJogo").mkdir()
    monkeypatch.setenv("APPDATA", str(roaming))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "Local"))
    monkeypatch.setattr(limpeza, "programas_instalados", lambda: set())

    limpeza.pastas_appdata_suspeitas()

    assert (roaming / "ResIduoDeJogo").exists()  # so listou, a pasta continua la


# --- esvaziar_lixeira --------------------------------------------------

def test_esvaziar_lixeira_chama_o_windows_sem_janelas_nem_som(monkeypatch):
    chamadas = []
    falso_shell = SimpleNamespace(SHEmptyRecycleBinW=lambda *args: chamadas.append(args))
    monkeypatch.setattr(ctypes, "windll", SimpleNamespace(shell32=falso_shell), raising=False)

    esvaziar_lixeira_real()  # a de verdade, mas falando com um "Windows" falso

    assert chamadas == [(None, None, 0x1 | 0x2 | 0x4)]
