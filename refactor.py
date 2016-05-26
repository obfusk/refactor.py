#!/usr/bin/python

# --                                                            ; {{{1
#
# File        : refactor.py
# Maintainer  : Felix C. Stegerman <flx@obfusk.net>
# Date        : 2016-05-25
#
# Copyright   : Copyright (C) 2016  Felix C. Stegerman
# Version     : v0.0.1
# License     : GPLv3+
#
# --                                                            ; }}}1

                                                                # {{{1
r"""
Python (2+3) implementation of Factor' (a subset of Factor)


Examples
========

>>> import refactor as R
>>> with open("fizzbuzz.refactor") as f: fizz = f.read()

# ... TODO ...

>>> R.evaluate("37 [ 42 swap ] call")
deque([42, 37])

>>> try: R.evaluate("37 call")
... except R.Error as e: print(e)
not a quotation

# ... TODO ...

>>> R.evaluate("swap", (1, 2, 3))
deque([1, 3, 2])

>>> try: R.evaluate("swap", ())
... except R.StackUnderFlowError as e: print("underflow")
underflow

# ... TODO ...

"""
                                                                # }}}1

from __future__ import print_function

import argparse, collections, sys
import pyparsing as P

if sys.version_info.major == 2:                                 # {{{1
  pass
else:
  xrange = range
                                                                # }}}1

__version__       = "0.0.1"

# TODO
def main(*args):                                                # {{{1
  p = argument_parser(); n = p.parse_args(args)
  if n.test:
    import doctest
    doctest.testmod(verbose = n.verbose)
    return 0
  # ...
  return 0
                                                                # }}}1

# TODO
def argument_parser():                                          # {{{1
  p = argparse.ArgumentParser(description = "refactor")
  p.add_argument("--version", action = "version",
                 version = "%(prog)s {}".format(__version__))
  p.add_argument("--test", action = "store_true",
                 help = "run tests (not refactor)")
  p.add_argument("--verbose", "-v", action = "store_true",
                 help = "run tests verbosely")
  return p
                                                                # }}}1

class Immutable(object):                                        # {{{1

  """immutable base class"""

  __slots__ = []

  args_are_mandatory = False

  @property
  def ___slots(self):
    return [x for x in self.__slots__ if not x.startswith("_")]

  def __init__(self, data = None, **kw):
    x = data if data is not None else {}; x.update(kw)
    ks = set(x.keys()); ss = set(self.___slots)
    for k in self.___slots:
      if k in x:
        self._Immutable___set(k, x[k]); del x[k]
      else:
        self._Immutable___set(k, None)
    if len(x):
      raise TypeError("unknown keys: {}".format(", ".join(x.keys())))
    if self.args_are_mandatory and ks != ss:
      raise TypeError("missing keys: {}".format(", ".join(ss - ks)))

  def ___set(self, k, v):
    super(Immutable, self).__setattr__(k, v)

  def __setattr__(self, k, v):
    if k in self.___slots:
      raise AttributeError(
        "'{}' object attribute '{}' is read-only".format(
          self.__class__.__name__, k
        )
      )
    else:
      raise AttributeError(
        "'{}' object has no attribute '{}'".format(
          self.__class__.__name__, k
        )
      )

  def copy(self, **kw):
    return type(self)(dict(self.iteritems()), **kw)

  def iteritems(self):
    return ((k, getattr(self, k)) for k in self.___slots)

  if sys.version_info.major == 2:
    def items(self):
      return list(self.iteritems())
  else:
    def items(self):
      return self.iteritems()

  def __eq__(self, rhs):
    if not isinstance(rhs, type(self)): return NotImplemented
    return dict(self.iteritems()) == dict(rhs.iteritems())

  def __lt__(self, rhs):
    if not isinstance(rhs, type(self)): return NotImplemented
    return sorted(self.iteritems()) < sorted(rhs.iteritems())

  def __le__(self, rhs):
    if not isinstance(rhs, type(self)): return NotImplemented
    return sorted(self.iteritems()) <= sorted(rhs.iteritems())

  def __gt__(self, rhs):
    if not isinstance(rhs, type(self)): return NotImplemented
    return sorted(self.iteritems()) > sorted(rhs.iteritems())

  def __ge__(self, rhs):
    if not isinstance(rhs, type(self)): return NotImplemented
    return sorted(self.iteritems()) >= sorted(rhs.iteritems())

  def __repr__(self):
    return '{}({})'.format(
      self.__class__.__name__,
      ", ".join("{} = {}".format(k, repr(v))
                for (k,v) in self.iteritems())
    )

  def __hash__(self):
    return hash(tuple(self.iteritems()))
                                                                # }}}1

class Term(Immutable):
  def copy(self): raise NotImplementedError

class Bool(Term):
  __slots__ = "value".split()
  def __init__(self, string):
    super(Bool, self).__init__(value = string == "t")
  @property
  def string(self): return "t" if self.value else "f"
  def __str__(self): return self.string

# TODO
class Num(Term):
  __slots__ = "value".split()
  def __init__(self, string):
    super(Num, self).__init__(value = int(string))              # TODO
  def __str__(self): return str(self.value)

# TODO
class Str(Term):
  __slots__ = "value".split()
  def __init__(self, value):
    super(Str, self).__init__(value = value)
  def __str__(self): return repr(self.value)                   # TODO

class Ary(Term):
  __slots__ = "values".split()
  def __init__(self, values):
    super(Ary, self).__init__(values = tuple(values))
  def __str__(self):
    if not self.values: return "{ }"
    return "{ " + " ".join( str(x) for x in self.values ) + " }"

class Word(Term):
  __slots__ = "value".split()
  def __init__(self, value):
    super(Word, self).__init__(value = value)
  def __str__(self): return self.value

class Quot(Term):
  __slots__ = "terms".split()
  def __init__(self, terms):
    super(Quot, self).__init__(terms = tuple(terms))
  def __str__(self):
    if not self.terms: return "[ ]"
    return "[ " + " ".join( str(x) for x in self.terms ) + " ]"

class Eff(Term):                                                # {{{1
  __slots__ = "pre post".split()
  def __init__(self, pre, post):
    super(Eff, self).__init__(pre = tuple(pre), post = tuple(post))
  @property
  def arity(self): return len(self.post) - len(self.pre)
  def __str__(self):
    a, b = " ".join(self.pre), " ".join(self.post)
    return "(" + (" " + a if a else "") + " -- " + \
                 (b + " " if b else "") + ")"
                                                                # }}}1

class Def(Term):                                                # {{{1
  __slots__ = "name eff terms".split()
  def __init__(self, name, eff, terms):
    super(Def, self).__init__(name = name, eff = eff,
                              terms = tuple(terms))
  def __str__(self):
    return ": " + self.name + " " + str(self.eff) + " " + \
                  " ".join( str(x) for x in self.terms ) + " ;"
                                                                # }}}1

class Prog(Term):
  __slots__ = "terms".split()
  def __init__(self, terms):
    super(Prog, self).__init__(terms = tuple(terms))
  def __str__(self):
    return "".join( str(x) + "\n" for x in self.terms )

def isterm(x): return isinstance(x, Term)

# TODO
def parse(s):                                                   # {{{1
  """Parse a Factor' program."""

  # TODO: whitespace ???
  sym           = P.alphanums + "!@#$%^&*()-_=+[]{}|<>,.?/'"    # TODO
  g, k, l, i, z = P.Group, P.Keyword, P.Literal, P.Suppress, \
                  P.ZeroOrMore
  ik            = lambda x: i(k(x))
  value, term   = P.Forward(), P.Forward()
  symbol        = P.Word(sym)("sym")
  boolean       = P.Combine( k("t") | k("f") )("bool")
  number        = P.Word(P.nums)("num")                         # TODO
  string        = P.Combine( i(l('"')) +
                    P.Regex(r'(?:[^"\n\r\\]|'
                            r'(?:\\(?:[^x]|x[0-9a-fA-F]+)))*') +
                    i(l('"')) )("str")                          # TODO
  array         = g( ik("{") + z(g(value)) + ik("}") )("ary")
  value        << ( boolean | number | string | array )
  word          = symbol("word")                      # not prim|bool
  quotation     = g( ik("[") + z( ~ik("]") + term )("body") +
                                   ik("]") )("quot")
  stack_effect  = g( ik("(" ) + z( ~ik("--") + symbol )("pre") +
                                    ik("--") +
                                z( ~ik(")" ) + symbol )("post") +
                                    ik(")" ) )
  word_def      = g( ik(":") + word("name") + stack_effect("eff") +
                               z(term)("body") + ik(";") )("wdef")
  term         << g( quotation | value | word )       # or primitive
  program       = z( g(word_def) | term )("prog")
  return program.parseString(s, True)
                                                                # }}}1

# TODO
def read(x):                                                    # {{{1
  r"""
  Parse a string into a Factor' expression.

  >>> import refactor as R
  >>> x = ''' 1 [ y z ] foo' 99 t f '''
  >>> y = ''' "foo\\"bar" nil? { 1 "two" 3 } '''
  >>> z = ''' x : foo ( x -- y z ) 42 ; y42 '''
  >>> for t in R.read(x).terms: print(repr(t))
  Num(value = 1)
  Quot(terms = (Word(value = 'y'), Word(value = 'z')))
  Word(value = "foo'")
  Num(value = 99)
  Bool(value = True)
  Bool(value = False)
  >>> for t in R.read(y).terms: print(repr(t))
  Str(value = 'foo\\"bar')
  Word(value = 'nil?')
  Ary(values = (Num(value = 1), Str(value = 'two'), Num(value = 3)))
  >>> for t in R.read(z).terms: print(repr(t))
  Word(value = 'x')
  Def(name = 'foo', eff = Eff(pre = ('x',), post = ('y', 'z')), terms = (Num(value = 42),))
  Word(value = 'y42')
  """

  if isterm(x): return x
  if not isinstance(x, P.ParseResults): x = parse(x)
  if   "bool" in x: return Bool(x.bool)
  elif "num"  in x: return Num(x.num)
  elif "str"  in x: return Str(x.str)
  elif "ary"  in x: return Ary(map(read, x.ary))
  elif "word" in x: return Word(x.word)
  elif "quot" in x: return Quot(map(read, x.quot.body))
  elif "wdef" in x:
    return Def(x.wdef.name, Eff(tuple(x.wdef.eff.pre),
                                tuple(x.wdef.eff.post)),
                            map(read, x.wdef.body))
  elif "prog" in x: return Prog(map(read, x.prog))
                                                                # }}}1

class Error(Exception): pass
class StackUnderFlowError(Error): pass
class UnknownNameError(Error): pass

RULES       = {}
PRIMITIVES  = {}

def rule(t):
  """Function decorator for a semantic rule."""
  def g(f): RULES[t] = f; return f
  return g

# TODO
def prim(name, effect):                                         # {{{1
  """Function decorator for a semantic rule for a primitive
  operation."""

  pre, post = [ x.split() for x in effect.split("--") ]
  arity     = len(post) - len(pre)
  def g(f):
    d = dict(pre = pre, post = post, arity = arity, f = f)
    PRIMITIVES[name] = d; return f
  return g
                                                                # }}}1

def evaluate(e, s = (), env = None):
  """Evaluate Factor' expression e with stack s and environment
  env."""
  if isinstance(e, str)                   : e   = read(e)
  if not isinstance(s, collections.deque) : s   = collections.deque(s)
  if env is None                          : env = {}
  RULES[type(e)](e, s, env)
  return s

# TODO
@rule(Word)
def rule_word(e, s, env):                                       # {{{1
  if e.value in PRIMITIVES:
    PRIMITIVES[e.value]["f"](s, env)
  elif e.value in env:
    s.append(Quot(env[e.value].terms))
    evaluate(Word("call"), s, env)                              # TODO
  else:
    raise UnknownNameError(e.value)
                                                                # }}}1

@rule(Bool)
@rule(Num)
@rule(Str)
def rule_bool_num_str(e, s, env):
  s.append(e.value)

@rule(Ary)
def rule_ary(e, s, env):
  s.append(list(e.values))

@rule(Quot)
def rule_quot(e, s, env):
  s.append(e)

# TODO
@rule(Def)
def rule_def(e, s, env):
  env[e.name] = e

@rule(Prog)
def rule_prog(e, s, env):
  for term in e.terms: evaluate(term, s, env)

# ... TODO ...

# TODO
@prim("call", "callable --")
def prim_call(s, env):
  c = pop(s)
  if not isinstance(c, Quot): raise Error("not a quotation")
  for term in c.terms: evaluate(term, s, env)

# ... TODO ...

@prim("swap", "x y -- y x")
def prim_swap(s, env):
  x, y = pop(s, 2); push(s, y, x)

# ... TODO ...

def pop(s, n = 1):                                              # {{{1
  r"""
  Pop n values from stack s, returning them in "stack-effect order".

  >>> import refactor as R
  >>> from collections import deque
  >>> s = deque((1, 2, 3)); x, y = R.pop(s, 2); x, y
  (2, 3)
  >>> z = R.pop(s); z
  1
  """

  if len(s) < n: raise StackUnderFlowError
  if n == 1: return s.pop()
  return reversed([ s.pop() for i in xrange(n) ])
                                                                # }}}1

def push(s, *values):                                           # {{{1
  r"""
  Push values onto stack s.

  >>> import refactor as R
  >>> from collections import deque
  >>> s = deque(); R.push(s, 1, 2, 3); s
  deque([1, 2, 3])
  """

  for v in values: s.append(v)
                                                                # }}}1

if __name__ == "__main__":
  sys.exit(main(*sys.argv[1:]))

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
