import unittest

import shapyro

class ShapyroGetTests(unittest.TestCase):
    # Primitives access
    def test_identity(self):
        _from = "test"
        get_from = shapyro.Get
        self.assertEqual(get_from(_from), "test")

    def test_dict(self):
        _from = {"k": "test"}
        get_k = shapyro.Get['k']
        self.assertEqual(get_k(_from), "test")
    
    def test_dict_get(self):
        _from = {"k": "test"}
        get_get = shapyro.Get.get
        # it should (1) get the `.get` attribute from the dict
        # and then (2) the parenthesis after should call that method
        # on the key "k"
        self.assertEqual(get_get(_from)("k"), "test")

    def test_list_dict(self):
        _from = [{"k": "test"}]
        get_first_k = shapyro.Get[0]['k']
        self.assertEqual(get_first_k(_from), "test")

    def test_str_index(self):
        _from = "test"
        get_first = shapyro.Get[0]
        self.assertEqual(get_first(_from), "t")
    
    def test_obj_attr(self):
        class TestObj(object):
            some_attr = "test"
        
        from_obj = TestObj()
        get_some_attr = shapyro.Get.some_attr
        self.assertEqual(get_some_attr(from_obj), "test")
    
    # Complex/nested access
    def test_obj_with_dict(self):
        class TestObj(object):
            some_attr_map = {"k": "test"}
        
        from_obj = TestObj()
        get_some_attr_map = shapyro.Get.some_attr_map['k']
        self.assertEqual(get_some_attr_map(from_obj), "test")
    
    def test_dict_with_obj(self):
        class TestObj(object):
            some_attr = "test"
        
        from_map_obj = {"k": TestObj()}
        get_attr_from_map = shapyro.Get['k'].some_attr
        self.assertEqual(get_attr_from_map(from_map_obj), "test")
    
    def test_bracket_callable(self):
        _from = "tset"
        c = lambda n: n.replace("set", "est")
        get_fixed_from = shapyro.Get[c]
        self.assertEqual(get_fixed_from(_from), "test")
    
    # Failure cases
    # These should match the failures you'd get from
    # doing the same access directly on the value
    def test_dict_missing_key_raises_KeyError(self):
        from_map = {"k": "test"}
        get_j = shapyro.Get['j']
        with self.assertRaises(KeyError):
            get_j(from_map)
    
    def test_obj_missing_attr_raises_AttributeError(self):
        class TestObj(object):
            some_attr = "test"
        
        get_non_exist = shapyro.Get.non_exist
        some_obj = TestObj()
        with self.assertRaises(AttributeError):
            get_non_exist(some_obj)
    
    def test_list_missing_index_raises_IndexError(self):
        from_list = []
        get_first = shapyro.Get[0]
        with self.assertRaises(IndexError):
            get_first(from_list)
    

    
if __name__ == "__main__":
    unittest.main()
