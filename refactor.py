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

# ... TODO ...
"""
                                                                # }}}1

from __future__ import print_function

import argparse, sys
import pyparsing as P

if sys.version_info.major == 2:                                 # {{{1
  pass
else:
  pass
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

# ... TODO ...

if __name__ == "__main__":
  sys.exit(main(*sys.argv[1:]))

# vim: set tw=70 sw=2 sts=2 et fdm=marker :
