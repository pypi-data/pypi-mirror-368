# This file is part of emzed (https://emzed.ethz.ch), a software toolbox for analysing
# LCMS data with Python.
#
# Copyright (C) 2020 ETH Zurich, SIS ID.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.


import abc
import copy
import pickle
import sqlite3
import sys

import numpy as np

import emzed

from ..utils.sqlite import create_uid
from .table_utils import MzType, RtType


class Expression(abc.ABC):
    compatible_with_sql_update = True

    @abc.abstractmethod
    def _to_sql_expression(self, aliases=None): ...

    @abc.abstractmethod
    def _accessors_involved(self): ...

    def copy(self):
        return copy.deepcopy(self)

    def __add__(left, right):
        """implements `+` for two columns or values"""
        return BinaryInfix("+", left, right)

    def __radd__(left, right):
        """implements `+=` for two columns or values"""
        return BinaryInfix("+", left, right)

    def __sub__(left, right):
        return BinaryInfix("-", left, right)

    def __rsub__(right, left):
        return BinaryInfix("-", left, right)

    def __truediv__(left, right):
        return BinaryInfix("/", left, right)

    def __rtruediv__(right, left):
        return BinaryInfix("/", left, right)

    def __mul__(left, right):
        return BinaryInfix("*", left, right)

    def __rmul__(right, left):
        return BinaryInfix("*", left, right)

    def __and__(left, right):
        return BinaryInfix("AND", left, right)

    def __rand__(right, left):
        return BinaryInfix("AND", left, right)

    def __or__(left, right):
        return BinaryInfix("OR", left, right)

    def __ror__(right, left):
        return BinaryInfix("OR", left, right)

    def __gt__(left, right):
        return BinaryInfix(">", left, right)

    def __ge__(left, right):
        return BinaryInfix(">=", left, right)

    def __lt__(left, right):
        return BinaryInfix("<", left, right)

    def __le__(left, right):
        return BinaryInfix("<=", left, right)

    def __eq__(left, right):
        return BinaryInfix("=", left, right)

    def __ne__(left, right):
        return BinaryInfix("!=", left, right)

    def __bool__(self):
        raise ValueError("I guess you forgot some parantheses around logical values.")

    def in_range(self, left, right):
        return (left <= self) & (self <= right)

    def approx_equal(self, other, atol, rtol):
        return (self - other).abs() <= atol + rtol * self.abs()

    def abs(self):
        return Unary(self, "abs", "abs({})")

    def max(self):
        """``table.column expression`` evaluating column to its maximal value.

        Examples:
        Given table t

        .. parsed-literal::

            a
            float
            -----
            2.00
            4.30
            1.50

        .. code-block:: python

        t.add_column('b ', t.a.max(), float)

        results

        .. parsed-literal::

            a      b
            float  float
            -----  -----
            2.00   4.30
            4.30   4.30
            1.50   4.30

        and

        .. parsed-literal::

            t.a.max().eval() == max(t.a) == 4.3

        """
        return Reduction(self, "max", "max({})")

    def min(self):
        """``table.column expression`` evaluating column to its minimal value,
        element-wise.

            Use analogous to :py:meth:`~.max`.
        """
        return Reduction(self, "min", "min({})")

    def round(self, digits=0):
        """expression to round column values to the given number of ``digits``,
        element-wise.

        :param digits: Number of digits applied for rounding.

        Use analogous to :py:meth:`~.max`.
        """
        return Unary(self, "round", "round({}, %d)" % digits)

    def floor(self):
        """Return the floor of the column values, element-wise.

            Example:

            .. parsed-literal::

                a
                float
                -----
                -1.70
                -1.50
                -0.20
                0.20
                1.50
                1.70
                2.00

        .. code-block:: python

            t.add_column('b ', t.a.floor(), float)

        results

        .. parsed-literal::

            a      b
            float  float
            -----  -----
            -1.70  -1.00
            -1.50  -1.00
            -0.20   0.00
            0.20   0.00
            1.50   1.00
            1.70   1.00
            2.00   2.00

        see also :py:meth:`~.max`.
        """
        return Unary(self, "floor", "cast({} as integer)")

    def if_not_none_else(left, right):
        return BinaryPrefix("ifnull", left, right)

    def then_else(self, then, else_):
        """expression to perform  ``if then else`` operations on Table Column.

        :param then: column or value returned if condition is ``True``.

        :param else: column or value returned if condition is ``False``.

        Examples:
        1)
        .. parsed-literal::

            a
            float
            -----
            2.00
            4.30
            1.50

        .. code-block:: python

        t.add_column('b ', (t.a>2).then_else(t.a, -1.0), float)

        results:

         .. parsed-literal::

            a      b
            float  float
            -----  -----
            2.00  -1.00
            4.30   4.30
            1.50  -1.00

        2)

        .. parsed-literal::

            a
            bool
            -----
            True
            False
            True

        .. code-block:: python

            t.add_column('b ', t.a.then_else('green', 'red'), str)

        retults:

            a      b
            bool   str
            -----  -----
            True   green
            False  red
            True   green

        """
        return ThenElse(self, then, else_)

    def is_none(self):
        """expression to evaluate ``None`` values in column.

        Since ``==`` operation is not possible with ``None`` it
        replaces Python expression ``if value is None:``

        Example:
        .. code-block:: python

            t.replace_column(t.a.is_none().then_else(1e-10, t.a), float)

        """
        return Predicate(self, "is null")

    def is_not_none(self):
        """Column expression to evaluate values different from ``None``.

        Since ``!=`` operation is not possible with ``None``
        it replaces Python expression ``if value is not None:``.

        Example:

        .. code-block:: python

           t1 = t.filter(t.a.is_not_none())

        """
        return Predicate(self, "is not null")

    def startswith(self, other):
        """Column expression to evaluate if value starts with the specified prefix,
        element-wise.

            : param: other: str defining prefix

        Example:
        .. parsed-literal::

            a
            str
            ---------
            hello
            hey
            you, hey?

        .. code-block:: python

            t.add_column('b ', t.a.startswith('he'), bool)

        results

        .. parsed-literal::

            a          b
            str        bool
            ---------  -----
            hello      True
            hey        True
            you, hey?  False

        """
        return StartsWith(self, other)

    def endswith(self, other):
        """Column expression to evaluate if value ends with the specified postfix,
        element-wise.

            : param: other: str defining postfix
        """
        return EndsWith(self, other)

    def contains(self, other):
        """Column expression to evaluate if value contains the specified string,
        element-wise.

            : param: other: String defining search sequence.

        """
        return Contains(self, other)

    def is_in(self, values):
        return IsIn(self, values)


class Predicate(Expression):
    def __init__(self, expression, sql_term):
        self.expression = expression
        self.sql_term = sql_term
        self._models_involved = expression._models_involved

    def _to_sql_expression(self, aliases=None):
        inner = self.expression._to_sql_expression(aliases)
        return f"({inner} {self.sql_term})"

    def __str__(self):
        return f"{self.expression!r} {self.sql_term}"

    def __repr__(self):
        return f"Predicate({self.expression!r}, {self.sql_term})"

    def _accessors_involved(self):
        return self.expression._accessors_involved()


class Value(Expression):
    def __init__(self, value):
        if isinstance(value, np.number):
            value = value.item()
        if isinstance(value, np.ndarray):
            value_new = value.flatten()
            if value_new.shape != (1,):
                dims = ", ".join(map(str, value.shape))
                raise ValueError(f"you passed an numpy array of dimensions ({dims})")
            value = value_new[0].item()

        if value is not None and not isinstance(value, (bool, int, float, str)):
            raise TypeError(f"invalid type {type(value)}")

        if value in (True, False):
            value = int(value)

        self.value = value
        self._model = None
        self._access_name = ""
        self._models_involved = set()

    def _to_sql_expression(self, aliases=None):
        if self.value is None:
            return "NULL"
        if self.value in (True, False):
            # older sqlite3 versions have no support for TRUE/FALSE
            return "({})".format(int(self.value))
        return "({!r})".format(self.value)

    def __str__(self):
        return f"{self.value!r}"

    def __repr__(self):
        return f"Value({self.value!r})"

    def _accessors_involved(self):
        return set()


class Unary(Expression):
    def __init__(self, expression, name, sql_template):
        self.expression = expression
        self.name = name
        self.sql_template = sql_template
        self._access_name = ""
        self._models_involved = expression._models_involved

    def _to_sql_expression(self, aliases=None):
        inner = self.sql_template.format(self.expression._to_sql_expression(aliases))
        return f"({inner})"

    def __str__(self):
        return self.sql_template.format(self.expression)

    __repr__ = __str__

    def _accessors_involved(self):
        return self.expression._accessors_involved()

    def eval(self):
        models = self._models_involved.copy()
        assert len(models) == 1
        model = models.pop()
        expression = self._to_sql_expression()
        result = model._conn.execute(
            f"SELECT {expression} FROM {model._access_name}"
        ).fetchall()
        return [r for (r,) in result]


class Reduction(Unary):
    def eval(self):
        return super().eval()[0]

    def _to_sql_expression(self, aliases=None):
        inner = self.sql_template.format(self.expression._to_sql_expression(aliases))

        models = self._models_involved.copy()
        assert len(models) == 1
        model = models.pop()
        return f"(SELECT {inner} FROM {model._access_name})"


class _Binary(Expression):
    def __init__(self, operator, left, right):
        self.operator = operator
        if not isinstance(left, Expression):
            left = Value(left)
        if not isinstance(right, Expression):
            right = Value(right)
        self.left = left
        self.right = right

        self._models_involved = set(left._models_involved) | set(right._models_involved)

    def _accessors_involved(self):
        return self.left._accessors_involved().union(self.right._accessors_involved())


class BinaryInfix(_Binary):
    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"

    def __repr__(self):
        return f"BinaryInfix({self.left}, {self.operator}, {self.right})"

    def _to_sql_expression(self, aliases=None):
        if aliases is None:
            aliases = {}

        sql_expression = "({} {} {})".format(
            self.left._to_sql_expression(aliases),
            self.operator,
            self.right._to_sql_expression(aliases),
        )
        return sql_expression


class BinaryPrefix(_Binary):
    def __str__(self):
        return f"{self.operator}({self.left}, {self.right})"

    def __repr__(self):
        return f"BinaryPrefix({self.operator}, {self.left}, {self.right})"

    def _to_sql_expression(self, aliases=None):
        if aliases is None:
            aliases = {}

        sql_expression = "({}({}, {}))".format(
            self.operator,
            self.left._to_sql_expression(aliases),
            self.right._to_sql_expression(aliases),
        )
        return sql_expression


class ThenElse(Expression):
    def __init__(self, condition, then, else_):
        if not isinstance(condition, Expression):
            condition = Value(condition)
        if not isinstance(then, Expression):
            then = Value(then)
        if not isinstance(else_, Expression):
            else_ = Value(else_)

        self.condition = condition
        self.then = then
        self.else_ = else_

        self._models_involved = (
            set(condition._models_involved)
            | set(then._models_involved)
            | set(else_._models_involved)
        )

    def _accessors_involved(self):
        return (
            self.condition._accessors_involved()
            .union(self.then._accessors_involved())
            .union(self.else_._accessors_involved())
        )

    def __str__(self):
        return f"({self.condition} ? {self.then} : {self.else_})"

    def __repr__(self):
        return f"ThenElse({self.condition}, {self.then}, {self.else_})"

    def _to_sql_expression(self, aliases=None):
        if aliases is None:
            aliases = {}

        c = self.condition._to_sql_expression(aliases)
        t = self.then._to_sql_expression(aliases)
        e = self.else_._to_sql_expression(aliases)

        sql_expression = f"""
              (CASE
                    WHEN ({c} IS NULL) THEN (NULL)
                    WHEN ({c}) THEN ({t})
                    ELSE ({e})
               END)"""
        return sql_expression


class FunctionWrapper:
    def __init__(self, function, model, ignore_nones, args):
        self.function = function
        self.model = model
        self.ignore_nones = ignore_nones
        self.args = args

        self.python_args = {
            i: ai for (i, ai) in enumerate(args) if not isinstance(ai, Expression)
        }

        self.expression_args = {
            i: ai for (i, ai) in enumerate(args) if isinstance(ai, Expression)
        }

    def reconstruct_all_function_args(self, db_args):
        args = [None] * len(self.args)

        for i, python_arg in self.python_args.items():
            args[i] = python_arg

        for (i, arg), db_arg in zip(self.expression_args.items(), db_args):
            if db_arg is None:
                args[i] = None
                continue
            if isinstance(arg, ColumnAccessor):
                t = arg.col_type
                args[i] = self.model._get_loader(t)(db_arg)
            else:
                args[i] = db_arg

        return tuple(args)

    def __call__(self, *db_args):
        try:
            args = self.reconstruct_all_function_args(db_args)
            if self.ignore_nones and any(ai is None for ai in args):
                return None
            result = self.function(*args)
            if isinstance(result, (emzed.Table, emzed.PeakMap)):
                raise TypeError(
                    f"function {self.function.__name__} must not return Table"
                    " or PeakMap"
                )
            if isinstance(result, np.number):
                result = result.item()
            if result is not None and not isinstance(result, (int, float, bool, str)):
                result = sqlite3.Binary(pickle.dumps(result))
            return result
        except:  # noqa: E722
            et, ev, tb = sys.exc_info()
            func = tb.tb_frame.f_locals["self"].function.__name__
            args = tb.tb_frame.f_locals["args"]
            ev = ev.__class__(
                "{} failed for args {}: {}".format(func, args, ev.args[0])
            )
            self.model._conn.set_exception(et, ev, tb)
        return None


class Apply(Expression):
    def __init__(self, model, function, args, ignore_nones):
        self._model = model

        self.args = args

        self._models_involved = set((model,))

        self.wrapper = FunctionWrapper(function, model, ignore_nones, args)

        nargs = len(self.wrapper.expression_args)

        self.fun_id = "fun_" + create_uid()  # we can not delete sqlite3 functions!
        self._model._conn.create_function(self.fun_id, nargs, self.wrapper)

    def _to_sql_expression(self, aliases=None):
        args = ", ".join(
            ai._to_sql_expression()  # if isinstance(ai, Expression) else str(ai)
            for ai in self.wrapper.expression_args.values()
        )

        return f"{self.fun_id}({args})"

    def _accessors_involved(self):
        return set((self._model._access_name,))


def column_accessor(model, col_name, col_type, db_col_name, access_name):
    if col_type in (str, int, float, bool, MzType, RtType):
        return ColumnAccessor(model, col_name, col_type, db_col_name, access_name)

    return NonAlgebraicColumnAccessor(
        model, col_name, col_type, db_col_name, access_name
    )


class ColumnAccessor(Expression):
    def __init__(self, model, col_name, col_type, db_col_name, access_name):
        self._model = model
        self.col_name = col_name
        self.col_type = col_type
        self.db_col_name = db_col_name
        self._access_name = access_name
        self._models_involved = set((model,))

    def __iter__(self):
        def generator():
            loader = self._model._get_loader(self.col_type)
            access_name = self._model._access_name
            col_name = self._model.col_name_mapping[self.col_name]
            stmt = f"SELECT {col_name} from {access_name};"
            yield from (
                loader(v[0]) if v[0] is not None else None
                for v in self._model._conn.execute(stmt)
            )

        return generator()

    def to_list(self):
        return list(self)

    def _to_sql_expression(self, aliases=None):
        if aliases is None:
            aliases = {}
        alias = aliases.get(self._model)
        col_name = self._model.col_name_mapping[self.col_name]
        if alias is None:
            return "{}.{}".format(self._access_name, col_name)
        else:
            return "{}.{}".format(alias, col_name)

    def _accessors_involved(self):
        return set((self._access_name,))

    def __str__(self):
        return self.col_name

    def __repr__(self):
        return f"Column({self.col_name})"

    def count_not_none(self):
        access_name = self._model._access_name
        cursor = self._model._conn.execute(
            f"SELECT count(*) FROM {access_name} WHERE {self.db_col_name} IS NOT NULL"
        )
        return cursor.fetchone()[0]

    def unique_values(self):
        access_name = self._model._access_name
        cursor = self._model._conn.execute(
            f"SELECT DISTINCT {self.db_col_name} FROM {access_name} WHERE"
            f" {self.db_col_name} IS NOT NULL"
        )
        loader = self._model._get_loader(self.col_type)
        return [loader(v[0]) for v in cursor]

    def unique_value(self):
        access_name = self._model._access_name
        cursor = self._model._conn.execute(
            f"SELECT COUNT(DISTINCT {self.db_col_name}) FROM {access_name} WHERE"
            f" {self.db_col_name} IS NOT NULL"
        )
        count = cursor.fetchone()[0]
        if count == 0:
            raise ValueError("the column is empty or contains only None values")
        if count > 1:
            raise ValueError(f"the column contains {count} different values")

        return self.unique_values()[0]

    def lookup(self, other_key, other_value):
        return Lookup(self, other_key, other_value)


class _StringLike(_Binary):
    def __init__(self, left, right):
        if not isinstance(left, Expression):
            assert isinstance(left, str)
            left = Value(left)

        assert isinstance(right, str)
        self.left = left
        self.right = right

        self._models_involved = set(left._models_involved)

    def _accessors_involved(self):
        return self.left._accessors_involved()

    def _to_sql_expression(self, aliases=None):
        left = self.left._to_sql_expression(aliases)

        return self._template.format(left=left, right=self.right)


class StartsWith(_StringLike):
    _template = "({left} LIKE '{right}%')"


class EndsWith(_StringLike):
    _template = "({left} LIKE '%{right}')"


class Contains(_StringLike):
    _template = "({left} LIKE '%{right}%')"


class NonAlgebraicColumnAccessor(ColumnAccessor):
    def _undefined_factory(op):
        def method(self, *a, **kw):
            raise TypeError(f"operation '{op}' not allowed for type {self.col_type}")

        return method

    __add__ = __radd__ = _undefined_factory("+")
    __sub__ = __rsub__ = _undefined_factory("-")
    __truediv__ = __rtruediv__ = _undefined_factory("/")
    __mul__ = __rmul__ = _undefined_factory("*")
    __and__ = __rand__ = _undefined_factory("&")
    __or__ = __ror__ = _undefined_factory("|")

    def _undefined_comp(self, other):
        raise TypeError(f"comparisons are not supported for type {self.col_type}")

    __gt__ = _undefined_comp
    __ge__ = _undefined_comp
    __lt__ = _undefined_comp
    __le__ = _undefined_comp
    __eq__ = _undefined_comp
    __ne__ = _undefined_comp


class Lookup(Expression):
    def __init__(self, left_key, right_key, right_value):
        self.left_key = left_key
        self.right_key = right_key
        self.right_value = right_value

        left_key_models = left_key._models_involved
        right_key_models = right_key._models_involved
        right_value_models = right_value._models_involved

        assert (
            right_key_models == right_value_models
        ), "other_key and other_value must refer to the same table"

        assert len(right_key_models) == 1, "more than one table involved"
        assert len(left_key_models) == 1, "more than one table involved"

        self._models_involved = left_key_models | right_key_models | right_value_models

        self.right_model = list(self.right_key._models_involved)[0]

        right_key_expression = self.right_key._to_sql_expression({})
        right_value_expression = self.right_value._to_sql_expression({})

        if hasattr(self.right_value, "col_type"):
            self.right_value_type = self.right_value.col_type
        else:
            self.right_value_type = None

        right_access_name = self.right_model._access_name

        conn = self.right_model._conn

        stmt = f"""SELECT {right_key_expression}, {right_value_expression}
                   FROM {right_access_name}
               """
        self.lookup = dict(conn.execute(stmt))

        if len(self.lookup) != len(self.right_model):
            raise LookupError("key value mapping is not unique")

    def _accessors_involved(self):
        return (
            self.left_key._accessors_involved()
            | self.right_key._accessors_involved()
            | self.right_value._accessors_involved(),
        )

    def _to_sql_expression(self, aliases=None):
        assert aliases is None

        left_model = list(self.left_key._models_involved)[0]
        left_key_expression = self.left_key._to_sql_expression({})

        def get(key):
            value = self.lookup.get(key)
            if self.right_value_type is None:
                return value
            return self.right_model._get_loader(self.right_value_type)(value)

        wrapper = FunctionWrapper(
            get,
            left_model,
            False,
            (self.left_key,),
        )
        fun_id = "fun_" + create_uid()  # we can not delete sqlite3 functions!
        left_model._conn.create_function(fun_id, 1, wrapper)
        return f"({fun_id}({left_key_expression}))"


class IsIn(Expression):
    def __init__(self, expression, values):
        self.expression = expression

        try:
            self.values = set(values)
        except TypeError:
            # might also happen if elements in values are not hashable, so
            # we fall back to list which might slow down lookup:
            try:
                self.values = list(values)
            except TypeError:
                raise ValueError("expected iterable for values argument")

        if any(isinstance(vi, (emzed.Table, emzed.PeakMap)) for vi in self.values):
            raise ValueError("is_in does not support PeakMap or Table values")

        def check(value):
            return value in values

        self._models_involved = expression._models_involved

        models = self._models_involved.copy()
        assert len(models) == 1
        model = models.pop()
        wrapper = FunctionWrapper(check, model, False, (self.expression,))
        self.fun_id = "fun_" + create_uid()  # we can not delete sqlite3 functions!
        model._conn.create_function(self.fun_id, 1, wrapper)

    def _to_sql_expression(self, aliases=None):
        inner = self.expression._to_sql_expression(aliases)
        return f"({self.fun_id}({inner}) = 1)"

    def __str__(self):
        return f"{self.expression!r}.is_in({self.values})"

    def __repr__(self):
        return f"IsIn({self.expression!r}, {self.values})"

    def _accessors_involved(self):
        return self.expression._accessors_involved()
