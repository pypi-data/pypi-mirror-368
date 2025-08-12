import time
from fastapi import FastAPI, APIRouter
from loguru import logger as log

from toomanythreads import ThreadedServer

if __name__ == "__main__":
    f = FastAPI()
    a = APIRouter()
    t = ThreadedServer()
    t2 = ThreadedServer()
    def t2_repr(self):
        return "Nested Server"
    t2.__repr__ = t2_repr

    t.mount("/app", f)
    t.mount("/nested", t2)
    t.include_router(a)

    @t.get("/test")
    async def test_endpoint(name: str):
        return {"message": f"Hello {name}"}


    @t.get("/caller")
    async def caller():
        # Use in-memory forwarding
        result = await t.forward("test_endpoint", name="World")
        return {"forwarded": result}

    t.thread.start()
    log.debug(t.app_metadata)
    log.debug(f.app_metadata)
    log.debug(t2.app_metadata)
    log.debug(id(t))
    log.debug(id(t2))
    log.debug(id(t2.app_metadata.base_app))
    time.sleep(100)  # Let server start