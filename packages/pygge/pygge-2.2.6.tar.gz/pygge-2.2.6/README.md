# pygge

## Introduction

`pygge` is a python library to interact with the Goodgame Empire API

## Installation

To install `pygge`, you can use pip:

```bash
pip install pygge
```

Alternatively, you can install it directly from the source:

```bash
git clone https://github.com/yourusername/pygge.git
cd pygge
python setup.py install
```

## Usage

Here is a simple example to get you started:

```python
from threading import Thread
from pygge.gge_socket import GgeSocket

socket = GgeSocket("<server_url>", "<server_header>")
Thread(target=socket.run_forever, daemon=True).start()
Thread(target=socket.keep_alive, daemon=True).start()
socket.init_socket()
socket.login("<username>", "<password>")

response = socket.get_account_infos()
print(response["payload"]["data"])
```
