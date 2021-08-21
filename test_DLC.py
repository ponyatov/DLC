import pytest
from DLC import *

def test_any(): assert True

hello = Object('Hello')
world = Object('World')

def test_hello():
    assert hello.test() == '\n<object:Hello>'

def test_world():
    assert world.test() == '\n<object:World>'
    assert (hello // world).test() == \
        '\n<object:Hello>' +\
        '\n\t0: <object:World>'

def test_shifts():
    left = Object('left')
    right = Object('right')
    assert (hello << left >> right).test() == \
        '\n<object:Hello>' +\
        '\n\tobject = <object:left>' +\
        '\n\tright = <object:right>' +\
        '\n\t0: <object:World>'


def test_env():
    assert glob['env'].head(test=True) == '<env:global>'
    assert glob['global'].head(test=True) == '<env:global>'

def test_nop():
    assert glob['nop'].eval(glob) is None


def test_lexer_none():
    lexer.input('')
    assert not lexer.token()

def test_lexer_spaces():
    lexer.input(' \t\r\n')
    assert not lexer.token()
