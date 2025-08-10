from . import _make_stats

def binary_search(lista, alvo, stats=False):
    s = _make_stats()
    esquerda, direita = 0, len(lista) - 1
    while esquerda <= direita:
        meio = (esquerda + direita) // 2
        s["comparisons"] += 1
        if lista[meio] == alvo:
            if stats:
                return meio, s
            return meio
        elif lista[meio] < alvo:
            esquerda = meio + 1
        else:
            direita = meio - 1
    if stats:
        return -1, s
    return -1
