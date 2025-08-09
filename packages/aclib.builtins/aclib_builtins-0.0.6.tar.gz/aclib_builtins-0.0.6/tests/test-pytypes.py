import unittest
from aclib.builtins import Object

class MyObject(Object):
    def __init__(self, name: str) -> None:
        self.name = name

class TestObject(unittest.TestCase):
    def test___repr__(self):
        o = MyObject('test_obj')
        self.assertEqual(repr(o), "<MyObject (name='test_obj')>")

TestObject().test___repr__()