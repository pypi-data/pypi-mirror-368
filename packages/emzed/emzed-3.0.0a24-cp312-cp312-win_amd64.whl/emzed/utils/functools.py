import inspect
import textwrap


def extend_function(
    original_function, wrapped_function, extra_kw_args, extra_kw_args_doc
):
    args_spec = inspect.getfullargspec(original_function)

    new_args = args_spec.args[:]
    if args_spec.varargs is not None:
        new_args += ["*" + args_spec.varargs]
    if args_spec.kwonlydefaults is not None:
        new_args += [
            f"{name}={value!r}" for (name, value) in args_spec.kwonlydefaults.items()
        ]

    new_args += [f"{name}={value!r}" for (name, value) in extra_kw_args.items()]
    args_decl = ", ".join(new_args)

    new_args = args_spec.args[:]
    if args_spec.varargs is not None:
        new_args += ["*" + args_spec.varargs]
    if args_spec.kwonlydefaults is not None:
        new_args += [
            f"{name}={name}" for (name, value) in args_spec.kwonlydefaults.items()
        ]

    new_args += [f"{name}={name}" for (name, value) in extra_kw_args.items()]
    args = ", ".join(new_args)

    doc_string = original_function.__doc__ or ""

    if ":returns:" in doc_string:
        before, after = doc_string.split(":returns:", 1)
        doc_string = (
            before
            + "\n        "
            + "\n        ".join(extra_kw_args_doc)
            + "\n        :returns:"
            + after
        )

    else:
        doc_string += "\n        " + "\n        ".join(extra_kw_args_doc)

    _globals = {}
    _globals["wrapped"] = wrapped_function

    new_function_decl = textwrap.dedent(
        f"""
    def {original_function.__name__}({args_decl}):
        '''
        {doc_string}
        '''
        return wrapped({args})
    """
    )

    locals = {}
    exec(new_function_decl, _globals, locals)
    return locals[original_function.__name__]
