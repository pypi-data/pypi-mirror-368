from typing import Generator, Optional

from pydantic import BaseModel

from skapp.utils import LazyString, dict_to_yaml


class Base(BaseModel):
    def generate(self, namespace: str = None) -> Generator:
        raise NotImplementedError()


class YamlMixin:
    def generate(self, namespace: str = None) -> Generator:
        raise NotImplementedError()

    def yaml_files(self, context: dict = None, namespace: str = None) -> Generator:

        for el in self.generate(namespace=namespace):
            filename = "{}.yml".format(
                "-".join([el["kind"].lower(), el["metadata"]["name"]])
            )
            # try:
            # print(el)
            filename = LazyString(filename).render(context)
            formatted = dict_to_yaml(el, context=context)
            yield filename, formatted
            # except Exception as e:
            #     print(e)
            #     breakpoint()
            #     raise e

    def to_yaml(self, context: dict = None, namespace: str = None) -> str:
        return "---\n".join(
            content
            for file, content in self.yaml_files(context=context, namespace=namespace)
        )
