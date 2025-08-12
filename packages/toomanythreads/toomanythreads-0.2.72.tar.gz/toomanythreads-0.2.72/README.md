# Managed Threads

A singleton-based thread management system with auto-registration, verbose logging, and dynamic mixin support.

## Quick Start

```python
from toomanythreads import ManagedThread, manager
import time

# Simple function to run in a thread
def worker_function(name, delay=1):
    for i in range(5):
        print(f"Worker {name}: iteration {i}")
        time.sleep(delay)

# Create and start a managed thread
thread = ManagedThread(worker_function)
thread.start()

# Check registered threads
print(f"Active threads: {len(manager.threads)}")

# Wait for completion
thread.join()
```

### ManagedThread

A decorator/factory function that creates managed threads. Can be used as a decorator.

**Parameters:**
- `obj`: Callable to run in the thread
- `*args`: Arguments to pass to the callable
- `**kwargs`: Keyword arguments to pass to the callable

**Returns:** Thread instance with management capabilities

## Requirements

- Python 3.8+
- loguru >= 0.6.0
- singleton-decorator >= 1.0.0

## License

MIT License - see LICENSE file for details.