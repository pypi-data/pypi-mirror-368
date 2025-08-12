import os
from shutil import rmtree
from typing import List, Optional

import docker
import typer
from dotenv import load_dotenv
from rich import print

from skapp.models.stack import Stack, load_plugins
from skapp.utils import load_yaml_files

app = typer.Typer()


@app.command()
def version():
    pass


def parse_values(value):
    obj = {}

    for val in value:
        if "=" in val:
            key, v = val.split("=", 1)
        else:
            key, v = val, True

        if "." in key:
            _parent = obj
            while "." in key:
                el, key = key.split(".", 1)
                if el not in _parent:
                    _parent[el] = {}
                _parent = _parent[el]

            _parent[key] = v

        else:
            obj[key] = v

    return obj


@app.command()
def rollout(
    name: str,
    configs: Optional[List[str]] = typer.Option(None),
    value: Optional[List[str]] = typer.Option(None),
    namespace: str = typer.Option(None),
    create_namespace: bool = typer.Option(False),
    environment: Optional[str] = typer.Option("dev"),
    build: bool = typer.Option(False),
    dotenv: Optional[str] = typer.Option(None),
) -> None:
    if dotenv:
        load_dotenv(dotenv)

    values = parse_values(value)
    stack = Stack.from_files(
        name=name, environment=environment, files=configs, values=values
    )
    if build:
        build_images(stack)
    stack.chart.rollout(namespace=namespace, create_namespace=create_namespace)


@app.command()
def generate_chart(
    name: str,
    location: str,
    configs: Optional[List[str]] = typer.Option(None),
    namespace: str = typer.Option(None),
    environment: Optional[str] = typer.Option("dev"),
    build: bool = typer.Option(False),
    dotenv: Optional[str] = typer.Option(None),
    version: Optional[str] = typer.Option(None),
    app_version: Optional[str] = typer.Option(None),
) -> None:
    if dotenv:
        load_dotenv(dotenv)

    stack = Stack.from_files(
        name=name,
        environment=environment,
        files=configs,
        version=version,
        app_version=app_version,
    )
    if build:
        build_images(stack)

    if os.path.exists(location):
        os.removedirs(location)

    os.makedirs(location)
    stack.chart.dump(
        location,
        namespace=namespace,
    )


def get_image_deps(img, images):
    deps = []
    for dep in img.dependencies:
        if dep in images:
            deps.append(images[dep])
            deps.extend(get_image_deps(images[dep], images))

    return deps


def build_images(stack: Stack, image: Optional[str] = None):
    if len(stack.build) == 0:
        return

    import datetime

    image_version = os.getenv("BUILD_VERSION") or datetime.datetime.now().strftime(
        "%Y%m%d%H%M%S"
    )
    client = docker.from_env()

    built_images = []

    images = {_.name: _ for _ in stack.build}

    while True:
        for img in images.values():
            if img.name in built_images:
                continue

            if image is not None and img.name != image:
                continue

            print(f"Building {img.name}")

            deps = get_image_deps(img, images)

            if not set(built_images).issuperset({_.name for _ in deps}):
                # print(f"Dependencies for {img.name} are not yet ready")
                continue

            img.build(client=client, image_version=image_version, deps=deps)

            built_images.append(img.name)

        if len(images) == len(built_images):
            break


@app.command()
def build(
    name: str,
    image: str = None,
    configs: Optional[List[str]] = typer.Option(None),
    value: Optional[List[str]] = typer.Option(None),
    namespace: str = typer.Option(None),
    environment: Optional[str] = typer.Option("dev"),
) -> None:
    values = parse_values(value)
    stack = Stack.from_files(
        name=name, environment=environment, files=configs, values=values
    )
    build_images(stack, image=image)


if __name__ == "__main__":
    app()
