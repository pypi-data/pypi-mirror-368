from . import _make_stats

def linear_search(lista, alvo, stats=False):
    s = _make_stats()
    for i, elemento in enumerate(lista):
        s["comparisons"] += 1
        if elemento == alvo:
            if stats:
                return i, s
            return i
    if stats:
        return -1, s
    return -1
