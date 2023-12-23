import unittest

import prymer

class FromAttrTests(unittest.TestCase):
    def test_fromattr_where_attr_exists(self):
        #
        # In general, if you're going to do this,
        # you probably just want to do a prymer.Get.that_attr
        # instead anyway
        #
        class SomeClass:
            def __init__(self):
                self.the_attr = "test"
            
        a = SomeClass()
        b = prymer.FromAttr("the_attr")
        self.assertEqual(b(a), "test")
    
    def test_fromattr_with_default(self):
        #
        # This is the main use case you would want
        # to use FromAttr for (i.e. the attr might
        # not exist and you want a default when 
        # that happens, just like getattr())
        #
        class SomeClass:
            def __init__(self):
                self.the_attr = "test"
        
        a = SomeClass()
        b = prymer.FromAttr("not_the_attr", "but_default")
        self.assertEqual(b(a), "but_default")
    
    def test_fromattr_where_attr_doesnt_exist_raises_AttributeError(self):
        # 
        # In general, if you're going to do this,
        # you probably just want to do a prymer.Get.that_attr
        # instead anyway
        #
        class SomeClass:
            def __init__(self):
                self.the_attr = "test"
        
        a = SomeClass()
        b = prymer.FromAttr("not_the_attr")
        with self.assertRaises(AttributeError):
            b(a)

class KeyOrDefaultTests(unittest.TestCase):
    def test_keyordefault_where_key_exists_on_dict(self):
        #
        # You probably want just prymer.Get['the_key']
        # with this usage
        #
        a = {"k": "test"}
        b = prymer.KeyOrDefault("k")
        self.assertEqual(b(a), "test")
    
    def test_keyordefault_with_default_on_dict(self):
        #
        # This is the main intended usage of KeyOrDefault
        #
        a = {"k": "test"}
        b = prymer.KeyOrDefault("v","the_default")
        self.assertEqual(b(a), "the_default")
    
    def test_keyordefault_where_key_doesnt_exist_on_dict_raises_KeyError(self):
        #
        # You probably want just prymer.Get['the_key']
        # with this usage
        # However -- on a dict, this should raise
        # *KeyError*, not *IndexError*, because that's
        # what `{"k":"test"}['v']` would do
        #
        a = {"k": "test"}
        b = prymer.KeyOrDefault("v")
        with self.assertRaises(KeyError):
            b(a)
    
    def test_keyordefault_where_index_exists_on_list(self):
        #
        # You probably want just prymer.Get[2]
        # with this usage
        #
        a = [2,5,"test"]
        b = prymer.KeyOrDefault(2)
        self.assertEqual(b(a), "test")
    
    def test_keyordefault_with_default_on_list(self):
        #
        # This is an intended side effect usage of KeyOrDefault
        # (The idea is to provide *any* "square-bracket" usage
        # with an optional default)
        #
        a = [2,5,"test"]
        b = prymer.KeyOrDefault(3,"the_default")
        self.assertEqual(b(a), "the_default")
    
    def test_keyordefault_where_index_doesnt_exist_on_list_raises_IndexError(self):
        #
        # You probably want just prymer.Get[2]
        # with this usage
        # However -- on a list, this should raise
        # IndexError, because that's what e.g.
        # `[0,5][2]` would do.
        #
        a = [0,5]
        b = prymer.KeyOrDefault(2)
        with self.assertRaises(IndexError):
            b(a)

class StringTemplateTest(unittest.TestCase):
    def test_stringtemplate_input_dict(self):
        #
        # Probably the most intended usage of StringTemplate
        #
        a = {"name": "Test"}
        b = prymer.StringTemplate("Test value: {name}")
        self.assertEqual(b(a), "Test value: Test")
    
    def test_stringtemplate_input_list(self):
        #
        # Alternate intended usage of StringTemplate
        #
        a = ["test", "test2"]
        b = prymer.StringTemplate("{0} vs {1}")
        self.assertEqual(b(a), "test vs test2")

        c = prymer.StringTemplate("{} vs {}")
        self.assertEqual(c(a), "test vs test2")
    
    def test_stringtemplate_input_doesnt_matter(self):
        #
        # Make sure double brackets don't interpolate
        # although this is more of a str.format test...
        #
        a = {"name": "test"}
        b = prymer.StringTemplate("Test name {{name}}")
        self.assertEqual(b(a), "Test name {name}")
    
    def test_stringtemplate_input_dict_incorrect(self):
        #
        # When the template key doesn't exist it should raise
        # just like str.format would
        #
        a = {"type": "test"}
        b = prymer.StringTemplate("test name: {name}")
        with self.assertRaises(KeyError):
            b(a)
    
    def test_stringtemplate_input_list_incorrect(self):
        # 
        # When the template key index doesn't exist it should raise
        # just like str.format would
        #
        a = ["one"]
        b = prymer.StringTemplate("{0} {1} {2}")
        with self.assertRaises(IndexError):
            b(a)

class OnlyIfExistsTests(unittest.TestCase):
    def test_index_in_list_exists(self):
        #
        # Intended usage, outcome 1: key exists
        #
        # This should just return the value in that case
        #
        a = ["one"]
        b = prymer.OnlyIfExists(0)
        self.assertEqual(b(a), "one")
    
    def test_key_in_dict_exists(self):
        #
        # Intended usage, outcome 1: key exists
        #
        # This should just return the value in that case
        #
        a = {"k": "test"}
        b = prymer.OnlyIfExists("k")
        self.assertEqual(b(a), "test")
    
    def test_callable_key(self):
        #
        # Intended usage, outcome 1: key returns a value and does not raise
        #
        # In this case, the callable should itself be a prymer.Composite
        # function, or otherwise one that takes just input and returns an
        # updated result. If the callable does not raise an exception that indicates
        # the lack of an existing value (e.g. KeyError, AttributeError,
        # IndexError, ValueError, TypeError, or prymer.SkipIteration),
        # OnlyIfExists should just return that value.
        #
        a = {"k": "test"}
        b = prymer.KeyOrDefault("k")
        c = prymer.OnlyIfExists(b)
        self.assertEqual(c(a), "test")
    
    def test_index_in_list_doesnt_exist(self):
        #
        # Intended usage, outcome 2: key does not exist
        #
        # OnlyIfExists should raise SkipIteration -- which is
        # a signal to prymer.port (and its derived composite
        # prymer.Template) that the entire iteration should be
        # ignored, which would skip either (1) the index in a list/seq
        # or (2) a k/v pair in a dict.
        #
        a = {"k": "test"}
        b = prymer.OnlyIfExists("v")
        with self.assertRaises(prymer.SkipIteration):
            b(a)
    
    def test_key_in_dict_doesnt_exist(self):
        #
        # Intended usage, outcome 2: key does not exist
        #
        # OnlyIfExists should raise SkipIteration -- which is
        # a signal to prymer.port (and its derived composite
        # prymer.Template) that the entire iteration should be
        # ignored, which would skip either (1) the index in a list/seq
        # or (2) a k/v pair in a dict.
        #
        a = ["one","two"]
        b = prymer.OnlyIfExists(2)
        with self.assertRaises(prymer.SkipIteration):
            b(a)
    
    def test_callable_key_raises_data_error(self):
        #
        # Intended usage, outcome 2: callable key raises a
        # exception indicating the lack of a value where one
        # should likely be, e.g. KeyError, AttributeError, IndexError,
        # ValueError, TypeError, or prymer.SkipIteration
        #
        # OnlyIfExists should raise SkipIteration -- which is
        # a signal to prymer.port (and its derived composite
        # prymer.Template) that the entire iteration should be
        # ignored, which would skip either (1) the index in a list/seq
        # or (2) a k/v pair in a dict.
        #
        a = ["one","two"]
        b = prymer.KeyOrDefault(2)
        c = prymer.OnlyIfExists(b)
        with self.assertRaises(prymer.SkipIteration):
            c(a)
    
    def test_callable_key_raises_OTHER_error(self):
        #
        # Callable key raises an exception that does NOT
        # indicate the lack of a value where one should be
        # Indicating that something else has gone terribly wrong
        #
        # OnlyIfExists should *reraise*
        #

        def raise_IOError(_):
            raise IOError("beep boop")
        a = ["one","two"]
        b = raise_IOError
        c = prymer.OnlyIfExists(b)
        with self.assertRaises(IOError):
            c(a)

if __name__=="__main__":
    unittest.main()