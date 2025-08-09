from pathlib import Path


def tokenized_expand(name: str | bytes | Path) -> tuple[str, dict[str, str]]:
    """Expand shell variables of the forms $var, ${var} and %var%.
    Unknown variables are left unchanged.

    Expand paths containing shell variable substitutions. The following rules apply:
        - no expansion within single quotes
        - '$$' is translated into '$'
        - '%%' is translated into '%' if '%%' is not seen in %var1%%var2%
        - ${var} is accepted.
        - $varname is accepted.
        - %var% is accepted.
        - Vars can be made out of letters, digits and the characters '_-'
        (though is not verified in the ${var} and %var% cases)

    :param name: String to expand
    :return: Tuple of (expanded string, dictionary of tokens)
    """
    import os
    import string

    if isinstance(name, bytes):
        name = name.decode("utf-8")

    if isinstance(name, Path):
        name = name.as_posix()

    name = os.fspath(name)
    token_map: dict = {}

    if "$" not in name and "%" not in name:
        return name, token_map

    var_chars = string.ascii_letters + string.digits + "_-"
    quote = "'"
    percent = "%"
    brace = "{"
    rbrace = "}"
    dollar = "$"
    environ = os.environ

    result = name[:0]
    index = 0
    path_len = len(name)
    while index < path_len:
        c = name[index : index + 1]
        if c == quote:  # no expansion within single quotes
            name = name[index + 1 :]
            path_len = len(name)
            try:
                index = name.index(c)
                result += c + name[: index + 1]
            except ValueError:
                result += c + name
                index = path_len - 1
        elif c == percent:  # variable or '%'
            if name[index + 1 : index + 2] == percent:
                result += c
                index += 1
            else:
                name = name[index + 1 :]
                path_len = len(name)
                try:
                    index = name.index(percent)
                except ValueError:
                    result += percent + name
                    index = path_len - 1
                else:
                    var = name[:index]
                    try:
                        if environ is None:
                            value = os.fsencode(os.environ[os.fsdecode(var)]).decode("utf-8")  # type: ignore[unreachable]
                        else:
                            value = environ[var]
                        token_map[var] = value
                    except KeyError:
                        value = percent + var + percent
                    result += value
        elif c == dollar:  # variable or '$$'
            if name[index + 1 : index + 2] == dollar:
                result += c
                index += 1
            elif name[index + 1 : index + 2] == brace:
                name = name[index + 2 :]
                path_len = len(name)
                try:
                    index = name.index(rbrace)
                except ValueError:
                    result += dollar + brace + name
                    index = path_len - 1
                else:
                    var = name[:index]
                    try:
                        if environ is None:
                            value = os.fsencode(os.environ[os.fsdecode(var)]).decode("utf-8")  # type: ignore[unreachable]
                        else:
                            value = environ[var]
                        token_map[var] = value
                    except KeyError:
                        value = dollar + brace + var + rbrace
                    result += value
            else:
                var = name[:0]
                index += 1
                c = name[index : index + 1]
                while c and c in var_chars:
                    var += c
                    index += 1
                    c = name[index : index + 1]
                try:
                    if environ is None:
                        value = os.fsencode(os.environ[os.fsdecode(var)]).decode("utf-8")  # type: ignore[unreachable]
                    else:
                        value = environ[var]
                    token_map[var] = value
                except KeyError:
                    value = dollar + var
                result += value
                if c:
                    index -= 1
        else:
            result += c
        index += 1

    return result, token_map


def tokenized_replace(name: str, tokens: dict[str, str]) -> str:
    """Replace text with shell variables.

    :param name: String to replace
    :param tokens: Dictionary of replacement tokens
    :return: replaced string
    """
    for key, value in tokens.items():
        name = name.replace(value, f"${key}")
    return name
