from pynoq import *

def test_Sym():
    assert str(Sym('a')) == 'a'
    
def test_Fun_singleArgument():
    assert str(Fun('f', [Sym('a')])) == 'f(a)'
    
def test_Fun_multipleArguments():
    assert str(Fun('f', [Sym('a'), Sym('b')])) == 'f(a, b)'