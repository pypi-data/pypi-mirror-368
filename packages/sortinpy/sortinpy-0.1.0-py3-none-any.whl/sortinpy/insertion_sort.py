from ._make_stats import _make_stats

def insertion_sort(lista, stats=False):
    s = _make_stats()
    arr = lista.copy()
    for i in range(1, len(arr)):
        chave = arr[i]
        s["assignments"] += 1
        j = i - 1
        while j >= 0:
            s["comparisons"] += 1
            if arr[j] > chave:
                arr[j + 1] = arr[j]
                s["assignments"] += 1
                j -= 1
            else:
                break
        arr[j + 1] = chave
        s["assignments"] += 1
    if stats:
        return arr, s
    return arr
