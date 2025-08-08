import pytest
import dsaria.sort

def test_bubble_sort_normal_cases():
    assert dsaria.sort.bubble_sort(arr=[1,3,4,5,2,6]) == [1,2,3,4,5,6]
    assert dsaria.sort.bubble_sort(arr=[2,4,3,1,9]) == [1,2,3,4,9]
    assert dsaria.sort.bubble_sort(arr=[5,4,3,2,1]) == [1,2,3,4,5]

def test_bubble_sort_single_and_empty():
    assert dsaria.sort.bubble_sort(arr=[1]) == [1]
    assert dsaria.sort.bubble_sort(arr=[]) == []

def test_bubble_sort_already_sorted():
    assert dsaria.sort.bubble_sort(arr=[1,2,3,4,5]) == [1,2,3,4,5]

def test_bubble_sort_duplicates():
    assert dsaria.sort.bubble_sort(arr=[4,2,2,1,3,4]) == [1,2,2,3,4,4]

def test_bubble_sort_all_equal():
    assert dsaria.sort.bubble_sort(arr=[7,7,7,7]) == [7,7,7,7]

def test_bubble_sort_floats():
    arr = [1.1, 2.2, 0.5, 2.1]
    assert dsaria.sort.bubble_sort(arr=arr) == sorted(arr)

def test_bubble_sort_strings():
    assert dsaria.sort.bubble_sort(arr=["b","a","c"]) == ["a","b","c"]

def test_bubble_sort_mixed_types_raises_type_error():
    with pytest.raises(TypeError):
        dsaria.sort.bubble_sort(arr=[1, "2", 3])