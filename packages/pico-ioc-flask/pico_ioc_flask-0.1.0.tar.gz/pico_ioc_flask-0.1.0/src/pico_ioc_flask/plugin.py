# src/pico_ioc_flask/plugin.py
import inspect
import logging
from typing import Any, Dict, Optional, Tuple

from flask import Flask, Blueprint, Request, request as _request

from pico_ioc import Binder, PicoPlugin, create_instance, resolve_param


class FlaskPlugin:
    """
    Pico-IoC plugin that registers @controller classes and their annotated
    @get_route/@post_route/... methods as Flask routes.

    Requirements in the container:
      - A Flask application bound under key `Flask` (the class), or
      - A blueprint registry dict under key `flask_blueprints` if controllers
        target specific blueprints via blueprint="name".
    """

    def __init__(self, *, blueprint_registry_key: str = "flask_blueprints"):
        self._controllers: list[type] = []
        self._bp_registry_key = blueprint_registry_key

    # ---- Plugin hooks -----------------------------------------------------

    def visit_class(self, module: Any, cls: type, binder: Binder) -> None:
        """Collect controller classes during scan."""
        if getattr(cls, "_pico_rest_is_controller", False):
            self._controllers.append(cls)

    def after_bind(self, container, binder: Binder) -> None:
        """
        Once the core bound everything, create controllers and register
        their routes into the Flask app or requested Blueprints.
        """
        app: Optional[Flask] = None
        try:
            app = container.get(Flask)
        except Exception:
            app = None  # allowed if every controller targets a blueprint

        bp_registry: Optional[Dict[str, Blueprint]] = None
        if self._bp_registry_key and binder.has(self._bp_registry_key):
            bp_registry = binder.get(self._bp_registry_key)

        for ctl_cls in self._controllers:
            ctl = create_instance(ctl_cls, container)

            base_path: str = (getattr(ctl_cls, "_pico_rest_base_path", "") or "").rstrip("/")
            blueprint_name: Optional[str] = getattr(ctl_cls, "_pico_rest_blueprint", None)

            target = None
            if blueprint_name:
                if not bp_registry or blueprint_name not in bp_registry:
                    raise RuntimeError(
                        f"Blueprint '{blueprint_name}' not found in registry '{self._bp_registry_key}'."
                    )
                target = bp_registry[blueprint_name]
            else:
                if app is None:
                    raise RuntimeError(
                        "No Flask application bound and no blueprint specified in controller."
                    )
                target = app

            for meth_name, method in inspect.getmembers(ctl, predicate=inspect.ismethod):
                routes = getattr(method, "_pico_routes", None)
                if not routes:
                    continue

                sig = inspect.signature(method)

                def make_view(m=method, s=sig, ctl_name=ctl_cls.__name__):
                    def view_func(**urlvars):
                        kwargs: Dict[str, Any] = {}
                        for p in s.parameters.values():
                            if p.name == "self" or p.kind in (
                                inspect.Parameter.VAR_POSITIONAL,
                                inspect.Parameter.VAR_KEYWORD,
                            ):
                                continue

                            # URL variables from the rule
                            if p.name in urlvars:
                                kwargs[p.name] = urlvars[p.name]
                                continue

                            # Flask request injection by name or annotation
                            if p.name == "request" or p.annotation is Request:
                                kwargs[p.name] = _request
                                continue

                            # Resolve via Pico-IoC (name, type, MRO, str(name))
                            kwargs[p.name] = resolve_param(container, p)

                        return m(**kwargs)

                    # Unique-ish endpoint function name
                    view_func.__name__ = f"{ctl_name}_{m.__name__}"
                    view_func.__qualname__ = view_func.__name__
                    return view_func

                for r in routes:
                    rule = r["rule"]
                    if base_path:
                        # join base_path + rule preserving single slash
                        rule = f"{base_path}/{rule.lstrip('/')}"

                    methods = list(r["methods"])
                    extra = dict(r["kwargs"])

                    # Default endpoint: Controller_method (safe for Flask)
                    endpoint = extra.pop("endpoint", f"{ctl_cls.__name__}_{meth_name}")
                    if "." in endpoint:
                        # Flask forbids '.' in endpoint names; blueprints will add their own prefix.
                        endpoint = endpoint.replace(".", "_")

                    target.add_url_rule(
                        rule,
                        endpoint=endpoint,
                        view_func=make_view(),
                        methods=methods,
                        **extra,
                    )
                    logging.info("[pico-ioc-flask] %s %s -> %s", methods, rule, endpoint)

