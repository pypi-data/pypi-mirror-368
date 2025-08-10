from ._make_stats import _make_stats

def upper_bound(lista, alvo, stats=False):
    s = _make_stats()
    esquerda, direita = 0, len(lista)
    while esquerda < direita:
        meio = (esquerda + direita) // 2
        s["comparisons"] += 1
        if lista[meio] <= alvo:
            esquerda = meio + 1
        else:
            direita = meio
    if stats:
        return esquerda, s
    return esquerda
