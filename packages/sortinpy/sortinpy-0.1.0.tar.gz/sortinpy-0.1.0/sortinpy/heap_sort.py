from ._make_stats import _make_stats

def heap_sort(lista, stats=False):
    s = _make_stats()
    arr = lista.copy()
    n = len(arr)
    def heapify(a, heap_size, i):
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        if left < heap_size:
            s["comparisons"] += 1
            if a[left] > a[largest]:
                largest = left
        if right < heap_size:
            s["comparisons"] += 1
            if a[right] > a[largest]:
                largest = right
        if largest != i:
            a[i], a[largest] = a[largest], a[i]
            s["swaps"] += 1
            heapify(a, heap_size, largest)
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        s["swaps"] += 1
        heapify(arr, i, 0)
    if stats:
        return arr, s
    return arr
