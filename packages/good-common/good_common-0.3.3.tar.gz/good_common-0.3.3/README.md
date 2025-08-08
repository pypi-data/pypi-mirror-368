# good-common

A small set of common dependencies for Good Kiwi.

# Dependency Provider

BaseProvider is a base class for creating fast_depends (so FastAPI and FastStream compatible) dependency providers.

```python

class APIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get(self, url: str):
        return f"GET {url} with {self.api_key}"

class APIClientProvider(BaseProvider[APIClient], APIClient):
    pass


from fast_depends import inject

@inject
def some_task(
    api_client: APIClient = APIClientProvider(api_key="1234"),
):
    return api_client.get("https://example.com")


```

Can also be used without fast_depends:

```python

client = APIClientProvider(api_key="1234").get()

```

Override `initializer` to customize how the dependency class is initialized.

```python

class APIClientProvider(BaseProvider[APIClient], APIClient):
    def initializer(
        self,
        cls_args: typing.Tuple[typing.Any, ...],  # args passed to the Provider
        cls_kwargs: typing.Dict[str, typing.Any],  # kwargs passed to the Provider
        fn_kwargs: typing.Dict[str, typing.Any],  # kwargs passed to the function at runtime
    ):
        return cls_args, {**cls_kwargs, **fn_kwargs}  # override the api_key with the one passed to the function


@inject
def some_task(
    api_key: str,
    api_client: APIClient = APIClientProvider(),
):
    return api_client.get("https://example.com")


some_task(api_key="5678")

```


# Pipeline

## Overview

The Pipeline library provides a flexible and efficient way to create and execute pipelines of components in Python. It supports both synchronous and asynchronous execution, type checking, parallel processing, and error handling.

## Features

- Create pipelines with multiple components that can accept multiple inputs and produce multiple outputs
- Typed "channels" for passing data between components
- Support for both synchronous and asynchronous components
- Type checking for inputs and outputs using Python type annotations
- Parallel execution of pipeline instances
- Error handling with Result types
- Function mapping for flexible component integration

## Quick Start

```python
from typing import Annotated
from good_common.pipeline import Pipeline, Attribute

def add(a: int, b: int) -> Annotated[int, Attribute("result")]:
    return a + b

def multiply(result: int, factor: int) -> Annotated[int, Attribute("result")]:
    return result * factor

# Create a pipeline
my_pipeline = Pipeline(add, multiply)

# Execute the pipeline
result = await my_pipeline(a=2, b=3, factor=4)
print(result.result)  # Output: 20
```

## Usage

### Creating a Pipeline

Use the `Pipeline` class to create a new pipeline:

```python
from pipeline import Pipeline

my_pipeline = Pipeline(component1, component2, component3)
```

### Defining Components

Components can be synchronous or asynchronous functions:

```python
from typing import Annotated
from pipeline import Attribute

def sync_component(x: int) -> Annotated[int, Attribute("result")]:
    return x + 1

async def async_component(x: int) -> Annotated[int, Attribute("result")]:
    await asyncio.sleep(0.1)
    return x * 2
```

### Executing a Pipeline

Execute a pipeline asynchronously:

```python
result = await my_pipeline(x=5)
print(result.result)
```

### Parallel Execution

Execute a pipeline with multiple inputs in parallel:

```python
inputs = [{"a": 1, "b": 2, "factor": 2}, {"a": 2, "b": 3, "factor": 3}]
results = [result async for result in my_pipeline.execute(*inputs, max_workers=3)]

for result in results:
    if result.is_ok():
        print(result.unwrap().result)
    else:
        print(f"Error: {result.unwrap_err()}")
```

### Error Handling

The pipeline handles errors gracefully in parallel execution:

```python
def faulty_component(x: int) -> Annotated[int, Attribute("result")]:
    if x == 2:
        raise ValueError("Error on purpose!")
    return x + 1

pipeline = Pipeline(faulty_component)
inputs = [{"x": 1}, {"x": 2}, {"x": 3}]
results = [result async for result in pipeline.execute(*inputs)]

for result in results:
    if result.is_ok():
        print(result.unwrap().result)
    else:
        print(f"Error: {result.unwrap_err()}")
```

### Function Mapping

Use `function_mapper` to adjust input parameter names:

```python
from pipeline import function_mapper

def multiply_diff(difference: int, factor: int) -> Annotated[int, Attribute("result")]:
    return difference * factor

pipeline = Pipeline(subtract, function_mapper(multiply_diff, diff="difference"))
```

## Advanced Features

- Mixed synchronous and asynchronous components in a single pipeline
- Custom output types with `Attribute` annotations
- Flexible error handling in both single and parallel executions


# Utilities

Various utility functions for common tasks.

Look at `/tests/good_common/utilities` for usage