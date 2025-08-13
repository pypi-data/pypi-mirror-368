__author__ = "ziyan.yin"
__describe__ = ""

from typing import Any

from fastapi import FastAPI

class RouteNode:
    def add_route(self, fullpath: str, handler: Any): ...

def install(app: FastAPI) -> None: ...
