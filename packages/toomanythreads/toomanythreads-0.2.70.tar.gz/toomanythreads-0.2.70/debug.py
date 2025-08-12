import time
from fastapi import FastAPI, APIRouter

from toomanythreads import ThreadedServer

# if __name__ == "__main__":
    # t = ThreadedServer()
    # f = FastAPI()
    # @f.get("/")
    # def foobar():
    #     return "foobar"
    # t.mount("/app", f)
    # t.thread.start()
    # time.sleep(100)
if __name__ == "__main__":
    f = FastAPI()
    a = APIRouter()
    t = ThreadedServer()

    t.mount("/app", f)
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
    time.sleep(100)  # Let server start