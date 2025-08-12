# pico_ioc_flask/decorators.py
from typing import Any, Optional

def controller(cls=None, *, base_path: str = "", lazy: bool = False, blueprint: Optional[str] = None):
    def deco(c):
        setattr(c, "_pico_rest_is_controller", True)
        setattr(c, "_pico_rest_base_path", base_path.rstrip("/"))
        setattr(c, "_pico_rest_lazy", bool(lazy))
        setattr(c, "_pico_rest_blueprint", blueprint)
        return c
    return deco(cls) if cls else deco

def _http_route_factory(methods):
    methods = list(methods)
    def outer(rule: str, **flask_kwargs):
        def deco(func):
            routes = getattr(func, "_pico_routes", [])
            routes.append({"rule": rule, "methods": methods, "kwargs": flask_kwargs})
            setattr(func, "_pico_routes", routes)
            return func
        return deco
    return outer

route         = _http_route_factory(["GET"])
get_route     = _http_route_factory(["GET"])
post_route    = _http_route_factory(["POST"])
put_route     = _http_route_factory(["PUT"])
patch_route   = _http_route_factory(["PATCH"])
delete_route  = _http_route_factory(["DELETE"])
head_route    = _http_route_factory(["HEAD"])
options_route = _http_route_factory(["OPTIONS"])

