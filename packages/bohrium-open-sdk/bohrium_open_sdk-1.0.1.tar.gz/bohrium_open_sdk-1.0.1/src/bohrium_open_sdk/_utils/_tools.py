from typing import Any, Callable, Dict, Optional


def dict_traverser(
    data: Any,
    handlers: Dict[Any, Callable] = {},
    key: Optional[str] = None,
):
    for type, handler in handlers.items():
        if isinstance(data, type):
            new_res = handler(key, data)
            return new_res

    if isinstance(data, list) or isinstance(data, tuple):
        if isinstance(data, list):
            return [dict_traverser(item, handlers, key) for item in data]
        return (dict_traverser(item, handlers, key) for item in data)
    if not isinstance(data, dict):
        return data

    new_res = {}
    for k, v in data.items():
        new_res[k] = dict_traverser(v, handlers, k)
    return new_res
