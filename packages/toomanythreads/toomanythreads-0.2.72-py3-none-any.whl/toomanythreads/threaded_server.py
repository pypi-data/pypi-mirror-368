import asyncio
import re
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
from starlette.exceptions import HTTPException
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

    async def forward(self, path: str, request: Request = None, **params):
        """Forward to an endpoint via memory using dot notation (e.g., 'auth.login')"""
        log.debug(f"{self}: Received forwarding request for '{path}'!")
        endpoints = self.endpoints
        index = endpoints.as_dict
        log.debug(index)
        if path in index:
            try:
                current = index.get(path)
                if not callable(current): raise AttributeError(f"'{path}' is not a callable endpoint")
                log.debug(f"{self}: Found method '{current}' at '{path}'!")
            except Exception as e:
                return HTTPException(404, e)

        async def attempt():
            log.info(f"{self}: Attempting to call {current} with params:")
            if request: params['request'] = request
            for each in params.items():
                print(f"  - {each}={params.get(each)}")
            attempts = 0
            while attempts < 3:
                log.debug(f"{self}: Trying attempt '{attempts + 1}' for {current}...")
                try:
                    try:
                        if asyncio.iscoroutinefunction(current):
                            return await current(**params)
                        else:
                            return current(**params)
                    except TypeError as e:
                        log.error(f"{self}: Attempt failed!\n{e}")
                        if "got an unexpected keyword argument" in str(e):
                            pattern = r"'([^']+)'"
                            bad_kw = re.search(pattern, str(e))
                            if bad_kw:
                                bad_param = bad_kw.group(1)
                                log.warning(f"{self}: Removing bad keyword, '{bad_param}'")
                                del params[bad_param]
                            raise
                except Exception as e:
                    log.error(f"{self}: Failed attempt '{attempts + 1}'")
                    attempts = attempts + 1
                    if attempts == 3: raise Exception(e)

        return await attempt()

    @property
    def endpoints(self):
        ns = SimpleNamespace()
        flat_dict = {}

        for route in self.routes:
            if hasattr(route, 'endpoint') and hasattr(route.endpoint, '__name__'):
                flat_dict[route.path] = route.endpoint
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

        setattr(ns, "as_dict", flat_dict)
        return ns
