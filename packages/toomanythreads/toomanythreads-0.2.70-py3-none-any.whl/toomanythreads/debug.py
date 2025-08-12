import time

from toomanythreads import ThreadedServer

app = ThreadedServer()

app.thread.start()
time.sleep(100)