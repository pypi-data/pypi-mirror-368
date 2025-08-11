#! /usr/bin/env python
# Copyright 2020 Uwe Schmitt <uwe.schmitt@id.ethz.ch>

import re
from string import ascii_lowercase as _LOWERS
from string import ascii_uppercase as _CAPITALS
from string import digits as _DIGITS

_LEFT_PARENTHESIS = "("
_RIGHT_PARENTHESIS = ")"
_LEFT_BRACKET = "["
_RIGHT_BRACKET = "]"


def _next(reminder):
    return reminder[0], reminder[1:]


def _parse_optional_int(reminder):
    count = 0
    # counst start with digit > 0
    if reminder[0] in "123456789":
        count = int(reminder[0])
        reminder = reminder[1:]
        while reminder[0] in _DIGITS:
            token, reminder = _next(reminder)
            count = 10 * count + int(token)
    return count, reminder


def _parse_element_with_count(reminder):
    token, reminder = _next(reminder)
    assert token in _CAPITALS, "illegal formula: stopped parsing at " + token + reminder
    element = token
    if reminder[0] in _LOWERS:
        token, reminder = _next(reminder)
        element += token
    count, reminder = _parse_optional_int(reminder)
    if count == 0:
        count = 1
    return element, count, reminder


def _sub_formula_parser(reminder, formula, indent):
    token, reminder = _next(reminder)
    subformula, reminder = _parse(reminder, indent + "    ")
    count, reminder = _parse_optional_int(reminder)
    assert count > 0, "illegal formula: stopped parsing at " + reminder
    return reminder, formula + subformula * count


def _isotop_parser(reminder, formula, indent):
    token, reminder = _next(reminder)
    isonumber, reminder = _parse_optional_int(reminder)
    assert isonumber > 0, "illegal formula: stopped at " + reminder
    assert reminder[0] == _RIGHT_BRACKET
    token, reminder = _next(reminder)
    assert reminder[0] in _CAPITALS, "illegal formula: stopped at " + reminder
    elem, count, reminder = _parse_element_with_count(reminder)
    formula.extend(((elem, isonumber),) * count)
    return reminder, formula


def _element_parser(reminder, formula, indent):
    elem, count, reminder = _parse_element_with_count(reminder)
    formula.extend(((elem, None),) * count)
    return reminder, formula


_actions = {_LEFT_PARENTHESIS: _sub_formula_parser, _LEFT_BRACKET: _isotop_parser}

for k in _CAPITALS:
    _actions[k] = _element_parser


def _parse(reminder, indent=""):
    formula = []
    while True:
        if reminder[0] in [chr(0), _RIGHT_PARENTHESIS]:
            return formula, reminder[1:]
        action = _actions.get(reminder[0])
        if action is None:
            raise Exception("parser stops at %r" % reminder)
        reminder, formula = action(reminder, formula, indent)


def parse_formula(mf, re=re.compile(r"\s")):
    """
    Returns Counter mapping (symbol, sassnumber) -> sount
    corresponding to mf.
    For symbols in mf, where no massnumber is specified, this
    funcion returns None as massnumber.

    Eg.::

        >>> parse_formula("[13]C2C4H")
        Counter({('C', None): 4, ('C', 13): 2, ('H', None): 1})

    """
    from collections import Counter

    mf = re.sub("", mf)  # remove whitespaces
    symbols, _ = _parse(mf + chr(0))
    return Counter(symbols)


def join_formula(cc, delim=""):
    symbols = []
    order = dict((s, i) for (i, s) in enumerate("CHNOPS"))
    items = list(cc.items())

    def key(t):
        (elem, iso), count = t
        return order.get(elem, 999), (iso or 0)

    items.sort(key=key)

    for (elem, isonumber), count in items:
        if count == 0:
            continue
        if isonumber:
            if count > 1:
                symbols.append("[%d]%s%d" % (isonumber, elem, count))
            else:
                symbols.append("[%d]%s" % (isonumber, elem))
        else:
            if count > 1:
                symbols.append("%s%d" % (elem, count))
            if count == 1:
                symbols.append(elem)

    return delim.join(symbols)
