
---

````markdown
# twill_throttle

A Python module providing **rate-limiting decorators** for synchronous and asynchronous functions.  
Includes two main classes:

- **`FuncPerMin`** – Limits the number of calls to a single function per minute.
- **`SharedRateLimiter`** – A shared rate limiter across multiple functions, supporting both sync and async.

---

## Features

- Per-function call limiting (`FuncPerMin`)
- Shared call limiting across multiple functions (`SharedRateLimiter`)
- Support for synchronous and asynchronous functions
- Sliding window rate limiting for precise control
- Thread-safe and async-safe locking
- Easy to integrate with any existing function or coroutine

---

## Installation

```bash
pip install twill_throttle
````

Or just copy the module file into your project.

---

## Usage

### Example 1 – Per-function limit

```python
from twill_throttle import FuncPerMin

@FuncPerMin(max_calls_per_minute=3)
def greet(name):
    print(f"Hello, {name}!")

for i in range(5):
    greet(f"User {i+1}")  # Last two calls will wait until the next minute
```

---

### Example 2 – Shared limit across multiple functions

```python
import asyncio
from twill_throttle import SharedRateLimiter

shared_limiter = SharedRateLimiter(max_calls_per_minute=4)

@shared_limiter
def process_data(data):
    print(f"Processing data: {data}")

@shared_limiter
async def async_task(task_id):
    print(f"Starting async task {task_id}...")
    await asyncio.sleep(0.5)
    print(f"Finished async task {task_id}.")

async def main():
    process_data("File1")
    process_data("File2")
    await asyncio.gather(
        async_task(1),
        async_task(2),
        async_task(3)
    )

asyncio.run(main())
```

---

## API Reference

### `FuncPerMin(max_calls_per_minute: int)`

Limits calls per minute for **one specific function**.

* **Parameters:**

  * `max_calls_per_minute` *(int)* – Maximum allowed calls per minute.
* **Behavior:**

  * Resets counter after 60 seconds from the first call.
  * If the limit is reached, blocks execution until the minute resets.

---

### `SharedRateLimiter(max_calls_per_minute: int)`

Limits calls per minute **shared** across multiple functions (sync & async).

* **Parameters:**

  * `max_calls_per_minute` *(int)* – Maximum allowed calls per minute.
* **Behavior:**

  * Uses a sliding time window for precision.
  * Waits until enough time passes before allowing a new call.
  * Works for both synchronous and asynchronous functions.

---

## Best Practices

* Use **`FuncPerMin`** when you only need to limit one specific function.
* Use **`SharedRateLimiter`** when multiple functions should share the same limit.
* Be aware that both limiters **block execution** until the limit resets.
  In async contexts, `SharedRateLimiter` will use non-blocking `asyncio.sleep()`.

---

## License

MIT License – You are free to use, modify, and distribute this code.

---






