from ._make_stats import _make_stats

import math
def introsort(lista, stats=False):
    s = _make_stats()
    arr = lista.copy()
    def insertion_sort_sub(arr, start, end):
        for i in range(start + 1, end + 1):
            chave = arr[i]
            s["assignments"] += 1
            j = i - 1
            while j >= start:
                s["comparisons"] += 1
                if arr[j] > chave:
                    arr[j + 1] = arr[j]
                    s["assignments"] += 1
                    j -= 1
                else:
                    break
            arr[j + 1] = chave
            s["assignments"] += 1
    def heapify_sub(arr, heap_size, root, offset):
        largest = root
        left = 2 * root + 1
        right = 2 * root + 2
        if left < heap_size:
            s["comparisons"] += 1
            if arr[offset + left] > arr[offset + largest]:
                largest = left
        if right < heap_size:
            s["comparisons"] += 1
            if arr[offset + right] > arr[offset + largest]:
                largest = right
        if largest != root:
            arr[offset + root], arr[offset + largest] = arr[offset + largest], arr[offset + root]
            s["swaps"] += 1
            heapify_sub(arr, heap_size, largest, offset)
    def heapsort_sub(arr, start, end):
        size = end - start + 1
        for i in range(size // 2 - 1, -1, -1):
            heapify_sub(arr, size, i, start)
        for i in range(size - 1, 0, -1):
            arr[start], arr[start + i] = arr[start + i], arr[start]
            s["swaps"] += 1
            heapify_sub(arr, i, 0, start)
    def partition(arr, low, high):
        pivot = arr[high]
        i = low - 1
        for j in range(low, high):
            s["comparisons"] += 1
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
                s["swaps"] += 1
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        s["swaps"] += 1
        return i + 1
    def introsort_util(arr, start, end, max_depth):
        size = end - start + 1
        if size <= 16:
            insertion_sort_sub(arr, start, end)
            return
        if max_depth == 0:
            heapsort_sub(arr, start, end)
            return
        pivot_index = partition(arr, start, end)
        introsort_util(arr, start, pivot_index - 1, max_depth - 1)
        introsort_util(arr, pivot_index + 1, end, max_depth - 1)
    max_depth = 2 * math.floor(math.log2(len(arr))) if len(arr) > 0 else 0
    introsort_util(arr, 0, len(arr) - 1, max_depth)
    if stats:
        return arr, s
    return arr
