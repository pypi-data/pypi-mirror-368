#!/usr/bin/env python

import types
from pprint import pprint

import emzed


def _recurse(module, result, seen=set()):
    if not module.__name__.startswith("emzed"):
        return

    if hasattr(module, "__all__"):
        sub_entries = module.__all__
    else:
        sub_entries = module.__dir__()

    for entry in sub_entries:
        if entry.startswith("_"):
            continue
        sub_module = getattr(module, entry)
        if isinstance(sub_module, (types.FunctionType, types.ClassType)):
            result.add(module.__name__ + "." + entry)
        elif isinstance(sub_module, emzed.Table):
            result.add(module.__name__ + "." + entry)
            result.update(
                {
                    ".".join((module.__name__, entry, name))
                    for name in sub_module.col_names
                }
            )
        elif isinstance(sub_module, types.ModuleType):
            if sub_module in seen:
                return
            seen.add(sub_module)
            result.add(module.__name__ + "." + entry)
            _recurse(sub_module, result)


result = set()
_recurse(emzed, result)
pprint(sorted(result))
