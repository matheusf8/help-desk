from pathlib import Path

from faxineira.diagnostico import tamanho_pasta, maiores_pastas


def test_tamanho_pasta_soma_arquivos(tmp_path: Path):
    (tmp_path / "a.txt").write_text("1234567890")  # 10 bytes
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "b.txt").write_text("12345")  # 5 bytes

    assert tamanho_pasta(tmp_path) == 15


def test_tamanho_pasta_vazia(tmp_path: Path):
    assert tamanho_pasta(tmp_path) == 0


def test_maiores_pastas_ordena_do_maior_pro_menor(tmp_path: Path):
    grande = tmp_path / "grande"
    pequena = tmp_path / "pequena"
    grande.mkdir()
    pequena.mkdir()
    (grande / "arquivo.bin").write_bytes(b"0" * 100)
    (pequena / "arquivo.bin").write_bytes(b"0" * 10)

    resultado = maiores_pastas(tmp_path)

    assert resultado[0][0] == "grande"
    assert resultado[1][0] == "pequena"


def test_maiores_pastas_caminho_inexistente():
    assert maiores_pastas(Path("C:/isso/nao/existe/de/verdade")) == []
