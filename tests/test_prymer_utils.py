
import unittest

import prymer

class PortTests(unittest.TestCase):
    """
    This set of tests is going to be structured
    differently from the others

    We're not going to directly test all the helper
    functions to port because port will call them anyway --
    so we're just going to call prymer.port as a whole.
    """

    def setUp(self):
        self._input = {
            "post": {
                "title": "test title",
                "content": "lorem ipsum..."
            },
            "user": {
                "id": 0,
                "name": "test",
                "group": "Admin"
            }
        }
    
    def test_documented_case(self):
        src = self._input
        dst = {
            "author": prymer.Get['user']['name'],
            "title": prymer.Get['post']['title'],
            "content": prymer.Get['post']['content']
        }
        expect = {
            "author": "test",
            "title": "test title",
            "content": "lorem ipsum..."
        }
        self.assertEqual(prymer.port(src, dst), expect)
    
    def test_onlyifexists_skipped(self):
        """
        if SkipIteration is raised,
        the entire k/v pair of a dict should be skipped
        (prymer.OnlyIfExists raises SkipIteration)
        """
        src = self._input
        dst = {
            "author": prymer.Get['user']['name'],
            "title": prymer.OnlyIfExists(prymer.Get['post']['not_title']),
            "content": prymer.Get['post']['content']
        }
        expect = {
            "author": "test",
            "content": "lorem ipsum..."
        }
        self.assertEqual(prymer.port(src, dst), expect)
    
    def test_fail_port(self):
        """
        if a callable raises,
        that should propagate
        """
        src = self._input
        dst = {
            "author": prymer.Get['user']['doesnt_exist']
        }
        with self.assertRaises(KeyError):
            prymer.port(src, dst)
    
    def test_template(self):
        """
        test prymer.Template
        """
        dst = prymer.Template({
            "author": prymer.Get['user']['name'],
            "title": prymer.Get['post']['title']
        })
        expect = {
            "author": "test",
            "title": "test title"
        }
        self.assertEqual(dst(self._input), expect)

class PortAsyncTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self._input = {
            "user": {
                "id": 0,
                "name": "test",
                "group": "Admin"
            },
            "post": {
                "title": "test title",
                "content": "lorem ipsum..."
            }
        }

    async def _get_IP(self, _):
        return "127.0.0.1"
    
    async def _get_addrinfo(self, _):
        return {
            "host": "localhost",
            "ip": self._get_IP
        }
    
    async def test_async_port(self):
        src = self._input
        dst = {
            "author": prymer.Get['user']['name'],
            "title": prymer.Get['post']['title'],
            "content": prymer.Get['post']['content'],
            "my_IP": self._get_IP
        }
        expect = {
            "author": "test",
            "title": "test title",
            "content": "lorem ipsum...",
            "my_IP": "127.0.0.1"
        }
        self.assertEqual(await prymer.port(src, dst), expect)
    
    async def test_async_port_nested(self):
        src = self._input
        dst = {
            "author": prymer.Get['user']['name'],
            "title": prymer.Get['post']['title'],
            "content": prymer.Get['post']['content'],
            "addrinfo": self._get_addrinfo
        }
        expect = {
            "author": "test",
            "title": "test title",
            "content": "lorem ipsum...",
            "addrinfo": {
                "host": "localhost",
                "ip": "127.0.0.1"
            }
        }

        self.assertEqual(await prymer.port(src, dst), expect)


if __name__=="__main__":
    unittest.main()