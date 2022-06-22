from typing import Iterator, List, Tuple
from itertools import pairwise
from pynoq import *

Fragments = List[str]


def intersperse(lst, item):
    result = [item] * (len(lst) * 2 - 1)
    result[0::2] = lst
    return result


def tokenize_by_char(text: str, delim: str, keep_delim: bool) -> Fragments:
    fragments = [frag.strip() for frag in text.split(delim)]
    if keep_delim:
        fragments = intersperse(fragments, delim)
    return [frag for frag in fragments if frag]  # Remove empty fragments
    

def tokenize(text: str) -> Fragments:
    "Tokenize the text using set of delimiters"
    delimiters = [
        dict(delim='=', keep_delim=True),
        dict(delim='(', keep_delim=True),
        dict(delim=')', keep_delim=True),
        dict(delim=',', keep_delim=False),
    ]
    fragments = [text]
    for delim in delimiters:
        old_fragments = fragments
        fragments = []
        for text in old_fragments:
            fragments.extend(tokenize_by_char(text, **delim))
    return fragments


def parse(text: str) -> Expr:
    
    def parse_expr(t: Iterator[Tuple[str, str]]) -> Expr:
        nonlocal token_pair
        token_pair = next(t)
        match token_pair:
            case (name, '('):
                args = parse_arg_list(t)
                token_pair = next(t) # Consume closing parenthesis
                return Fun(name, args)
            case (name, _):
                return Sym(name)
            case _:
                raise RuntimeError(f"Cannot match {token_pair}")
                
        
    def parse_arg_list(t: Iterator[Tuple[str, str]]) -> List[Expr]:
        nonlocal token_pair
        args = []
        token_pair = next(t)
        assert token_pair[0] == '('
        while token_pair[1] != ')':  # parse_expr will update token_pair
            args.append(parse_expr(t))
        return args
    
    tokens = tokenize(text)
    token_pair = tuple()
    t = pairwise(tokens+[' ', ' '])  # Token pairs generator, two spaces used as sentinel
    expr = parse_expr(t)
    return expr
    
    


if __name__ == '__main__':
    
    # import doctest
    # doctest.testmod()
    
    print(tokenize("swap(pair(a, b)) = pair(b, a)"))
