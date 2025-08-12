# tests/test_hello.py
# import sys, os
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hello_pypi.main import say_hello

def test_say_hello():
    assert say_hello("World") == "Hello, World!"
