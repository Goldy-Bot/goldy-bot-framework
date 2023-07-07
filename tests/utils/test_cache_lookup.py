from .. import cache_lookup

tuple_list_type_cache = [
    (56, "uwu"),
    ("jeff", "uwu_v2")
]

dict_type_cache = {
    "sussy_wussy": "just a test",
    "damn": 1452365
}

tuple_set_list_cache = {
    ("willywonka", 2525),
    ("1452365", "damn")
}


def test_cache_lookup_tuple():
    assert cache_lookup(56, tuple_list_type_cache) == (56, "uwu")
    assert cache_lookup("jeff", tuple_list_type_cache) == ("jeff", "uwu_v2")

def test_cache_lookup_dict():
    assert cache_lookup("sussy_wussy", dict_type_cache) == "just a test"
    assert cache_lookup("damn", dict_type_cache) == 1452365

def test_cache_lookup_set():
    assert cache_lookup("willywonka", tuple_set_list_cache) == ("willywonka", 2525)
    assert cache_lookup("1452365", tuple_set_list_cache) == ("1452365", "damn")