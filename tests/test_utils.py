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
