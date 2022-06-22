from enum import auto
from collections import deque
from typing import Iterator, List, Tuple, Iterable
from itertools import pairwise, chain
from pynoq import *

# Peekable class unscrupously copied from
# https://more-itertools.readthedocs.io/en/stable/_modules/more_itertools/more.html#peekable
# Method next_if added.

_marker = object()
class Peekable:
    """Wrap an iterator to allow lookahead and prepending elements.

    Call :meth:`peek` on the result to get the value that will be returned
    by :func:`next`. This won't advance the iterator:

        >>> p = peekable(['a', 'b'])
        >>> p.peek()
        'a'
        >>> next(p)
        'a'

    Pass :meth:`peek` a default value to return that instead of raising
    ``StopIteration`` when the iterator is exhausted.

        >>> p = peekable([])
        >>> p.peek('hi')
        'hi'

    peekables also offer a :meth:`prepend` method, which "inserts" items
    at the head of the iterable:

        >>> p = peekable([1, 2, 3])
        >>> p.prepend(10, 11, 12)
        >>> next(p)
        10
        >>> p.peek()
        11
        >>> list(p)
        [11, 12, 1, 2, 3]

    peekables can be indexed. Index 0 is the item that will be returned by
    :func:`next`, index 1 is the item after that, and so on:
    The values up to the given index will be cached.

        >>> p = peekable(['a', 'b', 'c', 'd'])
        >>> p[0]
        'a'
        >>> p[1]
        'b'
        >>> next(p)
        'a'

    Negative indexes are supported, but be aware that they will cache the
    remaining items in the source iterator, which may require significant
    storage.

    To check whether a peekable is exhausted, check its truth value:

        >>> p = peekable(['a', 'b'])
        >>> if p:  # peekable has items
        ...     list(p)
        ['a', 'b']
        >>> if not p:  # peekable is exhausted
        ...     list(p)
        []

    """

    def __init__(self, iterable):
        self._it = iter(iterable)
        self._cache = deque()

    def __iter__(self):
        return self

    def __bool__(self):
        try:
            self.peek()
        except StopIteration:
            return False
        return True

    def peek(self, default=_marker):
        """Return the item that will be next returned from ``next()``.

        Return ``default`` if there are no items left. If ``default`` is not
        provided, raise ``StopIteration``.

        """
        if not self._cache:
            try:
                self._cache.append(next(self._it))
            except StopIteration:
                if default is _marker:
                    raise
                return default
        return self._cache[0]
    
    def next_if(self, predicate):
        """Call ``next()`` if the returned item fulfills the ``predicate``.
        
        Otherwise it returns None.
        """
        if predicate(self.peek(None)):
            return next(self)
        return None

    def prepend(self, *items):
        """Stack up items to be the next ones returned from ``next()`` or
        ``self.peek()``. The items will be returned in
        first in, first out order::

            >>> p = peekable([1, 2, 3])
            >>> p.prepend(10, 11, 12)
            >>> next(p)
            10
            >>> list(p)
            [11, 12, 1, 2, 3]

        It is possible, by prepending items, to "resurrect" a peekable that
        previously raised ``StopIteration``.

            >>> p = peekable([])
            >>> next(p)
            Traceback (most recent call last):
              ...
            StopIteration
            >>> p.prepend(1)
            >>> next(p)
            1
            >>> next(p)
            Traceback (most recent call last):
              ...
            StopIteration

        """
        self._cache.extendleft(reversed(items))

    def __next__(self):
        if self._cache:
            return self._cache.popleft()
        return next(self._it)

    def _get_slice(self, index):
        # Normalize the slice's arguments
        step = 1 if (index.step is None) else index.step
        if step > 0:
            start = 0 if (index.start is None) else index.start
            stop = maxsize if (index.stop is None) else index.stop
        elif step < 0:
            start = -1 if (index.start is None) else index.start
            stop = (-maxsize - 1) if (index.stop is None) else index.stop
        else:
            raise ValueError('slice step cannot be zero')

        # If either the start or stop index is negative, we'll need to cache
        # the rest of the iterable in order to slice from the right side.
        if (start < 0) or (stop < 0):
            self._cache.extend(self._it)
        # Otherwise we'll need to find the rightmost index and cache to that
        # point.
        else:
            n = min(max(start, stop) + 1, maxsize)
            cache_len = len(self._cache)
            if n >= cache_len:
                self._cache.extend(islice(self._it, n - cache_len))

        return list(self._cache)[index]

    def __getitem__(self, index):
        if isinstance(index, slice):
            return self._get_slice(index)

        cache_len = len(self._cache)
        if index < 0:
            self._cache.extend(self._it)
        elif index >= cache_len:
            self._cache.extend(islice(self._it, index + 1 - cache_len))

        return self._cache[index]


# Fragments = List[str]

# def intersperse(lst, item):
#     result = [item] * (len(lst) * 2 - 1)
#     result[0::2] = lst
#     return result


# def tokenize_by_char(text: str, delim: str, keep_delim: bool) -> Fragments:
#     fragments = [frag.strip() for frag in text.split(delim)]
#     if keep_delim:
#         fragments = intersperse(fragments, delim)
#     return [frag for frag in fragments if frag]  # Remove empty fragments
    

# def tokenize(text: str) -> Fragments:
#     "Tokenize the text using set of delimiters"
#     delimiters = [
#         dict(delim='=', keep_delim=True),
#         dict(delim='(', keep_delim=True),
#         dict(delim=')', keep_delim=True),
#         dict(delim=',', keep_delim=False),
#     ]
#     fragments = [text]
#     for delim in delimiters:
#         old_fragments = fragments
#         fragments = []
#         for text in old_fragments:
#             fragments.extend(tokenize_by_char(text, **delim))
#     return fragments

# def parse(text: str) -> Expr:
    
#     def parse_expr(t: Iterator[Tuple[str, str]]) -> Expr:
#         nonlocal token_pair
#         token_pair = next(t)
#         match token_pair:
#             case (name, '('):
#                 args = parse_arg_list(t)
#                 token_pair = next(t) # Consume closing parenthesis
#                 return Fun(name, args)
#             case (name, _):
#                 return Sym(name)
#             case _:
#                 raise RuntimeError(f"Cannot match {token_pair}")
                
        
#     def parse_arg_list(t: Iterator[Tuple[str, str]]) -> List[Expr]:
#         nonlocal token_pair
#         args = []
#         token_pair = next(t)
#         assert token_pair[0] == '('
#         while token_pair[1] != ')':  # parse_expr will update token_pair
#             args.append(parse_expr(t))
#         return args
    
#     tokens = tokenize(text)
#     token_pair = tuple()
#     t = pairwise(tokens+[' ', ' '])  # Token pairs generator, two spaces used as sentinel
#     expr = parse_expr(t)
#     return expr
    
    

class TokenKind(Enum):
    Sentinel = auto()
    Sym = auto()
    LParen = auto()
    RParen = auto()
    Comma = auto()
    Equals = auto()
    

@dataclass
class Token:
    kind: TokenKind
    text: str
    
    
def tokenize(text: Iterable[str]):
    chars = pairwise(chain(text, '  '))
    for x, x_next in chars:
        match x:
            case '(': yield Token(TokenKind.LParen, x)
            case ')': yield Token(TokenKind.RParen, x)
            case ',': yield Token(TokenKind.Comma, x)
            case '=': yield Token(TokenKind.Equals, x)
            case ' ': pass
            case _:
                if x.isalnum(): 
                    text = [x]
                else: raise RuntimeError(f'Cannot tokenize {x}{x_next}...')
                while True:
                    if not x_next.isalnum(): 
                        yield Token(TokenKind.Sym, ''.join(text))
                        break
                    x, x_next = next(chars)
                    if x.isalnum(): text.append(x)
    yield Token(TokenKind.Sentinel, '')


def parse(text: str) -> Expr:
    
    def parse_expr(t: Iterator[Tuple[Token, Token]]) -> Expr:
        nonlocal token_pair
        token_pair = next(t)
        match token_pair:
            case (Token(TokenKind.Sym, name), Token(TokenKind.LParen, _)):
                # token_pair = next(t)  # Consume opening parenthesis       
                args = parse_arg_list(t)
                assert token_pair[0].kind == TokenKind.RParen
                # token_pair = next(t) # Consume closing parenthesis
                return Fun(name, args)
            case (Token(TokenKind.Sym, name), _):
                return Sym(name)
            case _:
                raise RuntimeError(f"Cannot match {token_pair}")
                
        
    def parse_arg_list(t: Iterator[Tuple[Token, Token]]) -> List[Expr]:
        nonlocal token_pair
        token_pair = next(t) # Consume opening parenthesis
        if [t.kind for t in token_pair] == [TokenKind.LParen, TokenKind.RParen]:
            token_pair = next(t)
            return []
        args = []
        while token_pair[0].kind != TokenKind.RParen:  # parse_expr will update token_pair
            args.append(parse_expr(t))
            assert token_pair[1].kind in {TokenKind.Comma, TokenKind.RParen}
            token_pair = next(t)
        return args
    
    tokens = tokenize(text)
    token_pair = tuple()
    t = pairwise(tokens)  # Token pairs generator, two spaces used as sentinel
    expr = parse_expr(t)
    return expr
    



# def parse(text: str, t: Iterable[Tuple[Token, Token]]=None) -> Expr:
#     if not t:
#         tokens = tokenize(text)
#         t = pairwise(tokens)
#     for token_pair in t:
#         match token_pair:
#             case (Token(TokenKind.Sym, text), Token(TokenKind.LParen, _)):
#                 # Function call
#                 args = parse_args(t)
                
#             case (Token(TokenKind.Sym, text), _):
#                 # Just a symbol
#                 return Sym(text)
#             case _: raise RuntimeError(f'Expected symbol token, found {token}')


if __name__ == '__main__':
    
    # import doctest
    # doctest.testmod()

    for token in tokenize("swap(pair(a, b)) = pair(b, a)"):
        print(token)
