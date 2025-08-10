from ._make_stats import _make_stats

def quick_sort(lista, stats=False):
    s = _make_stats()
    def _quick(arr):
        if len(arr) <= 1:
            return arr.copy()
        pivot = arr[0]
        less = []
        greater = []
        for x in arr[1:]:
            s["comparisons"] += 1
            if x <= pivot:
                less.append(x)
                s["assignments"] += 1
            else:
                greater.append(x)
                s["assignments"] += 1
        return _quick(less) + [pivot] + _quick(greater)
    sorted_list = _quick(lista)
    if stats:
        return sorted_list, s
    return sorted_list
