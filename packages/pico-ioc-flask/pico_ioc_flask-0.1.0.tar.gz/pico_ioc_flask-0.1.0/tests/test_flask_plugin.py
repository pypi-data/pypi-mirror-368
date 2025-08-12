import sys
import pytest

from pico_ioc import init, component
from pico_ioc_flask import controller, get_route, post_route, FlaskPlugin


@pytest.fixture
def demo_pkg(tmp_path):
    import pico_ioc
    pico_ioc._container = None

    root = tmp_path / "demo"
    (root / "web").mkdir(parents=True)

    sys.path.insert(0, str(tmp_path))
    (root / "__init__.py").write_text("")
    (root / "web" / "__init__.py").write_text("")

    (root / "web" / "components.py").write_text(
        """
from pico_ioc import component
from flask import Flask, Blueprint

@component(name=Flask)
class App(Flask):
    def __init__(self):
        super().__init__(__name__)

@component(name="flask_blueprints")
class BPRegistry(dict):
    def __init__(self):
        super().__init__()
        self["api"] = Blueprint("api", __name__)
"""
    )

    (root / "web" / "controllers.py").write_text(
        """
from flask import jsonify, Request
from pico_ioc_flask import controller, get_route, post_route

@controller(base_path="/api/v1")
class AppController:
    @get_route("/health", endpoint="app_health")
    def health(self):
        return jsonify(ok=True)

    @get_route("/add/<int:a>/<int:b>", strict_slashes=False)
    def add(self, a: int, b: int):
        return jsonify(sum=a+b)

    @post_route("/echo/<name>")
    def echo(self, request: Request, name: str):
        data = request.get_json(silent=True) or {}
        return jsonify(name=name, payload=data)

@controller(base_path="/v2", blueprint="api")
class BPController:
    @get_route("/ping", endpoint="ping")
    def ping(self):
        return jsonify(pong=True)
"""
    )

    yield "demo"

    # teardown
    sys.path.remove(str(tmp_path))
    pico_ioc._container = None
    for m in [m for m in list(sys.modules) if m == "demo" or m.startswith("demo.")]:
        sys.modules.pop(m, None)


def _init_ioc(pkg_name):
    pkg = __import__(pkg_name)
    return init(pkg, plugins=(FlaskPlugin(),))


def test_registers_routes_on_app(demo_pkg):
    ioc = _init_ioc(demo_pkg)
    from flask import Flask
    app = ioc.get(Flask)
    client = app.test_client()

    r = client.get("/api/v1/health")
    assert r.status_code == 200 and r.json == {"ok": True}

    r1 = client.get("/api/v1/add/2/5")
    r2 = client.get("/api/v1/add/2/5/")
    assert r1.status_code == 200 and r1.json == {"sum": 7}
    assert r2.status_code == 200 and r2.json == {"sum": 7}

    r = client.post("/api/v1/health")
    assert r.status_code == 405

    assert "app_health" in app.view_functions


def test_registers_routes_on_blueprint_and_uses_request_injection(demo_pkg):
    ioc = _init_ioc(demo_pkg)
    from flask import Flask
    app = ioc.get(Flask)

    bps = ioc.get("flask_blueprints")
    app.register_blueprint(bps["api"], url_prefix="/bp")

    client = app.test_client()

    r = client.get("/bp/v2/ping")
    assert r.status_code == 200 and r.json == {"pong": True}

    r = client.post("/api/v1/echo/Ada", json={"x": 1})
    assert r.status_code == 200 and r.json == {"name": "Ada", "payload": {"x": 1}}

    # Flask añade el prefijo "api." al endpoint del blueprint
    assert "api.ping" in app.view_functions

