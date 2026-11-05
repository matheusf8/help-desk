"""
utils.py - ferramentas pequenas usadas pelo resto do programa.

Por que esse arquivo existe separado dos outros?
Porque aqui so tem funcoes "puras": elas recebem um valor, devolvem um
resultado, e NAO mexem no disco sozinhas. Isso facilita testar com o
Pytest, porque nao precisamos fingir um disco de verdade pra testar elas.
"""
import sys
import time

from colorama import Fore, Style


def formatar_bytes(valor_bytes: int) -> str:
    """
    Transforma um numero de bytes em algo que um humano le facil.
    Exemplo: formatar_bytes(1536) -> "1.5 KB"

    A ideia: bytes sao muito pequenos pra ler ("5000000000 bytes" e
    confuso). Entao a gente vai dividindo por 1024 ate o numero ficar
    pequeno, e troca o nome da unidade (B -> KB -> MB -> GB -> TB).
    """
    if valor_bytes < 0:
        # Espaco em disco nunca e negativo. Se isso acontecer, e porque
        # outro lugar do codigo chamou essa funcao com um valor errado.
        raise ValueError("valor_bytes nao pode ser negativo")

    unidades = ["B", "KB", "MB", "GB", "TB"]
    tamanho = float(valor_bytes)

    for unidade in unidades:
        # Enquanto o numero for grande (>= 1024), divide e passa pra
        # proxima unidade. Quando ficar pequeno (ou chegar no TB, que e
        # a ultima da lista), para e devolve o resultado formatado.
        if tamanho < 1024 or unidade == unidades[-1]:
            if unidade == "B":
                return f"{int(tamanho)} {unidade}"
            return f"{tamanho:.1f} {unidade}"
        tamanho /= 1024

    return f"{tamanho:.1f} TB"


def calcular_percentual(usado: int, total: int) -> float:
    """
    Calcula quantos % de 'total' o valor 'usado' representa.
    Exemplo: calcular_percentual(50, 200) -> 25.0 (ou seja, 25%)
    """
    if total <= 0:
        # Protege contra divisao por zero. Um disco de tamanho 0 nao
        # faz sentido, mas e melhor devolver 0 do que o programa travar.
        return 0.0
    return round((usado / total) * 100, 1)


def imprimir_robo(texto: str, atraso: float = 0.012, cor: str = Fore.GREEN) -> None:
    """
    Imprime o texto letra por letra, com uma pequena pausa entre cada uma.
    E so um efeito visual (estilo "robo digitando"), nao muda o conteudo
    do texto.
    """
    for caractere in texto:
        sys.stdout.write(cor + caractere + Style.RESET_ALL)
        sys.stdout.flush()  # mostra a letra na hora, sem esperar o resto
        time.sleep(atraso)
    print()  # pula uma linha no final, como um print() normal faria


def confirmar(pergunta: str) -> bool:
    """
    Faz uma pergunta de sim ou nao pro usuario e so aceita essas duas
    respostas (pergunta de novo se a pessoa digitar outra coisa).
    Usado antes de QUALQUER limpeza, pra nunca apagar nada sem avisar.
    """
    while True:
        resposta = input(Fore.YELLOW + f"{pergunta} [s/n]: " + Style.RESET_ALL).strip().lower()
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "nao", "não"):
            return False
        print(Fore.RED + "Responde só com 's' ou 'n'." + Style.RESET_ALL)


def linha(caractere: str = "=", tamanho: int = 60) -> str:
    """Desenha uma linha separadora, tipo '------------'. So estetica."""
    return caractere * tamanho
