<p align="center">
  <a href="http://feldroy.github.io/air/"><img src="https://raw.githubusercontent.com/feldroy/air/refs/heads/main/docs/img/logo-blue-369x369.png" alt="Air: The new web framework that breathes fresh air into Python web development. Built with FastAPI, Starlette, and Pydantic."></a>
</p>

<p align="center">
    <em>Air: The new web framework that breathes fresh air into Python web development. Built with FastAPI, Starlette, and Pydantic.</em>
</p>

<p align="center">
<a href="https://github.com/feldroy/air/actions?query=workflow%3Apython-package+event%3Apush+branch%main" target="_blank">
    <img src="https://github.com/feldroy/air/actions/workflows/python-package.yml/badge.svg?event=push&branch=main" alt="Test">
</a>
<a href="https://pypi.org/project/air" target="_blank">
    <img src="https://img.shields.io/pypi/v/air?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<a href="https://pypi.org/project/air" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/air.svg?color=%2334D058" alt="Supported Python versions">
</a>
</p>
<p align="center">
        <a href="https://discord.gg/aTzWBVrtEs">
        <img src="https://img.shields.io/discord/1388403469505007696?logo=discord"
            alt="Chat on Discord"></a>
</p>

> [!CAUTION]
> Air is currently in an alpha state. While breaking changes are becoming less common, nevertheless, anything and everything could change.


> [!IMPORTANT]
> If you have an idea for a new feature, discuss it with us by opening an issue before writing any code. Do understand that we are working to remove features from core, and for new features you will almost always create your own package that extends or uses Air instead of adding to this package. This is by design, as our vision is for the Air package ecosystem to be as much a "core" part of Air as the code in this minimalist base package.

## Why use Air?


- **Powered by FastAPI** - Designed to work with FastAPI so you can serve your API and web pages from one app
- **Fast to code** - Tons of intuitive shortcuts and optimizations designed to expedite coding HTML with FastAPI
- **Air Tags** - Easy to write and performant HTML content generation using Python classes to render HTML
- **Jinja Friendly** - No need to write `response_class=HtmlResponse` and `templates.TemplateResponse` for every HTML view
- **Mix Jinja and Air Tags** - Jinja and Air Tags both are first class citizens. Use either or both in the same view!
- **HTMX friendly** - We love HTMX and provide utilities to use it with Air
- **HTML form validation powered by pydantic** - We love using pydantic to validate incoming data. Air Forms provide two ways to use pydantic with HTML forms (dependency injection or from within views)
- **Easy to learn yet well documented** - Hopefully Air is so intuitive and well-typed you'll barely need to use the documentation. In case you do need to look something up we're taking our experience writing technical books and using it to make documentation worth boasting about

---

**Documentation**: <a href="https://feldroy.github.io/air/" target="_blank">https://feldroy.github.io/air/</a>

**Source Code**: <a href="https://github.com/feldroy/air" target="_blank">https://github.com/feldroy/air</a>


## Installation

Install using `pip install -U air` or `conda install air -c conda-forge`.

For `uv` users, just create a virtualenv and install the air package, like:

```sh
uv venv
source .venv/bin/activate
uv add air
uv add "fastapi[standard]"
```

## A Simple Example

Create a `main.py` with:

```python
import air

app = air.Air()


@app.get("/")
async def index():
    return air.Html(air.H1("Hello, world!", style="color: blue;"))
```

Run the app with:

```sh
fastapi dev
```

> [!NOTE]
> This example uses Air Tags, which are Python classes that render as HTML. Air Tags are typed and documented, designed to work well with any code completion tool.
> You can also run this with `uv run uvicorn main:app --reload` if you prefer using Uvicorn directly.

Then open your browser to <http://127.0.0.1:8000> to see the result.

## Combining FastAPI and Air

Air is just a layer over FastAPI. So it is trivial to combine sophisticated HTML pages and a REST API into one app. 

```python
import air
from fastapi import FastAPI

app = air.Air()
api = FastAPI()

@app.get("/")
def landing_page():
    return air.Html(
        air.Head(air.Title("Awesome SaaS")),
        air.Body(
            air.H1("Awesome SaaS"),
            air.P(air.A("API Docs", target="_blank", href="/api/docs")),
        ),
    )


@api.get("/")
def api_root():
    return {"message": "Awesome SaaS is powered by FastAPI"}

# Combining the Air and and FastAPI apps into one
app.mount("/api", api)
```

## Combining FastAPI and Air using Jinja2

Want to use Jinja2 instead of Air Tags? We've got you covered.

```python
import air
from air.requests import Request
from fastapi import FastAPI

app = air.Air()
api = FastAPI()

# Air's JinjaRenderer is a shortcut for using Jinja templates
jinja = air.JinjaRenderer(directory="templates")

@app.get("/")
def index(request: Request):
    return jinja(request, name="home.html")

@api.get("/")
def api_root():
    return {"message": "Awesome SaaS is powered by FastAPI"}

# Combining the Air and and FastAPI apps into one
app.mount("/api", api)    
```

Don't forget the Jinja template!

```html
<!doctype html
<html>
    <head>
        <title>Awesome SaaS</title>
    </head>
    <body>
        <h1>Awesome SaaS</h1>
        <p>
            <a target="_blank" href="/api/docs">API Docs</a>
        </p>
    </body>
</html>
```

> [!NOTE]
> Using Jinja with Air is easier than with FastAPI. That's because as much as we enjoy Air Tags, we also love Jinja!

## Contributing

For guidance on setting up a development environment and how to make a contribution to Air, see [Contributing to Air](https://github.com/feldroy/air/blob/main/CONTRIBUTING.md).
