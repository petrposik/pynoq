import pytest
from pynoq.parser import *

from .testingvars import *

tokenizer_test_pairs = [
    ('a', ['a']),
    ('abc', ['abc']),
    ('f()', ['f', '(', ')']),
    ('foo()', ['foo', '(', ')']),
    ('f(a)', ['f', '(', 'a', ')']),
    ('foo(abc)', ['foo', '(', 'abc', ')']),
    ('f(a, b)', ['f', '(', 'a', 'b', ')']),
    ('foo(abc, bcd)', ['foo', '(', 'abc', 'bcd', ')']),
    ('f(g())', ['f', '(', 'g', '(', ')', ')']),
    ('foo(gee())', ['foo', '(', 'gee', '(', ')', ')']),
    ('f(g(a))', ['f', '(', 'g', '(', 'a', ')', ')']),
    ('foo(gee(abc))', ['foo', '(', 'gee', '(', 'abc', ')', ')']),
    ('f(g(), h())', ['f', '(', 'g', '(', ')', 'h', '(', ')', ')']),
    ('foo(gee(), hue())', ['foo', '(', 'gee', '(', ')', 'hue', '(', ')', ')']),
    ('f(g(a), h(b))', ['f', '(', 'g', '(', 'a', ')', 'h', '(', 'b', ')', ')']),
    ('foo(gee(abc), hue(bcd))', ['foo', '(', 'gee', '(', 'abc', ')', 'hue', '(', 'bcd', ')', ')']),
]

@pytest.mark.parametrize('text, tokens', tokenizer_test_pairs)
def test_tokenize(text, tokens):
    assert tokenize(text) == tokens


parser_test_pairs = [
    ('a', Sym(a)),
    ('abc', Sym(abc)),
    ('f()', Fun(f, [])),
    ('foo()', Fun(foo, [])),
    ('f(a)', Fun(f, [Sym(a)])),
    ('foo(abc)', Fun(foo, [Sym(abc)])),
    ('f(a, b)', Fun(f, [Sym(a), Sym(b)])),
    ('foo(abc, bcd)', Fun(foo, [Sym(abc), Sym(bcd)])),
    ('f(g())', Fun(f, [Fun(g, [])])),
    ('foo(gee())', Fun(foo, [Fun(gee, [])])),
    ('f(g(a))', Fun(f, [Fun(g, [Sym(a)])])),
    ('foo(gee(abc))', Fun(foo, [Fun(gee, [Sym(abc)])])),
    ('f(g(), h())', Fun(f, [Fun(g, []), Fun(h, [])])),
    ('foo(gee(), hue())', Fun(foo, [Fun(gee, []), Fun(hue, [])])),
    ('f(g(a), h(b))', Fun(f, [Fun(g, [Sym(a)]), Fun(h, [Sym(b)])])),
    ('foo(gee(abc, bcd), hue(bcd, abc))', Fun(foo, [Fun(gee, [Sym(abc), Sym(bcd)]), Fun(hue, [Sym(bcd), Sym(abc)])])),
]

@pytest.mark.parametrize('text, expr', parser_test_pairs)
def test_parse(text, expr):
    assert parse(text) == expr