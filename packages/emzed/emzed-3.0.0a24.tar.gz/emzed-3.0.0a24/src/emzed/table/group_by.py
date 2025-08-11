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


import pickle
import statistics
import sys

from emzed.utils.sqlite import create_uid

from .expressions import ColumnAccessor, Expression
from .pickle import Pickle


class AggregateFunctionWrapper:
    def __init__(self, function, model, ignore_nones, args):
        self.function = function
        self.model = model
        self.ignore_nones = ignore_nones
        self.args = args
        self.nargs = len(args)

        self.python_args = {
            i: ai for (i, ai) in enumerate(args) if not isinstance(ai, Expression)
        }

        self.expression_args = {
            i: ai for (i, ai) in enumerate(args) if isinstance(ai, Expression)
        }

    def __call__(self, *args):
        self.values = []
        return self

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

    def step(self, *db_args):
        args = self.reconstruct_all_function_args(db_args)
        if self.ignore_nones and any(ai is None for ai in args):
            return

        self.values.append(args)

    def finalize(self):
        if self.ignore_nones:
            values = [v for v in self.values if v is not None]
        else:
            values = self.values
        try:
            if values:
                # unzip and create list of lists:
                unpacked = list(map(list, zip(*values)))
            else:
                return None
            result = self.function(*unpacked)
            if result is not None and not isinstance(result, (int, str, float)):
                result = pickle.dumps(result)
            return result
        except:  # noqa: E722
            et, ev, tb = sys.exc_info()
            func = tb.tb_frame.f_locals["self"].function.__name__
            values = tb.tb_frame.f_locals["unpacked"]

            v_str = ", ".join(map(str, values))
            ev = ev.__class__(
                "{} failed for values {}: {}".format(func, v_str, ev.args[0])
            )
            self.model._conn.set_exception(et, ev, tb)

        return None


class GroupBy:
    def __init__(self, model, col_names, group_nones):
        self.model = model
        self.col_names = col_names
        self.group_nones = group_nones

    def aggregate(self, function, *args, ignore_nones=True):
        wrapped = AggregateFunctionWrapper(function, self.model, ignore_nones, args)
        self.model._conn.create_aggregate("_f", len(args), wrapped)
        return self._agg("_f", *args)

    def id(self):
        last_id = -1

        def next_id(_):
            nonlocal last_id
            last_id += 1
            return last_id

        return self.aggregate(next_id, "0")

    def std(self, expression):
        return self.aggregate(
            lambda values: None if len(values) < 2 else statistics.stdev(values),
            expression,
        )

    def median(self, expression):
        return self.aggregate(
            lambda values: None if not values else statistics.median(values), expression
        )

    def _logical_agg(self, agg, check, expression, ignore_nones):
        if ignore_nones:

            def _agg(values):
                if all(v is None for v in values):
                    return None
                return agg(check(v) for v in values if v is not None)

        else:

            def _agg(values):
                return agg(v is not None and check(v) for v in values)

        return self.aggregate(_agg, expression, ignore_nones=False)

    def all_false(self, expression, ignore_nones=False):
        return self._logical_agg(
            all, lambda v: bool(v) is False, expression, ignore_nones
        )

    def any_false(self, expression, ignore_nones=False):
        return self._logical_agg(
            any, lambda v: bool(v) is False, expression, ignore_nones
        )

    def all_true(self, expression, ignore_nones=False):
        return self._logical_agg(
            all, lambda v: bool(v) is True, expression, ignore_nones
        )

    def any_true(self, expression, ignore_nones=False):
        return self._logical_agg(
            any, lambda v: bool(v) is True, expression, ignore_nones
        )

    def all_none(self, expression):
        def agg(values):
            return all(v is None for v in values)

        return self.aggregate(agg, expression, ignore_nones=False)

    def any_none(self, expression):
        def agg(values):
            return any(v is None for v in values)

        return self.aggregate(agg, expression, ignore_nones=False)

    def _agg(self, function, *expressions):
        arg_expressions = [
            expression
            if isinstance(expression, str)
            else expression._to_sql_expression()
            for expression in expressions
        ]

        access_name = self.model._access_name

        columns = [self.model.col_name_mapping[name] for name in self.col_names]

        group_by_spec = ", ".join(columns)

        index_name = "_index_{}".format(create_uid())

        cursor = self.model._conn.cursor()

        cursor.execute(f"CREATE INDEX {index_name} ON {access_name}({group_by_spec});")

        if self.group_nones:
            condition = " AND ".join(
                f"({access_name}.{name} IS NULL AND A.{name} is NULL"
                f" OR {access_name}.{name} = A.{name})"
                for name in columns
            )
        else:
            condition = " AND ".join(
                f"({access_name}.{name} = A.{name})" for name in columns
            )

        join = "JOIN" if self.group_nones else "LEFT JOIN"

        arg_expression = ", ".join(arg_expressions)

        stmt = f"""
            SELECT A.F
            FROM {access_name}
            {join} (
                SELECT {group_by_spec}, {function}({arg_expression}) AS F
                FROM {access_name}
                GROUP BY {group_by_spec}
            ) A
            ON {condition}
            ORDER BY data._index;
        """

        try:
            values = [row[0] for row in cursor.execute(stmt)]
            for i, v in enumerate(values):
                if isinstance(v, bytes) and v[0] == 128 and v[-1] == 46:
                    # looks like a pickle, they start with \x80 and end with '.'
                    values[i] = Pickle(v)
            return values
        finally:
            cursor.execute(f"DROP INDEX IF EXISTS {index_name};")
            cursor.close()

    def sum(self, expression):
        return self._agg("SUM", expression)

    def min(self, expression):
        return self._agg("MIN", expression)

    def max(self, expression):
        return self._agg("MAX", expression)

    def count(self):
        return self._agg("COUNT", "*")

    def mean(self, expression):
        return self._agg("AVG", expression)
