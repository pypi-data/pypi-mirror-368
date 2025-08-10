from ._make_stats import _make_stats

def shell_sort(lista, stats=False):
    s = _make_stats()
    arr = lista.copy()
    n = len(arr)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = arr[i]
            s["assignments"] += 1
            j = i
            while j >= gap:
                s["comparisons"] += 1
                if arr[j - gap] > temp:
                    arr[j] = arr[j - gap]
                    s["assignments"] += 1
                    j -= gap
                else:
                    break
            arr[j] = temp
            s["assignments"] += 1
        gap //= 2
    if stats:
        return arr, s
    return arr
