# tests/test_segment_tree.py
import pytest
import time
import random
from dynamic_segment_tree import DynamicSegTree

def test_basic_set_and_query():
    N = 50
    st = DynamicSegTree(N)

    # initially empty
    assert st.query(0, N-1, 1) == 0
    assert st.get(10) == -1

    # set some positions
    st.set(2, 10)
    st.set(5, 7)
    st.set(7, 10)
    st.set(15, 1000)
    st.set(18, 7)

    assert st.query(0, 10, 10) == 2
    assert st.query(0, 19, 7) == 2
    assert st.query(10, 19, 1000) == 1

    # change a position
    st.set(7, 7)  # was 10 -> now 7
    assert st.query(0, 10, 10) == 1
    assert st.query(0, 10, 7) == 2

    # setting same category is a no-op
    st.set(7, 7)
    assert st.query(0, 10, 7) == 2

def test_build_and_overwrite():
    arr = [0,1,2,0,1,2,3,3,3]
    st = DynamicSegTree(len(arr))
    st.build(arr)
    assert st.query(0, len(arr)-1, 0) == 2
    assert st.query(0, len(arr)-1, 1) == 2
    assert st.query(0, len(arr)-1, 2) == 2
    assert st.query(0, len(arr)-1, 3) == 3

    # overwrite several
    st.set(0, 3)
    st.set(8, 0)
    assert st.query(0, len(arr)-1, 0) == 2  # still 2
    assert st.query(0, len(arr)-1, 3) == 3  # still 3 (but different positions may be changed)

def test_benchmark_dynamic_segment_tree():
    N = 10_000_000
    M = 1000
    Q = 100_000

    st = DynamicSegTree(N)

    start = time.time()
    for _ in range(Q):
        pos = random.randint(0, N-1)
        cat = random.randint(0, M-1)
        st.set(pos, cat)
    end = time.time()
    print(f"Performed {Q} random set operations in {end - start:.2f}s")

    start = time.time()
    for _ in range(Q):
        l = random.randint(0, N-1)
        r = random.randint(l, min(N-1, l + 1000))
        cat = random.randint(0, M-1)
        _ = st.query(l, r, cat)
    end = time.time()
    print(f"Performed {Q} random queries in {end - start:.2f}s")

def test_complex_random_queries():
    N = 1000
    M = 1000

    # Generate random categories for each position
    arr = [random.randint(0, M-1) for _ in range(N)]
    st = DynamicSegTree(N)
    st.build(arr)

    # Perform multiple random queries and verify against brute force
    NUM_QUERIES = 1000
    for _ in range(NUM_QUERIES):
        l = random.randint(0, N-1)
        r = random.randint(l, N-1)
        cat = random.randint(0, M-1)

        expected = sum(1 for x in arr[l:r+1] if x == cat)
        actual = st.query(l, r, cat)

        assert actual == expected, f"Mismatch for query({l}, {r}, {cat}): expected {expected}, got {actual}"

if __name__ == "__main__":
    pytest.main([__file__])
