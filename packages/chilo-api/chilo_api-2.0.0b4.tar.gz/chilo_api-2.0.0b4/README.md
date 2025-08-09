# Chilo

<p align="center">
  <a href="https://chiloproject.io"><img src="https://raw.githubusercontent.com/dual/chilo-docs/main/img/logo-no-bg.png" alt="Chilo"></a>
</p>
<p align="center">
    <em>Chilo is a lightweight, form-meets-function, opinionated (yet highly configurable) api framework</em>
</p>

[![CircleCI](https://circleci.com/gh/dual/chilo.svg?style=shield)](https://circleci.com/gh/syngenta/acai-python)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=dual_chilo&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=dual_chilo)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=dual_chilo&metric=coverage)](https://sonarcloud.io/summary/new_code?id=dual_chilo)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=dual_chilo&metric=bugs)](https://sonarcloud.io/summary/new_code?id=dual_chilo)
[![pypi package](https://img.shields.io/pypi/v/chilo-api?color=%2334D058&label=pypi%20package)](https://pypi.org/project/chilo-api/)
[![python](https://img.shields.io/pypi/pyversions/chilo-api.svg?color=%2334D058)](https://pypi.org/project/chilo-api)
[![Inline docs](https://inch-ci.org/github/dwyl/hapi-auth-jwt2.svg?branch=master)](https://chiloproject.io)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/dwyl/esta/issues)

Chilo, short for chilorhinophis (meaning two headed snake), is a lightweight, form-meets-function, opinionated (yet highly configurable) api framework.

## Benefits

* No route definitions needed; route based on your directory structure
* Built-in OpenAPI request and response validation
* Built-in GRPC support
* Generate OpenAPI spec from code base
* Ease of use with gunicorn
* Infinitely customizable with middleware extensions

## Philosophy

The Chilo philosophy is to provide a dry, configurable, declarative framework, which encourages Happy Path Programming (HPP).

Happy Path Programming is a development approach where all inputs are validated up front, allowing the main logic to proceed without interruption. This avoids deeply nested conditionals, scattered try/catch blocks, and the clutter of mid-flow exception handling. Chilo provides a flexible middleware system that lets developers define what counts as valid input—keeping the code focused, readable, and on the "happy path" where things work as expected.

## Documentation & Examples

* [Full Docs](https://chiloproject.io)
* [Examples](https://github.com/dual/chilo-docs/tree/main/examples)
* Tutorial (coming soon)

## Quick Start (REST)

### 0. Install

```bash
$ pip install chilo_api
# pipenv install chilo_api
# poetry add chilo_api
```

### 1. Create `main.py` for REST

```python
from chilo_api import Chilo


api = Chilo(
    base_path='/',
    handlers='api/handlers',
)
```

### 2. Create First Handler

`{PWD}/api/handlers/__init__.py`

```python
from chilo_api import Request, Response

def get(request: Request, response:Response ) -> Response:
    response.body = {'hello': 'world'}
    return response
```

### 3. Run your API

```bash
python -m chilo_api serve --api=main --reload=true
```

### 4. Checkout your API

[http://127.0.0.1:3000/](http://127.0.0.1:3000/)

### 5. Validate Your Endpoint (optional)

```python
from chilo_api import requirements


@requirements(required_params=['greeting'])
def get(request, response):
    response.body = {'hello': request.query_params['greeting']}
    return response
```

### 6. Checkout your API (again)

[http://127.0.0.1:3000/?greeting=developer](http://127.0.0.1:3000/?greeting=developer)

## Quick Start (GRPC)

### 1. Create `main_grpc.py` for GRPC

```python
from chilo_api import Chilo


api = Chilo(
    api_type='grpc',
    handlers='api/handlers',
    protobufs='api/protobufs',
    reflection=True,
    port=50051
)
```

#### 2. Create Your Protobuff files

```protobuf
syntax = "proto3";

package calculator;

service Calculator {
    rpc Add(CalcRequest) returns (CalcResponse);
    rpc Subtract(CalcRequest) returns (CalcResponse);
    rpc Multiply(CalcRequest) returns (CalcResponse);
    rpc Divide(CalcRequest) returns (CalcResponse);
}

message CalcRequest {
    double num1 = 1;
    double num2 = 2;
}

message CalcResponse {
    double result = 1;
}
```

#### 3. Create First GRPC Handlers

`{PWD}/api/handlers/__init__.py`

```python
from chilo_api import requirements, Request, Response

@requirements(
    protobuf='calculator.proto',
    service='Calculator',
    rpc='Add'
)
def add(request: Request, response: Response) -> Response:
    num1 = request.body.get('num1', 0)
    num2 = request.body.get('num2', 0)
    result = num1 + num2
    response.body = {'result': result}
    return response
```

### 4. Run your GRPC API

```bash
python -m chilo_api serve --api=main_grpc
```

### 5. Checkout your GRPC API

[http://127.0.0.1:50051/](http://127.0.0.1:50051/)
