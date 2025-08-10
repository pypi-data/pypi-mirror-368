from ._make_stats import _make_stats

import random
def bogo_sort(lista, stats=False, max_attempts=100000):
    s = _make_stats()
    def esta_ordenada(arr):
        s["comparisons"] += max(0, len(arr) - 1)
        return all(arr[i] <= arr[i + 1] for i in range(len(arr) - 1))
    arr = lista.copy()
    tentativas = 0
    while not esta_ordenada(arr):
        if tentativas >= max_attempts:
            if stats:
                return arr, s
            return arr
        random.shuffle(arr)
        s["assignments"] += len(arr)
        tentativas += 1
    if stats:
        s["assignments"] += tentativas
        return arr, s
    return arr
