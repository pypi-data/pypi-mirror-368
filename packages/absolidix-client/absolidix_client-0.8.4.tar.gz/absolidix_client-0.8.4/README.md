# Absolidix API client

[![DOI](https://zenodo.org/badge/563802198.svg)](https://doi.org/10.5281/zenodo.7693569)
[![PyPI](https://img.shields.io/pypi/v/absolidix_client.svg?style=flat)](https://pypi.org/project/absolidix-client)

This library allows for programmatic interactions with the Absolidix infrastructure.

## Installation

`pip install absolidix_client`

## Usage

There are two client flavors: **asyncronous** `asyncio` client
and simplified **synchronous** client.

### Asynchronous client

An asynchronous client is `AbsolidixAPIAsync`. Example of usage:

```python
from absolidix_client import AbsolidixAPIAsync, AbsolidixTokenAuth

async def main():
    async with AbsolidixAPIAsync(API_URL, auth=AbsolidixTokenAuth("VERY_SECRET_TOKEN")) as client:
        print(await client.v0.auth.whoami())
        data = await client.v0.datasources.create(content, name)
        results = await client.v0.calculations.create_get_results(data["id"])
        print(resuls)
```

See `examples` directory for more examples.

### Synchronous client

A synchronous client is `AbsolidixAPI`. Example of usage:

```python
from absolidix_client import AbsolidixAPI, AbsolidixTokenAuth

client = AbsolidixAPI(API_URL, auth=AbsolidixTokenAuth("VERY_SECRET_TOKEN"), timeout=5)
data = client.v0.datasources.create(content, name)
results = client.v0.calculations.create_get_results(data["id"], timeout=False)
print(results)
```

NB in development one can replace a `VERY_SECRET_TOKEN` string with the development user email, e.g.
`admin@test.com` (refer to **users_emails** BFF table).

## Contributing

Please give a minute to the [contribution guide](./CONTRIBUTING.md).

## License

Author Sergey Korolev, Tilde Materials Informatics

Copyright 2024-2025 Tilde Materials Informatics

Copyright 2023-2024 BASF SE

BSD 3-Clause
