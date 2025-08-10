from ._make_stats import _make_stats

def merge_sort(lista, stats=False):
    s = _make_stats()
    def _merge(left, right):
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            s["comparisons"] += 1
            if left[i] <= right[j]:
                result.append(left[i])
                s["assignments"] += 1
                i += 1
            else:
                result.append(right[j])
                s["assignments"] += 1
                j += 1
        while i < len(left):
            result.append(left[i])
            s["assignments"] += 1
            i += 1
        while j < len(right):
            result.append(right[j])
            s["assignments"] += 1
            j += 1
        return result
    def _merge_sort(arr):
        if len(arr) <= 1:
            return arr.copy()
        mid = len(arr) // 2
        left = _merge_sort(arr[:mid])
        right = _merge_sort(arr[mid:])
        return _merge(left, right)
    sorted_list = _merge_sort(lista)
    if stats:
        return sorted_list, s
    return sorted_list
