from ._make_stats import _make_stats

def bubble_sort(lista, stats=False):
    s = _make_stats()
    arr = lista.copy()
    n = len(arr)
    for i in range(n):
        trocou = False
        for j in range(0, n - i - 1):
            s["comparisons"] += 1
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                s["swaps"] += 1
                trocou = True
        if not trocou:
            break
    if stats:
        return arr, s
    return arr
