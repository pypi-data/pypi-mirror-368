# Fastchat MCP

![alt text](/doc/images/fastchat.png)

<div align = center>

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/pypi/v/fastchat-mcp?color=%2334D058&label=Version)](https://pypi.org/project/fastchat-mcp)
[![Last commit](https://img.shields.io/github/last-commit/rb58853/fastchat-mcp.svg?style=flat)](https://github.com/rb58853/fastchat-mcp/commits)
[![Commit activity](https://img.shields.io/github/commit-activity/m/rb58853/fastchat-mcp)](https://github.com/rb58853/fastchat-mcp/commits)
[![Stars](https://img.shields.io/github/stars/rb58853/fastchat-mcp?style=flat&logo=github)](https://github.com/rb58853/fastchat-mcp/stargazers)
[![Forks](https://img.shields.io/github/forks/rb58853/fastchat-mcp?style=flat&logo=github)](https://github.com/rb58853/fastchat-mcp/network/members)
[![Watchers](https://img.shields.io/github/watchers/rb58853/fastchat-mcp?style=flat&logo=github)](https://github.com/rb58853/fastchat-mcp)
[![Contributors](https://img.shields.io/github/contributors/rb58853/fastchat-mcp)](https://github.com/rb58853/fastchat-mcp/graphs/contributors)

</div>

Python chat client, based on [`"mcp[cli]"`](https://github.com/modelcontextprotocol/python-sdk), for connecting to MCP servers through multiple protocols, specifically designed to work with integrated language models.

## Table of Contents

* [Overview](#overview)
* [Installation](#installation)
* [LLM Implementation](#llm-implementation)
  * [LLM Providers](#llm-providers)
  * [LLM Models](#llm-models)
* [Implemented Transfer Protocols](#implemented-transfer-protocols)
* [System Requirements](#system-requirements)
* [Usage Example](#usage-example)
* [Version History](#version-history)
* [Project Status](#project-status)
* [Flow](./doc/FLOW.md)
* [License](#license)

## Overview

This package provides a Python interface to connect to MCP servers in an easy, intuitive, and configurable way. It features a modular architecture that allows for the seamless addition of new transfer protocols and language models (LLM) providers. Currently, it supports the HTTPStream and Stdio transport protocols for any OpenAI language model, with the capability to expand to more options in the future.

## Installation

To install the MCP client, you can use pip:

```bash
pip install fastchat-mcp
```

## LLM Implementation

### LLM Providers

The client currently supports the following language models:

| Provider | Status | Technical Description |
| ---      | ---    |---                    |
| OpenAI   | Implemented |OpenAI is a leading provider of artificial intelligence-based language models that develop advanced technologies for automatic text processing and generation through models like GPT.|

>🚨 **CONFIGURATION NOTE** Currently, this project only work with `OpenAI` llm provider.

**Default Provider (`OpenAI`):** OpenAI is a leading provider of artificial intelligence-based language models that develop advanced technologies for automatic text processing and generation through models like GPT.

### LLM Models

This project can use any valid OpenAI language model, providing flexibility to choose the model that best fits your specific needs. To explore all available models, their features, and how to use them, it is recommended to consult the official [OpenAI documentation](https://platform.openai.com/docs/models).

To select a model, you should create a chat instance like this:

```python
from fastchat import Fastchat
chat = Fastchat(model="my-openai-model-name", ...)
```

**Default Model (`"gpt-5-nano"`):** GPT-5 Nano is the smallest and fastest version of the GPT-5 family, designed to deliver quick and accurate responses with ultra-low latency. It is optimized for simple tasks and processing large volumes of queries. Its focus is on speed and low cost, making it ideal for personal assistants, rapid translation, and lightweight applications, while maintaining basic reasoning capabilities and reliable text generation.

## Implemented Transfer Protocols

Protocols for communication with MCP servers:

| Protocol | Status | Technical Characteristics |
| --- | --- | --- |
| stdio | Implemented | Standard input/output interface that facilitates direct communication between processes.|
| HTTPStream | Implemented | Asynchronous HTTP-based protocol that enables continuous data streaming.|
| SSE (Server-Sent Events) | Not Implemented | Unidirectional protocol that allows the server to send multiple updated events through a single HTTP connection.|

>🚨 **CRITICAL CONFIGURATION NOTE** Currently, this project don't work with `SSE (Server-Sent Events)` protocol.

## System Requirements

### Environmental Configuration

* **`.env` file**: The `.env` file contains the authentication credentials necessary for integration with external services. This file must be created in the project root directory with the following format:

    ```env
    # .env
    
    #CRIPTOGRAFY_KEY by token data storage (OAuth2)
    CRIPTOGRAFY_KEY=<any-criptografy-key>

    # OpenAI Authentication
    OPENAI_API_KEY=<your-openai-key>
    ```

* **`fastchat.config.json` file**: The `fastchat.config.json` file defines the configuration of available MCP servers. It must be created in the project root directory with this [structure](#file-fastchatconfigjson)

### Dependencies

* `Python = ">=3.11"`
* `openai = "^1.68.2"`
* `mcp[cli]`
* `mcp-oauth`

## File `fastchat.config.json`

This file defines the **configuration of available MCP servers** (Model Context Protocol) in the project.
It must be placed in the root directory of the repository. Its main purpose is to inform the application which servers can be used and how to connect to them.

### General Structure

The file is JSON formatted and follows this main structure:

```json
{
    "app_name": "fastchat-mcp",
    "mcp_servers": {
    "..."
    }
}
```

* **`app_name`**: The identifiable name of the appslication or project using these MCP servers.
* **`mcp_servers`**: An object listing one or more configured MCP servers, each with its unique key.

### Server Definition

Each MCP server inside `"mcp_servers"` has a custom configuration with these common properties:

* **Server key** (e.g., `"example_public_server"`, `"github"`, etc.): internal name identifying this server.
  
* **`protocol`**: Protocol or communication method. It can be:
  * `"httpstream"`: Communication via HTTP streaming.
  * `"stdio"`: Communication based on standard input/output (local command execution).

### Server Configuration Examples

#### 1. Public HTTP Stream Server

```json
"example_public_server": {
    "protocol": "httpstream",
    "httpstream-url": "http://127.0.0.1:8000/public-example-server/mcp",
    "name": "example-public-server",
    "description": "Example public server."
}
```

* **`httpstream-url`**: Base URL where the MCP HTTP streaming server is exposed.
* No authentication required (public access).
* `"name"` and `"description"` provide descriptive labels for users.

#### 2. Private HTTP Stream Server with Authentication

```json
"example_private_mcp": {
    "protocol": "httpstream",
    "httpstream-url": "http://127.0.0.1:8000/private-example-server/mcp",
    "name": "example-private-server",
    "description": "Example private server with oauth required.",
    "auth": {
        "required": true,
        "post_body": {
            "username": "user",
            "password": "password"
        }
    }
}
```

* Adds an `"auth"` object on top of basic config:
  * **`required`**: `true` indicates authentication is needed.
  * **`post_body`**: Data sent for authentication (username and password here).
* Suitable for servers secured with OAuth2.

#### 3. GitHub Server with Authentication Headers

```json
"github": {
    "protocol": "httpstream",
    "httpstream-url": "https://api.githubcopilot.com/mcp",
    "name": "github",
    "description": "This server specializes in github operations.",
    "headers": {
        "Authorization": "Bearer {your-github-access-token}"
    }
}
```

* Uses a custom HTTP header `"Authorization"` for token-based authentication.
* Perfect for sending API keys or tokens in headers to access the server.

#### 4. Local Server using STDIO protocol

```json
"my-stdio-server": {
    "protocol": "stdio",
    "name": "my-stdio-server",
    "config": {
        "command": "npx",
        "args": [
            "-y",
            "@modelcontextprotocol/example-stdio-server"
        ]
    }
}
```

* Does not use HTTP; communication happens by executing local commands.
* `"config"` specifies the command and arguments to run the MCP server. This key value(or body) has the same Claude Desktop sintaxis.
* Useful for local integrations or development testing without networking.

### Notes

[see config.example.json](config.example.json)

> ⚠️ Place this file in the **project root** so the application can detect it automatically.
>
>💡 If you need an httpstream MCP server to test the code, you can use [simple-mcp-server](https://github.com/rb58853/simple-mcp-server).
>
> ✍️ If you need help configuring a specific server or using this configuration in your code, feel free to open discussion for help!

---

## Usage Example

```python
#example1.py
from fastchat import TerminalChat
chat = TerminalChat()
chat.open()
```

<https://github.com/user-attachments/assets/1fcb0db8-5798-4745-8711-4b93198e36cc>

```python
#example2.py
from fastchat import Fastchat
import asyncio

async def chating():
    chat: Fastchat = Fastchat()
    await chat.initialize()
    while True:
        query = input("> ")
        if query == "":
            break
        async for step in chat(query):
            print(f"<< {step.json}")
            
asyncio.run(chating())  
```

Alternatively, you may test this service using the following [template available on GitHub](https://github.com/rb58853/template-fastchat-mcp):

```shell
# clone repo
git clone https://github.com/rb58853/template-fastchat-mcp.git
# change to project dir
cd template-fastchat-mcp
# install dependencies
pip install -r requirements.txt
# open in vscode
code .
```

## Version History

### Last Version Features

* 💬 Fully functional streaming chat by passing a query; see [`Fastchat`](./src/fastchat/services/llm/chat/chat.py).
* ⚙️ Integration with `Tools`, `Resources`, and `Prompts` from MCP servers, achieving a well-integrated client workflow with each of these services. [Check flow](./doc/FLOW.md)
* 🔐 Simple authentication system using [mcp-oauth](https://github.com/rb58853/mcp-oauth) and [this environmental configuration](#2-private-http-stream-server-with-authentication). Also integrate [headers authorization](#3-github-server-with-authentication-headers).
* 👾 OpenAI GPT as an integrated LLM using any valid OpenAI language model.
* 📡 Support for the httpstream transport protocol.
* 📟 Support for the stdio transport protocol.
* 💻 Easy console usage via [`open_local_chat()`](./src/fastchat/dev.py); see [example1](#usage-example) for the use case.

[See more in changelog](./doc//CHANGELOG.md)

## Project Status
>
>⚠️ **Important Notice:** This project is currently in active development phase. As a result, errors or unexpected behaviors may occur during usage.
>
> Future versions are expected to include additional features such as voice systems, quick integrations with databases, built-in websocket support for frontend connections, among other useful functionalities. We invite you to **follow this repository (watch)** to stay updated on the latest news and improvements implemented.

## License

MIT License. See [`license`](LICENSE)

---
<div align = center>

#### If you find this project helpful, please don’t forget to ⭐ star the [repository](https://github.com/rb58853/fastchat-mcp)

</div>

<!-- or [buy me a ☕ coffee](buymeacoffee.com/rb58853).** -->
