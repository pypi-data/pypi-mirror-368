__version__ = "0.2.5"


from fastapi import FastAPI


def setup(app: FastAPI) -> None:
    try:
        from fastapi_extra import routing as native_routing  # type: ignore

        native_routing.install(app)
    except ImportError:  # pragma: nocover
        pass
