from ._make_stats import _make_stats

def radix_sort(lista, stats=False):
    s = _make_stats()
    if not lista:
        if stats:
            return [], s
        return []
    if any((not isinstance(x, int) or x < 0) for x in lista):
        raise ValueError("radix_sort requer inteiros não negativos.")
    def counting_sort_exp(arr, exp):
        n = len(arr)
        output = [0] * n
        count = [0] * 10
        for i in range(n):
            index = (arr[i] // exp) % 10
            count[index] += 1
            s["assignments"] += 1
        for i in range(1, 10):
            count[i] += count[i - 1]
            s["assignments"] += 1
        i = n - 1
        while i >= 0:
            index = (arr[i] // exp) % 10
            output[count[index] - 1] = arr[i]
            s["assignments"] += 1
            count[index] -= 1
            i -= 1
        for i in range(n):
            arr[i] = output[i]
            s["assignments"] += 1
    arr = lista.copy()
    max_val = max(arr)
    exp = 1
    while max_val // exp > 0:
        counting_sort_exp(arr, exp)
        exp *= 10
    if stats:
        return arr, s
    return arr
