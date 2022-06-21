# pynoq

Python port of Alexey Kutepov's [Noq](https://github.com/tsoding/Noq), originally written in Rust. Simple expression transformer that is not [Coq](https://coq.inria.fr/).

Developed (incrementally) using Alexey's [video series](https://www.youtube.com/watch?v=Ra_Fk7JFMoo&list=PLpM-Dvs8t0VZVE64QKPf6y_TIUwj5nKQ7).

## Quick start
```shell
$ python pynoq.py
```

## Description
The application design is closely modeled by the original [Noq](https://github.com/tsoding/Noq) system. 

## Personal note
This project served for me as a possibility to get acquainted with 
  * the new Python pattern matching functionality ([`match` statement](https://docs.python.org/3/tutorial/controlflow.html#match-statements)),
  * type hints and [mypy](http://mypy-lang.org/),
  * unit testing using [pytest](https://pytest.org)

Big thanks to [Alexey](https://github.com/tsoding) for sharing great educative content!