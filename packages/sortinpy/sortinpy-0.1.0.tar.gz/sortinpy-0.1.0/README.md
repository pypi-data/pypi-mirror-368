````
# sortinpy

Python library providing a collection of classic sorting and searching algorithms implemented from scratch. Designed for educational purposes and practical use in Python projects.

## Installation

To install the package locally for development or usage, navigate to the project root folder (where `setup.py` is located) and run:

```bash
pip install -e .
````

This installs the library in editable mode, so any changes you make to the source code will reflect immediately.

## Usage

Import the specific sorting or searching function you need from `sortinpy` and use it on your lists.

Example with sorting algorithms:

```python
import sortinpy

lst = [5, 3, 2, 8, 1]

# Simple use returning just the sorted list
sorted_list = sortinpy.bubble_sort(lst)
print("Bubble Sort:", sorted_list)

# Using a function with optional statistics output
sorted_list, stats = sortinpy.shell_sort(lst, stats=True)
print("Shell Sort:", sorted_list)
print("Operation counts:", stats)
```

## Available Algorithms

### Sorting Algorithms

* **Bubble Sort** — simple, inefficient, good for learning
* **Insertion Sort** — simple, efficient on nearly sorted data
* **Selection Sort** — simple, always O(n²)
* **Merge Sort** — efficient, stable divide and conquer
* **Quick Sort** — efficient average case, recursive
* **Heap Sort** — efficient, in-place, uses heap data structure
* **Counting Sort** — efficient for integers in small range
* **Radix Sort** — non-comparative sort for integers
* **Shell Sort** — optimized insertion sort with gap sequence
* **Bogo Sort** — educational, randomized and very inefficient
* **Introsort** — hybrid of quicksort and heapsort for efficiency

### Searching Algorithms

* **Binary Search** — fast search on sorted lists
* **Linear Search** — simple search for any list
* **Lower Bound** — finds insertion position (left)
* **Upper Bound** — finds insertion position (right)

## Optional Statistics

Most sorting functions accept an optional boolean parameter (`stats=True`) that makes them return a tuple: the sorted list plus a dictionary containing counts of:

* Comparisons
* Swaps
* Assignments

This allows analyzing algorithm performance on given inputs.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for full details.

---

Created by wandsondev

```
```

