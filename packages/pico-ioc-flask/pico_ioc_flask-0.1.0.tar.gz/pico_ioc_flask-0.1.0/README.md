# 🌐 Pico-IoC Flask Extension

[![PyPI](https://img.shields.io/pypi/v/pico-ioc-flask.svg)](https://pypi.org/project/pico-ioc-flask/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
![CI (tox matrix)](https://github.com/dperezcabrera/pico-ioc-flask/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/dperezcabrera/pico-ioc-flask/branch/main/graph/badge.svg)](https://codecov.io/gh/dperezcabrera/pico-ioc-flask)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=dperezcabrera_pico-ioc-flask&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=dperezcabrera_pico-ioc-flask)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=dperezcabrera_pico-ioc-flask&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=dperezcabrera_pico-ioc-flask)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=dperezcabrera_pico-ioc-flask&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=dperezcabrera_pico-ioc-flask)

**Pico-IoC Flask** is an optional plugin for [Pico-IoC](https://pypi.org/project/pico-ioc/) that provides **automatic controller discovery and route registration** for Flask applications.
It allows you to build **loosely-coupled, testable Flask apps** without manually wiring routes or blueprints.

---

## ✨ Key Features

* **Automatic controller registration** — detect `@controller` classes and register all annotated routes.
* **Dependency injection in handlers** — request objects, services, and other components injected automatically.
* **Blueprint support** — register controllers into existing or DI-provided blueprints.
* **HTTP method decorators** — `@get_route`, `@post_route`, `@put_route`, `@delete_route`, etc.
* **Zero dependencies** — only requires Flask and Pico-IoC.
* **Extensible** — built as a standard Pico-IoC plugin.

---

## 📦 Installation

```bash
pip install pico-ioc-flask
```

Requires:

* **pico-ioc >= 0.4.0**
* **Flask >= 2.0, < 4.0** (tested with Flask 2.x and 3.x)

---

## 🚀 Quick Start

```python
from flask import Flask, jsonify, Request
from pico_ioc import component, init
from pico_ioc_flask import controller, get_route, post_route, FlaskPlugin

@component
class AppConfig:
    message = "Hello from Pico-IoC Flask!"

@controller(base_path="/api/v1")
class MyController:
    @get_route("/ping")
    def ping(self):
        return jsonify(pong=True)

    @post_route("/echo/<name>")
    def echo(self, request: Request, name: str):
        return jsonify(name=name)

# Bootstrap container + Flask
container = init(__name__, plugins=(FlaskPlugin(),))
app = container.get(Flask)

if __name__ == "__main__":
    app.run(debug=True)
```

---

## 🧩 Route Decorators

Pico-IoC Flask provides HTTP method decorators for clean route definitions:

```python
from pico_ioc_flask import get_route, post_route, put_route, delete_route

@get_route("/status", endpoint="status_check")
def status(self):
    return {"ok": True}
```

**Available decorators:**

* `@get_route`
* `@post_route`
* `@put_route`
* `@delete_route`
* `@patch_route`

All decorators accept:

* `path`: relative route path
* `endpoint`: optional Flask endpoint name
* `**kwargs`: passed to `add_url_rule` (e.g., `strict_slashes=False`)

---

## 📜 Controllers

Controllers are regular classes marked with `@controller`:

```python
from pico_ioc_flask import controller

@controller(base_path="/api")
class MyAPI:
    @get_route("/items")
    def list_items(self, service: "ItemService"):
        return service.get_all()
```

**Options:**

* `base_path`: prefix for all routes in this controller
* `blueprint`: optional blueprint name (must be a DI-provided `Blueprint`)

---

## 🧠 Dependency Injection in Handlers

Handler method parameters are resolved using Pico-IoC’s **parameter name → type → MRO → string name** resolution order.
You can inject:

* Components from Pico-IoC
* Flask request objects (`flask.Request`)
* Any other resolvable dependency

Example:

```python
from flask import Request

@post_route("/save")
def save_item(self, request: Request, repo: "ItemRepository"):
    data = request.get_json()
    repo.save(data)
    return {"saved": True}
```

---

## 🏗️ Using Blueprints

You can inject a `Blueprint` as a Pico-IoC component and map controllers to it:

```python
from flask import Blueprint
from pico_ioc import component

@component(name="flask_blueprints")
class Blueprints(dict):
    def __init__(self):
        super().__init__()
        self["api"] = Blueprint("api", __name__)
```

Then register the blueprint in your app:

```python
app.register_blueprint(container.get("flask_blueprints")["api"], url_prefix="/bp")
```

---

## 🧪 Testing

Install test dependencies:

```bash
pip install pytest tox
```

Run the full matrix:

```bash
tox
```

Run with a specific Python/Flask version:

```bash
tox -e py311-flask3
```

---

## 🔌 Plugin Lifecycle

The **FlaskPlugin** integrates into Pico-IoC’s plugin API:

1. **visit\_class** — detects controllers and stores them for later binding.
2. **after\_bind** — resolves Flask/Blueprint instances and registers controller routes.
3. **before\_eager** — all controllers are bound before other eager components.

---

## ❓ FAQ

**Q: Can I mix FlaskPlugin with other plugins?**
A: Yes, plugins are executed in the order passed to `init()`.

**Q: Do I need to manually instantiate controllers?**
A: No, they are created by the plugin via Pico-IoC DI.

**Q: Can I use Flask 4?**
A: Not yet — the extension is tested only up to Flask 3.x.

---

## 📜 License

MIT — see [LICENSE](https://opensource.org/licenses/MIT)

