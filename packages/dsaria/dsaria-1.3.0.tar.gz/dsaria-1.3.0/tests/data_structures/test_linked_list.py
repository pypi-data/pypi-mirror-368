import pytest
from dsaria.linked_list import LinkedList

def test_insert_normal_case():
    ll = LinkedList(val_type=int, unique_vals=False)
    ll.insert(val=5)
    ll.insert(val=3)
    ll.insert(val=7)
    assert ll.to_list() == [3, 5, 7]

def test_insert_empty_list():
    ll = LinkedList(val_type=int, unique_vals=False)
    ll.insert(val=10)
    assert ll.to_list() == [10]

def test_insert_duplicate_raises_value_error_if_unique():
    ll = LinkedList(val_type=int, unique_vals=True)
    ll.insert(val=1)
    with pytest.raises(ValueError):
        ll.insert(val=1)

def test_insert_wrong_type_raises_type_error():
    ll = LinkedList(val_type=int, unique_vals=False)
    with pytest.raises(TypeError):
        ll.insert(val="test")

def test_node_with_val_exists_true_and_false():
    ll = LinkedList(val_type=int, unique_vals=False)
    ll.insert(val=1)
    ll.insert(val=2)
    assert ll.node_with_val_exists(val=1) is True
    assert ll.node_with_val_exists(val=3) is False

def test_node_with_val_exists_type_error():
    ll = LinkedList(val_type=int, unique_vals=False)
    with pytest.raises(TypeError):
        ll.node_with_val_exists(val="int")

def test_search_found_and_not_found():
    ll = LinkedList(val_type=int, unique_vals=False)
    ll.insert(val=2)
    ll.insert(val=4)
    node = ll.search(2)
    assert node is not None and node.val == 2
    assert ll.search(10) is None

def test_search_type_error():
    ll = LinkedList(val_type=int, unique_vals=False)
    with pytest.raises(TypeError):
        ll.search("test")

def test_len_empty_and_nonempty():
    ll = LinkedList(val_type=int, unique_vals=False)
    assert len(ll) == 0
    ll.insert(val=1)
    ll.insert(val=2)
    assert len(ll) == 2

def test_to_list_returns_correct_values():
    ll = LinkedList(val_type=int, unique_vals=False)
    values = [5, 1, 3]
    for v in values:
        ll.insert(val=v)
    assert sorted(ll.to_list()) == sorted(values)

def test_delete_single_value():
    ll = LinkedList(val_type=int, unique_vals=False)
    ll.insert(val=1)
    ll.insert(val=2)
    ll.delete(val=1)
    assert ll.to_list() == [2]

def test_delete_multiple_values():
    ll = LinkedList(val_type=int, unique_vals=False)
    for v in [1,2,3,2,4]:
        ll.insert(val=v)
    ll.delete(val=2)
    assert 2 not in ll.to_list()
    assert sorted(ll.to_list()) == [1,3,4]

def test_delete_nonexistent_value_no_error():
    ll = LinkedList(val_type=int, unique_vals=False)
    ll.insert(val=1)
    ll.delete(val=99)
    assert ll.to_list() == [1]

def test_delete_type_error():
    ll = LinkedList(val_type=int, unique_vals=False)
    with pytest.raises(TypeError):
        ll.delete(val="int")

def test_clear_method():
    ll = LinkedList(val_type=int, unique_vals=False)
    ll.insert(val=1)
    ll.clear()
    assert ll.is_empty() is True
    assert len(ll) == 0

def test_is_empty_true_and_false():
    ll = LinkedList(val_type=int, unique_vals=False)
    assert ll.is_empty() is True
    ll.insert(val=10)
    assert ll.is_empty() is False

def test_repr_returns_correct_string():
    ll = LinkedList(val_type=int, unique_vals=False)
    assert repr(ll) == "Empty"
    ll.insert(val=2)
    ll.insert(val=1)
    ll.insert(val=3)
    assert repr(ll) == "1->2->3"

def test_vt_property_is_read_only():
    ll = LinkedList(val_type=int, unique_vals=True)
    with pytest.raises(AttributeError):
        ll.vt = str

def test_uv_property_is_read_only():
    ll = LinkedList(val_type=int, unique_vals=True)
    with pytest.raises(AttributeError):
        ll.uv = False