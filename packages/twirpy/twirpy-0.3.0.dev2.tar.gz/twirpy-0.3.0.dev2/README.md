# Twirpy

> Twirp is a framework for service-to-service communication emphasizing simplicity and minimalism.
> It generates routing and serialization from API definition files and lets you focus on your application's logic
> instead of thinking about folderol like HTTP methods and paths and JSON.
>
> -- <cite>[Twirp's README](https://github.com/twitchtv/twirp/blob/main/README.md)</cite>

Twirpy is a Python implementation of the Twirp framework.
It currently supports [Twirp Wire Protocol v7](https://twitchtv.github.io/twirp/docs/spec_v7.html).

This repository contains:
* a protoc (aka the Protocol Compiler) plugin that generates sever and client code;
* a Python package with common implementation details.

## Installation

### Runtime Library

The runtime library package contains common types like `TwirpServer` and `TwirpClient` that are used by the generated code.

Add the Twirp package to your Python project with:
```
pip install twirpy
```

### Code Generator

You need to install `protoc`, the Protocol Buffers compiler, and the `protoc-gen-twirpy` protoc plugin to generate code.

First, install the [Protocol Buffers](https://developers.google.com/protocol-buffers) compiler.
For installation instructions, see [Protocol Buffer Compiler Installation documentation](https://github.com/protocolbuffers/protobuf#protobuf-compiler-installation).
You can also use your package manager (e.g. `brew install protobuf` on macOS).

Go the [releases page](https://github.com/Cryptact/twirpy/releases/latest), and download the `protoc-gen-twirpy` binary for your platform.
Unzip the archive and move the binary to a directory in your PATH.

On macOS, you can use the following commands:
```sh
curl -L -o- \
  https://github.com/Cryptact/twirpy/releases/latest/download/protoc-gen-twirpy-darwin-arm64.tar.gz \
  | tar xz -C ~/.local/bin protoc-gen-twirpy
````

## Generate and run

Use the protoc plugin to generate twirp server and client code.
```sh
protoc --python_out=. --pyi_out=. --twirpy_out=. example/rpc/haberdasher/service.proto
```

For more information on how to generate code, see the [example](example/README.md).

## Development

We use [`hatch`](https://hatch.pypa.io/latest/) to manage the development process.

To open a shell with the development environment, run: `hatch shell`.
To run the linter, run: `hatch fmt --check` or `hatch fmt` to fix the issues.

To run the type checker, run: `hatch run types:check`.

## Standing on the shoulders of giants

- The initial version of twirpy was made from an internal copy of https://github.com/daroot/protoc-gen-twirp_python_srv
- The work done by [Verloop](https://verloop.io/) on [the initial versions of Twirpy](https://github.com/verloop/twirpy).
- The `run_in_threadpool` method comes from https://github.com/encode/starlette
