from enum import Enum
from dataclasses import dataclass
from itertools import pairwise
from typing import Dict, List
from copy import deepcopy




@dataclass
class Expr:
    "Common ancestor of nodes in AST"
    pass


Bindings = Dict[str, Expr]


@dataclass
class Sym(Expr):
    """AST node representing simple symbols (e.g., variables)
    
    >>> Sym("a")
    Sym(name='a')
    >>> print(_)
    a
    """
    name: str
    
    def __str__(self):
        return self.name


@dataclass
class Fun(Expr):
    """AST node representing a functor
    
    >>> Fun("f", [Sym("a"), Sym("b")])
    Fun(name='f', args=[Sym(name='a'), Sym(name='b')])
    >>> print(_)
    f(a, b)
    """
    name: str
    args: List[Expr]
    
    def __str__(self) -> str:
        return f"{self.name}({', '.join(map(str, self.args))})"


@dataclass
class Rule:
    "A transformation rule prescribing pattern to match and expression it should be transformed to"
    head: Expr
    body: Expr
    
    def __str__(self) -> str:
        return f"{self.head} = {self.body}"
    
    def apply_all(self, expr: Expr) -> Expr:
        "Find all matches of the rule head and apply all substitutions"
        if bindings := pattern_match(self.head, expr):
            # If expr matches the rule head, use the found bindings,
            # apply them to rule's body, and return resulting expression
            print(bindings)
            return substitute_bindings(bindings, self.body)
        else:
            # If expression does not match the rule, ...
            match expr:
                case Sym(_):
                    return deepcopy(expr)
                case Fun(name, args):
                    return Fun(name, [self.apply_all(arg) for arg in args])
                case _: 
                    raise RuntimeError('Unknown expression kind')
                
            
def substitute_bindings(bindings: Bindings, expr: Expr) -> Expr:
    """Transform expression using the known bindings
    
    >>> expr = Fun('pair', [Sym('a'), Sym('b')])
    >>> print(expr)
    pair(a, b)
    >>> bindings = {'a': Fun(name='f', args=[Sym(name='a')]), 'b': Fun(name='g', args=[Sym(name='b')])}
    >>> print(substitute_bindings(bindings, expr))
    pair(f(a), g(b))
    """
    match expr:
        case Sym(name):
            if name in bindings:
                return deepcopy(bindings[name])
            else:
                return deepcopy(expr)
        case Fun(name, args):
            new_name = None
            match bindings.get(name, None):
                case Sym(sym_name): new_name = sym_name
                case None: new_name = name
                case _: raise Exception(f"Expected symbol in the places of functor {name}")
            new_args = [substitute_bindings(bindings, arg) for arg in args]
            return Fun(new_name, new_args)
            
        
def pattern_match(pattern: Expr, expr: Expr) -> Bindings:
    'Check that expr matches a pattern, and return the found bindings'
    
    def pattern_match_impl(pattern: Expr, expr: Expr) -> bool:
        match (pattern, expr):
            case (Sym(name), _):
                if name in bindings:
                    # If name is already bound, check that the expression 
                    # it is bound to is the same as the matched expression
                    return bindings[name] == expr
                else:
                    bindings[name] = deepcopy(expr)
                    return True
            case (Fun(name1, args1), Fun(name2, args2)) if name1 == name2:
                if len(args1) != len(args2): return False
                for arg1, arg2 in zip(args1, args2):
                    if not pattern_match_impl(arg1, arg2): return False
                return True
            case _:
                return False
    
    bindings: Bindings = {}
    return bindings if pattern_match_impl(pattern, expr) else {}
    # return None
    

class TokenKind(Enum):
    """Token kinds"""
    SYM = 1
    LPAREN = 2
    RPAREN = 3
    COMMA = 4
    EQUALS = 5
    
    
@dataclass
class Token:
    """Token in the input stream"""
    kind: TokenKind
    text: str


class Lexer:
    """Lexer for the input stream"""
    def __init__(self, chars: str):
        self.chars = chars

    def __iter__(self):
        return self
    
    def __next__(self):
        for curr_char, next_char in pairwise(self.chars):
            return curr_char
        else:
            raise StopIteration()


if __name__ == '__main__':
    
    import doctest
    doctest.testmod()
    
    for token in Lexer("swap(pair(a, b)) = pair(b, a)"):
        print(token)
