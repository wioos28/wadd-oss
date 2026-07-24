# Python Async Programming

## async/await Basics

```python
import asyncio

async def say_hello():
    print("Hello")
    await asyncio.sleep(1)  # Non-blocking sleep
    print("World")

# Run async function
asyncio.run(say_hello())
```

## Coroutines

```python
# Coroutine function (async def)
async def fetch_data():
    return {"data": 123}

# Coroutine object
coro = fetch_data()
# Must be awaited or scheduled
result = await coro  # or asyncio.run(coro)
```

## Tasks

```python
async def task1():
    await asyncio.sleep(2)
    return "Task 1 done"

async def task2():
    await asyncio.sleep(1)
    return "Task 2 done"

async def main():
    # Run sequentially
    result1 = await task1()
    result2 = await task2()
    
    # Run concurrently
    task_a = asyncio.create_task(task1())
    task_b = asyncio.create_task(task2())
    result_a = await task_a
    result_b = await task_b

asyncio.run(main())
```

## Gather and Wait

```python
async def fetch(url):
    await asyncio.sleep(1)
    return f"Data from {url}"

async def main():
    urls = ["url1", "url2", "url3"]
    
    # gather - run all and wait for all
    results = await asyncio.gather(*[fetch(url) for url in urls])
    print(results)
    
    # wait - with timeout or return_when
    tasks = [fetch(url) for url in urls]
    done, pending = await asyncio.wait(tasks, timeout=2)

asyncio.run(main())
```

## Async Iterators

```python
class AsyncCounter:
    def __init__(self, stop):
        self.stop = stop
        self.current = 0
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.current >= self.stop:
            raise StopAsyncIteration
        await asyncio.sleep(0.1)
        self.current += 1
        return self.current

async def main():
    async for num in AsyncCounter(5):
        print(num)  # 1, 2, 3, 4, 5

# Async generator
async def async_range(n):
    for i in range(n):
        await asyncio.sleep(0.1)
        yield i

async def main():
    async for num in async_range(5):
        print(num)
```

## Async Context Managers

```python
class AsyncDatabase:
    async def __aenter__(self):
        print("Connecting...")
        await asyncio.sleep(1)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("Disconnecting...")
        await asyncio.sleep(1)
    
    async def query(self, sql):
        await asyncio.sleep(0.5)
        return f"Results for: {sql}"

async def main():
    async with AsyncDatabase() as db:
        result = await db.query("SELECT * FROM users")
        print(result)

asyncio.run(main())
```

## Async Libraries

```python
# aiohttp - async HTTP client/server
import aiohttp

async def fetch_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

# aiofiles - async file operations
import aiofiles

async def read_file(path):
    async with aiofiles.open(path, 'r') as f:
        content = await f.read()
        return content

async def write_file(path, content):
    async with aiofiles.open(path, 'w') as f:
        await f.write(content)

# asyncio.Queue for producer-consumer
async def producer(queue):
    for i in range(5):
        await asyncio.sleep(1)
        await queue.put(i)
        print(f"Produced {i}")

async def consumer(queue):
    while True:
        item = await queue.get()
        print(f"Consumed {item}")
        queue.task_done()

async def main():
    queue = asyncio.Queue()
    prod = asyncio.create_task(producer(queue))
    cons = asyncio.create_task(consumer(queue))
    await prod
    await queue.join()
    cons.cancel()
```

## Thread Pool and Process Pool

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# CPU-bound task
def cpu_intensive(n):
    return sum(i * i for i in range(n))

# IO-bound task
async def io_task():
    await asyncio.sleep(1)

async def main():
    loop = asyncio.get_event_loop()
    
    # Thread pool for IO-bound
    with ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, blocking_io_function)
    
    # Process pool for CPU-bound
    with ProcessPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, cpu_intensive, 1000000)
    
    # asyncio.to_thread (Python 3.9+)
    result = await asyncio.to_thread(blocking_io_function)

asyncio.run(main())
```

## Common Patterns

```python
# Rate limiting
class RateLimiter:
    def __init__(self, rate, period):
        self.rate = rate
        self.period = period
        self.tokens = rate
        self.last_refill = asyncio.get_event_loop().time()
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        async with self.lock:
            now = asyncio.get_event_loop().time()
            elapsed = now - self.last_refill
            self.tokens = min(self.rate, self.tokens + elapsed * self.rate / self.period)
            self.last_refill = now
            
            if self.tokens < 1:
                await asyncio.sleep(1)
                return await self.acquire()
            
            self.tokens -= 1

# Timeout
async def fetch_with_timeout(url, timeout):
    try:
        async with asyncio.timeout(timeout):
            return await fetch(url)
    except asyncio.TimeoutError:
        return None
```
