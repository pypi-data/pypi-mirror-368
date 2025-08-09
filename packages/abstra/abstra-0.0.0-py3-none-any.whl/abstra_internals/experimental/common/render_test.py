from unittest import TestCase

from .render import make_url

url = make_url("foo")

class TestUrl(TestCase):
    def test_empty(self):
        self.assertEqual(url(), "foo")
    
    def test_single(self):
        self.assertEqual(url("tables"), "foo/tables")
    
    def test_multiple(self):
        self.assertEqual(url("tables", "table"), "foo/tables/table")
    
    def test_query(self):
        self.assertEqual(url(page=2), "foo?page=2")
    
    def test_multiple_query(self):
        self.assertEqual(url("tables", page=2, limit=10), "foo/tables?page=2&limit=10")
    
    def test_json(self):
        self.assertEqual(url(json={"a": 1, "b": 2}), "foo?json=%7B%22a%22%3A%201%2C%20%22b%22%3A%202%7D")