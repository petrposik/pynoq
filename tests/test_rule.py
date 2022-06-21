from pynoq import *

def test_substitute_bindings():
    expr = Fun('pair', [Sym('a'), Sym('b')])
    bindings = {'a': Fun(name='f', args=[Sym(name='a')]), 'b': Fun(name='g', args=[Sym(name='b')])}
    assert str(substitute_bindings(bindings, expr)) == 'pair(f(a), g(b))'

class TestPatternMatch:

    pattern = Fun("swap", 
                  [Fun("pair", 
                       [Sym("a"), 
                        Sym("b")])])

    def test_patternMatch_ok(self):
        expr = Fun("swap", 
                    [Fun("pair", 
                        [Fun("f", [Sym("a"), Sym("b")]),
                        Fun("g", [Sym("a"), Sym("b")])])])
        assert pattern_match(self.pattern, expr) == {'a': Fun("f", [Sym("a"), Sym("b")]), 'b': Fun("g", [Sym("a"), Sym("b")])}

    def test_patternMatch_failTopNodeDoesNotMatch(self):
        expr = Fun("foo", 
                    [Fun("pair", 
                        [Fun("f", [Sym("a"), Sym("b")]),
                        Fun("g", [Sym("a"), Sym("b")])])])
        assert pattern_match(self.pattern, expr) == {}
        
    def test_patternMatch_failBoundSymbolDoesNotMatch(self):
        pattern = Fun("swap", 
                    [Fun("pair", 
                        [Sym("a"), 
                         Sym("a")])])
        expr = Fun("swap", 
                    [Fun("pair", 
                        [Fun("f", [Sym("a"), Sym("b")]),
                        Fun("g", [Sym("a"), Sym("b")])])])
        assert pattern_match(pattern, expr) == {}


class TestRuleApplication:
    
    def test_applyAll_ok(self):
        # Rule: swap(pair(a, b)) = pair(b, a)
        swap = Rule(
            head=Fun("swap", 
                    [Fun("pair", [Sym("a"), Sym("b")])]),
            body=Fun("pair", [Sym("b"), Sym("a")])
        )
        expr = Fun("foo", [
                Fun("swap", 
                    [Fun("pair", [Fun("f", [Sym("a")]),
                                    Fun("g", [Sym("b")])])]),
                Fun("swap", 
                    [Fun("pair", [Fun("q", [Sym("c")]),
                                    Fun("z", [Sym("d")])])]),
                ])
        assert str(swap.apply_all(expr)) == 'foo(pair(g(b), f(a)), pair(z(d), q(c)))'

