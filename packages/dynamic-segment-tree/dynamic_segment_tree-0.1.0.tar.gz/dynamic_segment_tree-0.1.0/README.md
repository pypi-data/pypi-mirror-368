# Dynamic Segment Tree

A high-performance dynamic segment tree implemented in C++ with Python bindings using pybind11.  
Supports efficient range queries and updates on large arrays without reserving memory upfront.

## About Dynamic Segment Tree

This package implements a **dynamic segment tree** data structure for efficient use in Python programs.

### What is a dynamic segment tree?

- A **segment tree** is a powerful data structure used to perform **range queries and updates** efficiently on an array.
- The **dynamic** variant does **not pre-allocate memory for the entire array size**, but instead **creates nodes only when needed**, saving memory.
- This makes it practical for very large arrays (e.g., length 10 million or more) where many elements are initially zero or default.

### What problem does this solve?

- Suppose you have **M categories** and an array of length N.
- At each position, exactly one category is assigned.
- You want to:
  - **Update** the category at any index dynamically.
  - **Query** how many elements of a given category exist in any range `[L, R]`.
- This package supports exactly that efficiently, using minimal memory.

## Main Functions

### `DynamicSegTree(N)`

- Creates a dynamic segment tree for an array of size `N`.
- Initially, all positions are empty (or a default invalid category).

### `build(arr)`

- Builds the tree from a given list/array `arr` of categories.
- This initializes the data structure with known values.

### `set(pos, category)`

- Updates the element at position `pos` to belong to `category`.
- If the position already had a category, it updates it accordingly.

### `get(pos)`

- Returns the current category at position `pos`.
- Returns `-1` if the position is unset or empty.

### `query(l, r, category)`

- Returns the **count** of elements belonging to `category` in the range `[l, r]`.
- This is the main query function and works efficiently even for large `N`.

## Why Use This Package?

- Designed for very large arrays where a classical segment tree would be memory-heavy.
- Provides a Python interface for easy integration into your projects.
- Efficiently supports queries and updates with **logarithmic time complexity**.
- Ideal for problems involving category counts over large ranges with sparse updates.

## Installation

```bash
pip install dynamic-segment-tree
