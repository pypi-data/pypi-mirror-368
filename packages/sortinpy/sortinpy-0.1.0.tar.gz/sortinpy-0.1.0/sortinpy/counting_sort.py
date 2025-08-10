from ._make_stats import _make_stats

def counting_sort(lista, stats=False):
    s = _make_stats()
    if not lista:
        if stats:
            return [], s
        return []
    if any((not isinstance(x, int) or x < 0) for x in lista):
        raise ValueError("counting_sort requer inteiros não negativos.")
    max_val = max(lista)
    count = [0] * (max_val + 1)
    for num in lista:
        count[num] += 1
        s["assignments"] += 1
    sorted_list = []
    for i, c in enumerate(count):
        if c:
            s["assignments"] += c
            sorted_list.extend([i] * c)
    if stats:
        return sorted_list, s
    return sorted_list
