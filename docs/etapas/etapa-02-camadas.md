# Etapa 2 — Remodelar em camadas

**Objetivo:** deixar cada arquivo com uma responsabilidade só e corrigir a inconsistência do Chrome.
**Resultado:** `main.py` com ~35 linhas, tela em `faxineira/menu.py`, textos em `faxineira/textos.py`; programa se comporta igual.

## Antes e depois

| Antes | Depois |
|---|---|
| `main.py` (263 linhas): textos + telas + loop + checagem de Windows | `main.py`: só a porta de entrada e a checagem de Windows |
| — | `faxineira/textos.py`: `BANNER`, `REGRAS_SEGURANCA`, `MENU` (só texto) |
| — | `faxineira/menu.py`: funções `rodar_*`, `ACOES` e o loop `executar()` |

## Passo a passo (o que foi feito e como)

### 1. `textos.py`
Moveu as três constantes grandes de texto. Não tem lógica, então não precisa de teste e quem for mudar uma frase não corre risco de quebrar o programa.

### 2. `menu.py`
Recebeu as funções `rodar_*`, o dicionário `ACOES` e o loop principal, que agora se chama `executar()`. A inicialização do `colorama` foi para dentro de `executar()`: antes rodava no momento do `import`, o que atrapalha testes (importar um módulo não deveria mudar o terminal).

### 3. `main.py` fino
```python
def main():
    if os.name != "nt": ...   # só Windows
    from faxineira.menu import executar
    executar()
```
O `import` fica dentro da função de propósito: o pacote `faxineira` importa `winreg`, que só existe no Windows. Em outro sistema o programa avisa "foi feito para Windows" em vez de quebrar com `ModuleNotFoundError`.

### 4. Correção: Chrome × Temp
Na v1, `rodar_limpeza_temp` tratava lista vazia e as falhas, mas `rodar_limpeza_chrome` não: com o cache vazio perguntava mesmo assim, e ignorava quantos itens não foram movidos. As duas agora usam `_limpar_em_lote_com_confirmacao()`:

1. mostra quantos itens achou;
2. se não achou nada, para;
3. pergunta (`confirmar`);
4. manda para a Lixeira e conta sucessos e falhas (`mostrar_resultado_movimento`).

**Por quê:** duas cópias do mesmo fluxo de segurança acabam diferentes (foi o que aconteceu). Um lugar só = uma regra só.

## Verificação
| Checagem | Resultado |
|---|---|
| `pytest` | 10 passaram |
| Programa real, entradas `1`, `x`, `0` | mostra o disco, avisa "Opcao invalida" e encerra |
