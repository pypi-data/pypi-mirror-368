from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ._handlers import health_handler


def create_app(
    *,
    enable_docs: bool,
    **kwargs,
) -> FastAPI:
    if enable_docs:
        app = FastAPI(
            redirect_slashes=False,
            **kwargs,
        )
    else:
        app = FastAPI(
            redirect_slashes=False,
            docs_url=None,
            redoc_url=None,
            openapi_url=None,
            **kwargs,
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    app.add_api_route('/health', health_handler)

    return app
