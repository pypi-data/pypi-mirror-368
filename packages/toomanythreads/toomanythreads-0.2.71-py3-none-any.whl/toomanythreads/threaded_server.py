import threading
import time
import traceback
import uuid
from dataclasses import dataclass, field
from functools import cached_property
from types import SimpleNamespace
from typing import Any

import uvicorn
from fastapi import FastAPI, APIRouter
from loguru import logger as log
from starlette.requests import Request
from starlette.responses import Response
from toomanyports import PortManager

from toomanythreads import ManagedThread

DEBUG = True


@dataclass
class AppMetadata:
    url: str | None
    rel_path: str
    app: Any
    name: str
    base_app: Any = None
    app_type: str = "base_app"
    is_parent_of: list = field(default_factory=list)
    is_child_of: list = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    request_count: int = 0
    error_count: int = 0

    @property
    def uptime(self) -> float:
        return time.time() - self.started_at

    @property
    def request_to_error_ratio(self):
        return self.error_count / self.request_count


class ThreadedServer(FastAPI):
    app_metadata: AppMetadata

    def __init__(
            self,
            host: str = "localhost",
            port: int = PortManager.random_port(),
            verbose: bool = DEBUG,
    ) -> None:
        self.verbose = verbose
        self.host = host
        self.port = port
        PortManager.kill(self.port, force=True)
        super().__init__(debug=self.verbose)
        if not getattr(self, "app_metadata", None):
            self.app_metadata = AppMetadata(
                url=self.url,
                rel_path="",
                app=self,
                name=self.__class__.__name__,
                base_app=self
            )
        if self.verbose: log.success(
            f"{self}: Initialized successfully!\n  - host={self.host}\n  - port={self.port}  - verbose={self.verbose}")

        @self.middleware("http")
        async def request_log(request: Request, call_next):
            self.app_metadata.request_count = self.app_metadata.request_count + 1
            if self.verbose: log.info(f"{self}: Received request to '{request.url.path}'"
                                      f"\n  - client={request.client}"
                                      f"\n  - cookies={request.cookies}"
                                      )
            try:
                return await call_next(request)
            except Exception as e:
                tb_str = traceback.format_exc()
                log.error(f"Request failed: {e}\n{tb_str}")

                self.app_metadata.error_count += 1
                return Response(e, 500)

    def __repr__(self):
        return f"[{self.__class__.__name__}]"

    def mount(self, rel_path: str, app: Any, name: str = None):
        if self.verbose: log.debug(f"{self}: Attempting to mount an application to {self}!")
        if not name: name = rel_path[1:].replace("/", "_")

        super().mount(rel_path, app, name)

        mounter = self
        mounted = app
        mounter.app_metadata.is_child_of.append(mounted)
        if not getattr(mounted, "app_metadata", None):
            metadata = AppMetadata(
                url=mounter.url + rel_path,
                rel_path=rel_path,
                app=mounted,
                name=name,
                base_app=mounter,
                app_type="mount",
                is_child_of=[mounter]
            )
            setattr(mounted, "app_metadata", metadata)
        else:
            mounted.app_metadata.url = mounter.app_metadata.url + rel_path
            mounted.app_metadata.rel_path = rel_path,
            mounted.app_metadata.base_app = self
            mounted.app_metadata.is_child_of.append(mounter)

        if self.verbose: log.success(f"{self}: Successfully mounted {name}!\n  - metadata={mounted.app_metadata}")

    def include_router(self, router: APIRouter, prefix: str = None, **kwargs):
        if self.verbose: log.debug(f"{self}: Attempting to include an APIRouter to {self}!")
        if prefix:
            name = prefix[1:].replace("/", "_")
        else:
            prefix = ""
            name = f"{router.__class__.__name__}"
            if name == "APIRouter": name = f"{name}.{str(uuid.uuid1())}"
        super().include_router(router, prefix=prefix, **kwargs)


        mounter = self
        mounted = router
        mounter.app_metadata.is_child_of.append(mounted)
        if not getattr(mounted, "app_metadata", None):
            metadata = AppMetadata(
                url=mounter.url + prefix,
                rel_path=prefix,
                app=mounted,
                name=name,
                base_app=mounter,
                app_type="mount",
                is_child_of=[mounter]
            )
            setattr(mounted, "app_metadata", metadata)
        else:
            mounted.app_metadata.url = mounter.app_metadata.url + prefix
            mounted.app_metadata.rel_path = prefix,
            mounted.app_metadata.base_app = self
            mounted.app_metadata.is_child_of.append(mounter)

        if self.verbose: log.success(f"{self}: Successfully mounted {name}!\n  - metadata={mounted.app_metadata}")

    @cached_property
    def url(self):
        if not getattr(self, "app_metadata.url", None):
            return f"http://{self.host}:{self.port}"
        else:
            return self.app_metadata.url

    @cached_property
    def uvicorn_cfg(self) -> uvicorn.Config:
        return uvicorn.Config(
            app=self,
            host=self.host,
            port=self.port,
        )

    @cached_property
    def thread(self) -> threading.Thread:  # type: ignore
        def proc(self):
            if self.verbose: log.info(f"{self}: Launching threaded server on {self.host}:{self.port}")
            server = uvicorn.Server(config=self.uvicorn_cfg)
            server.run()

        return ManagedThread(proc, self)

    async def forward(self, endpoint_path: str, request: Request = None, **params):
        """Forward to an endpoint via memory using dot notation (e.g., 'auth.login')"""
        # Split "auth.login" into ["auth", "login"]
        path_parts = endpoint_path.split('.')

        # Navigate the nested structure
        current = self.endpoints
        for part in path_parts:
            if hasattr(current, part):
                current = getattr(current, part)
            else:
                raise AttributeError(f"Endpoint path '{endpoint_path}' not found")

        # Current should now be the actual endpoint function
        if not callable(current):
            raise AttributeError(f"'{endpoint_path}' is not a callable endpoint")

        # Add request to params if provided
        if request:
            params['request'] = request

        # Handle both async and sync endpoints
        import asyncio
        if asyncio.iscoroutinefunction(current):
            return await current(**params)
        else:
            return current(**params)

    @property
    def endpoints(self):
        ns = SimpleNamespace()
        for route in self.routes:
            if hasattr(route, 'endpoint') and hasattr(route.endpoint, '__name__'):
                # Split path into parts: "/auth/login" -> ["auth", "login"]
                path_parts = [p for p in route.path.split('/') if p and '{' not in p]

                # Build nested structure
                current = ns
                for part in path_parts[:-1]:  # All but last part
                    if not hasattr(current, part):
                        setattr(current, part, SimpleNamespace())
                    current = getattr(current, part)

                # Set the endpoint on the final part
                if path_parts:
                    setattr(current, path_parts[-1], route.endpoint)
                else:
                    setattr(current, 'root', route.endpoint)

        return ns