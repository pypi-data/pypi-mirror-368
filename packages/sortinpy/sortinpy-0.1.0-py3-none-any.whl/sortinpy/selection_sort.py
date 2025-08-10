from ._make_stats import _make_stats

def selection_sort(lista, stats=False):
    s = _make_stats()
    arr = lista.copy()
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            s["comparisons"] += 1
            if arr[j] < arr[min_idx]:
                min_idx = j
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            s["swaps"] += 1
    if stats:
        return arr, s
    return arr
