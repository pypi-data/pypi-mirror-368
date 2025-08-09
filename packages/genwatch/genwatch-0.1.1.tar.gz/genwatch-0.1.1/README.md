# genwatch

Tiny, surgical **observability for classic Python generators**.

`genwatch` wraps a generator function and emits **structured JSON logs** for the core lifecycle only. By design:

- In `_ProxyReporter.__iter__` **every event logs at `INFO`**.
- **Only** when an unexpected exception escapes the generator do we log at `ERROR` (and re-raise).
- No `DEBUG`, no `WARNING`, no `CRITICAL` inside `__iter__`.

This keeps the noise floor flat and makes logs deterministic and cheap.

---

## Install

```bash
pip install genwatch
```

Python 3.10+.

---

## Why this exists

- You want the **return value** from a generator (`StopIteration.value`) visible in logs.
- You need to **trace delegation** (`yield from`) without global tracing hooks.
- You prefer **stable, assertion-friendly logs** over verbose, level-juggling traces.
- You want a one-line decorator that works on **functions and methods**.

---

## Quick start

```python
import logging
from genwatch import GeneratorReporter
from genwatch._logger import JSONFormatter  # optional

# Minimal JSON logger
logger = logging.getLogger("genwatch.demo")
logger.setLevel(logging.INFO)
h = logging.StreamHandler()
h.setFormatter(JSONFormatter())
logger.addHandler(h)

@GeneratorReporter(logger=logger)
def demo(n):
    for i in range(n):
        received = (yield i)  # you can .send(...) into this if you want
    return "done"

g = demo(2)
next(g)            # -> 0
g.send(None)       # -> 1
try:
    next(g)        # StopIteration with value "done"
except StopIteration as e:
    assert e.value == "done"
```

Sample output (with `JSONFormatter`):

```json
{"timestamp":"2025-08-09T19:00:00.123456","level":"INFO","filename":"example.py","lineno":12,"msg":"[genwatch] start demo"}
{"timestamp":"2025-08-09T19:00:00.124000","level":"INFO","filename":"example.py","lineno":12,"msg":"[genwatch] done demo → return 'done'"}
{"timestamp":"2025-08-09T19:00:00.124100","level":"INFO","filename":"example.py","lineno":12,"msg":"[genwatch] closed demo"}
```

If an unexpected exception escapes, you’ll additionally see one `ERROR` log before it’s re-raised.

---

## Practical examples

### 1) Function — streaming CSV parser

Parses a CSV stream row-by-row (nice for big files). Returns the total rows parsed.

```python
import io
import csv
import logging

from genwatch import GeneratorReporter
from genwatch._logger import JSONFormatter  # optional

logger = logging.getLogger("genwatch.demo.func")
logger.setLevel(logging.INFO)
h = logging.StreamHandler()
h.setFormatter(JSONFormatter())
logger.addHandler(h)

@GeneratorReporter(logger=logger)
def parse_csv(stream):
    reader = csv.DictReader(stream)
    count = 0
    for row in reader:
        _ = (yield row)  # consume or react to .send(...) if needed
        count += 1
    return count

# usage
sample = io.StringIO("id,name\n1,Ana\n2,Bao\n3,Chirag\n")
g = parse_csv(sample)

for row in g:
    pass

try:
    next(g)
except StopIteration as e:
    assert e.value == 3
```

Expected logs:

```json
{"timestamp": "2025-08-09T01:57:52.100597", "level": "INFO", "filename": "example.py", "msg": "parse_csv"}
{"timestamp": "2025-08-09T01:57:52.101668", "level": "INFO", "filename": "example.py", "msg": {"gi_code": "<code object parse_csv at 0x000001735A6828B0, file \"example.py\", line 4>", "gi_frame": "<frame at 0x000001735A743AC0, file 'example.py', line 9, code parse_csv>", "gi_running": "False", "gi_suspended": "True", "gi_yieldfrom": null}, "lineno": 9}
{"timestamp": "2025-08-09T01:57:52.102694", "level": "INFO", "filename": "example.py", "msg": {"yielded_value": {"id": "1", "name": "Ana"}}, "lineno": 9}
{"timestamp": "2025-08-09T01:57:52.103717", "level": "INFO", "filename": "example.py", "msg": {"value_sent_gen": "No value sent to,  the generator"}, "lineno": 9}
{"timestamp": "2025-08-09T01:57:52.103717", "level": "INFO", "filename": "example.py", "msg": {"gi_code": "<code object parse_csv at 0x000001735A6828B0, file \"example.py\", line 4>", "gi_frame": "<frame at 0x000001735A743AC0, file 'example.py', line 9, code parse_csv>", "gi_running": "False", "gi_suspended": "True", "gi_yieldfrom": null}, "lineno": 9}
{"timestamp": "2025-08-09T01:57:52.104733", "level": "INFO", "filename": "example.py", "msg": {"yielded_value": {"id": "2", "name": "Bao"}}, "lineno": 9}
```

---

### 2) Method — batching records in a service

Yields fixed-size batches; accepts live size changes via `.send(...)`. Returns a small summary dict.

```python
import logging
from itertools import islice
from genwatch import GeneratorReporter
from genwatch._logger import JSONFormatter  # optional

logger = logging.getLogger("genwatch.demo.method")
logger.setLevel(logging.INFO)
h = logging.StreamHandler()
h.setFormatter(JSONFormatter())
logger.addHandler(h)

class BatchService:
    def __init__(self, name: str, *, logger: logging.Logger | None = None):
        self.name = name
        self.logger = logger or logging.getLogger("genwatch.demo.method")

    @GeneratorReporter(logger=logger)  # descriptor binding makes this work on methods
    def batches(self, items, size: int):
        total = 0
        emitted = 0
        it = iter(items)
        while True:
            chunk = list(islice(it, size))
            if not chunk:
                break
            total += len(chunk)
            emitted += 1
            control = (yield chunk)   # .send(int) to change the batch size
            if isinstance(control, int) and control > 0:
                size = control
        return {"batches": emitted, "items": total, "service": self.name}

# usage
svc = BatchService("orders", logger=logger)
g = svc.batches(range(7), size=3)

first = next(g)             # -> [0,1,2]
second = g.send(2)          # -> [3,4]
third = next(g)             # -> [5,6]

try:
    next(g)
except StopIteration as e:
    assert e.value == {"batches": 3, "items": 7, "service": "orders"}
```

Expected logs:

```json
{"timestamp": "2025-08-09T01:46:30.250727", "level": "INFO", "filename": "example.py", "msg": "batches"}
{"timestamp": "2025-08-09T01:46:30.253206", "level": "INFO", "filename": "example.py", "msg": {"gi_code": "<code object batches at 0x0000026597279550, file \"example.py\", line 18>", "gi_frame": "<frame at 0x0000026597272D40, file 'example.py', line 29, code batches>", "gi_running": "False", "gi_suspended": "True", "gi_yieldfrom": null}, "lineno": 29}
{"timestamp": "2025-08-09T01:46:30.254881", "level": "INFO", "filename": "example.py", "msg": {"yielded_value": [0, 1, 2]}, "lineno": 29}
{"timestamp": "2025-08-09T01:46:30.255919", "level": "INFO", "filename": "example.py", "msg": {"value_sent_gen": "Value sent to generator: 2"}, "lineno": 29}
{"timestamp": "2025-08-09T01:46:30.256940", "level": "INFO", "filename": "example.py", "msg": {"gi_code": "<code object batches at 0x0000026597279550, file \"example.py\", line 18>", "gi_frame": "<frame at 0x0000026597272D40, file 'example.py', line 29, code batches>", "gi_running": "False", "gi_suspended": "True", "gi_yieldfrom": null}, "lineno": 29}
```

---

## Logging policy (tailored)

Inside `_ProxyReporter.__iter__` we log only:

- **INFO**
  - Start of iteration (source filename, and line if available).
  - Normal completion with the **returned value** (`StopIteration.value`).

- **ERROR**
  - Only when a non-`StopIteration` exception bubbles out of the generator.
  - The exception is re-raised; behavior is unchanged.


This yields **stable, low-variance logs** that are easy to diff, assert on, and parse in CI.

---

## API

```python
GeneratorReporter(func: Optional[GeneratorFunction] = None, *, logger: Optional[logging.Logger] = None)
```

- Use as a **decorator** on generator functions.
- Accepts an optional `logging.Logger` instance. If omitted, a default logger with a JSON stream handler is used.
- Works on free functions, instance methods, and class methods (via descriptor binding).

### Validation & misuse

- Decorating a non-generator function → `TypeError`.
- Attempting to decorate an existing reporter instance → `TypeError`.

---

## JSON logs

`_logger.JSONFormatter` formats dict-style messages into JSON lines:

```python
# record.msg structure
{
  "filename": "/path/to/file.py",
  "lineno": 42,            # may be omitted if unknown
  "msg": "[genwatch] start <name>"
}
```

Use your own formatter if you prefer; `JSONFormatter` is provided for convenience.

---

## Design notes

- **Decorator** wraps generator functions without modifying bodies.
- **Descriptor** support ensures bound/unbound methods work.
- **Proxy** forwards `__iter__/send/throw/close`, injecting lifecycle logs.
- Light **introspection** (`gi_frame`, `gi_code`) to annotate source info without global traces.

---

## Performance

- INFO-only lifecycle logs are cheap.
- No heavy introspection unless available (`gi_frame`/`gi_code`), and even then minimal fields.
- Works well in hot loops and test harnesses.