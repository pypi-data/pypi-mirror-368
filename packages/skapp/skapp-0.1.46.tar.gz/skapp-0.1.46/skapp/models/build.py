import os
import subprocess
import tempfile
from typing import Optional

from pydantic import BaseModel

# import docker
from python_on_whales import docker
from rich import print


class ImageBuild(BaseModel):
    prefix: str = "docker.io"
    push: bool = True
    pull: bool = False
    name: str
    context: str = "./"
    dockerfile: str = "Dockerfile"
    tag: Optional[str] = None
    image: Optional[str] = None
    platforms: list[str] = os.getenv(
        "BUILD_PLATFORMS",
        "linux/arm64" if "arm64" in os.uname().machine else "linux/amd64",
    ).split(",")
    target: Optional[str] = None
    md5version: Optional[list[str]] = []
    dependencies: Optional[list[str]] = []

    def get_md5version(self):
        import hashlib

        m = hashlib.md5()

        content = []
        for verfile in self.md5version:
            with open(verfile, "r") as f:
                content.append(f.read())

        m.update("".join(content).encode("utf-8"))
        return m.hexdigest()

    def build(
        self,
        client: "docker.DockerClient",
        image_version: str,
        deps: list["ImageBuild"] = [],
    ) -> str:
        # Use docker-py to build the image
        separator = ":" if ":" not in self.prefix else "-"

        if self.md5version:
            image_version = self.get_md5version()

        platform = self.platforms[0]

        self.tag = f"{self.prefix}{separator}{self.name}-{image_version}-{platform.replace('/', '-')}"

        exists = False
        # if self.md5version:
        try:
            client.images.get_registry_data(self.tag)
        except Exception as e:
            print(e)
            exists = False
        else:
            exists = True

        if exists:
            print(f"Image {self.tag} already exists")
        else:
            print(
                f"Building {self.name} as {self.tag} with dockerfile {self.dockerfile} in {self.context}"
            )

            dockerfile_path = self.dockerfile
            if self.dependencies:
                # Generate tempfile
                dockerfile_path = tempfile.mktemp()

                with open(self.dockerfile, "r") as f:
                    content = f.read()
                    print(deps, self.dependencies)
                    content = content.format(**{dep.name: dep.tag for dep in deps})
                    with open(dockerfile_path, "w") as f:
                        f.write(content)

            docker_command = [
                "docker",
                "buildx",
                "build",
                "--platform",
                ",".join(self.platforms),
                "-t",
                self.tag,
                self.context,
                "-f",
                dockerfile_path,
                "--push" if self.push else "--load",
            ]

            if self.target is not None:
                docker_command.extend(["--target", self.target])

            print(" ".join(docker_command))
            process = subprocess.Popen(
                docker_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )

            # Stream and print the output
            for line in process.stdout:
                print(line, end="")

            # Get the return code, if non-zero, raise an exception
            process.wait()
            if process.returncode != 0:
                raise Exception(f"Failed to build image {self.name}")

    @classmethod
    def new(cls, **config) -> "ImageBuild":
        return cls(**config)


class Builds(list[ImageBuild]):
    item_class = ImageBuild
