<!-- TODO: Go through the readme and enter the information here -->

# AAS HTTP Client

<div align="center">
<!-- change this to your projects logo if you have on.
  If you don't have one it might be worth trying chatgpt dall-e to create one for you...
 -->
<img src="docs/assets/fluid_logo.svg" alt="aas_http_client" width=500 />
</div>

---

[![License: em](https://img.shields.io/badge/license-emSL-%23f8a602?label=License&labelColor=%23992b2e)](LICENSE)
[![CI](https://github.com/fluid40/aas-http-client/actions/workflows/CI.yml/badge.svg?branch=main&cache-bust=1)](https://github.com/fluid40/aas-http-client/actions)
[![PyPI version](https://img.shields.io/pypi/v/aas-http-client.svg)](https://pypi.org/project/aas-http-client/)

A generic HTTP client for communicating with various types of AAS and submodel repository servers. The client works with Python dictionaries for the input and output parameters.
In addition, wrappers are provided that work with various AAS frameworks and use the http client as middleware. 

Currently, wrappers are available for the following frameworks:
- BaSyx Python SDK

## Links

🚀 [Getting Started](docs/getting_started.md)

💻 [Developer Quickstart](docs/dev_guide.md)

👨‍⚕️ [Troubleshooting](docs/troubleshooting.md)

🤖 [Releases](http://github.com/fluid40/aas-http-client/releases)

📦 [Pypi Packages](https://pypi.org/project/aas-http-client/)

📜 [em AG Software License](LICENSE)

## ⚡ Quickstart

```bash
pip install aas-http-client
````

```python
from aas_http_client import create_client_by_url

client = create_client_by_url(
    base_url="http://myaasserver:5043/"
)

print(client.get_shells())
```