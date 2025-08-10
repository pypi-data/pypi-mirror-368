<div align="center">
  <table>
    <tr>
      <td>
        <a href="https://ondewo.com/en/products/natural-language-understanding/">
            <img width="400px" src="https://raw.githubusercontent.com/ondewo/ondewo-logos/master/ondewo_we_automate_your_phone_calls.png"/>
        </a>
      </td>
    </tr>
    <tr>
        <td align="center">
          <a href="https://www.linkedin.com/company/ondewo "><img width="40px" src="https://cdn-icons-png.flaticon.com/512/3536/3536505.png"></a>
          <a href="https://www.facebook.com/ondewo"><img width="40px" src="https://cdn-icons-png.flaticon.com/512/733/733547.png"></a>
          <a href="https://twitter.com/ondewo"><img width="40px" src="https://cdn-icons-png.flaticon.com/512/733/733579.png"> </a>
          <a href="https://www.instagram.com/ondewo.ai/"><img width="40px" src="https://cdn-icons-png.flaticon.com/512/174/174855.png"></a>
        </td>
    </tr>
  </table>
  <h1>
  Ondewo T2S Client Python Library
  </h1>
</div>


This library facilitates the interaction between a user and a CAI server. It achieves this by providing a higher-level interface mediator.

This higher-level interface mediator is structured around a series of python files generated from protobuf files. These protobuf files specify the details of the interface, and can be used to generate code in 10+ high-level languages. They are found in the [ONDEWO T2S API](https://github.com/ondewo/ondewo-t2s-api) along with the older Google protobufs from Dialogueflow that were used at the start. The [ONDEWO PROTO-COMPILER](https://github.com/ondewo/ondewo-proto-compiler) will generate the needed files directly in this library.

## Python Installation

You can install the library by installing it directly from the PyPi:

```bash
pip install ondewo-t2s-client
```

Or, you could clone it and install the requirements:

```bash
git clone git@github.com:ondewo/ondewo-t2s-client-python.git
cd ondewo-t2s-client-python
make setup_developer_environment_locally
```

## Repository Structure

```
.
├── examples
│   ├── configs
│   │   ├── insecure_grpc.json
│   │   └── secure_grpc_placeholder.json
│   ├── example_api.py
│   ├── __init__.py
│   ├── ondewo_t2s_with_certificate.ipynb
│   ├── requirements.txt
│   └── setup.py
├── ondewo
│   ├── t2s
│   │   ├── client
│   │   │   ├── services
│   │   │   │   ├── __init__.py
│   │   │   │   └── text_to_speech.py
│   │   │   ├── client_config.py
│   │   │   ├── client.py
│   │   │   ├── __init__.py
│   │   │   └── services_container.py
│   │   ├── __init__.py
│   │   ├── text_to_speech_pb2_grpc.py
│   │   ├── text_to_speech_pb2.py
│   │   └── text_to_speech_pb2.pyi
│   └── __init__.py
├── ondewo-proto-compiler
├── ondewo-t2s-api
├── CONTRIBUTING.md
├── Dockerfile.utils
├── LICENSE
├── Makefile
├── MANIFEST.in
├── mypy.ini
├── README.md
├── RELEASE.md
├── requirements-dev.txt
├── requirements.txt
├── setup.cfg
├── setup.py
└── temp.txt
```

## Build

The `make build` command is dependent on 2 `repositories` and their speciefied `version`:

- [ondewo-t2s-api](https://github.com/ondewo/ondewo-t2s-api) -- `T2S_API_GIT_BRANCH` in `Makefile`
- [ondewo-proto-compiler](https://github.com/ondewo/ondewo-proto-compiler) -- `ONDEWO_PROTO_COMPILER_GIT_BRANCH` in `Makefile`

It will generate a `_pb2.py`, `_pb2.pyi` and `_pb2_grpc.py` file for every `.proto` in the api submodule.

> :warning: All Files in the `ondewo` folder that dont have `pb2` in their name are handwritten, and therefor need to be manually adjusted to any changes in the proto-code.

## Examples

The `/examples` folder provides a possible implementation of this library. To run an example, simple execute it like any other python file. To specify the server and credentials, you need to provide an environment file with the following variables:

- host `// The hostname of the Server - e.g. 127.0.0.1`
- port `// Port of the Server - e.g. 6600`
- user_name `// Username - same as you would use in AIM`
- password `// Password of the user`
- http_token `// Token to allow access through`
- grpc_cert `// gRPC Certificate of the server`

## Automatic Release Process

The entire process is automated to make development easier. The actual steps are simple:

TODO after Pull Request was merged in:

- Checkout master:
  ```shell
  git checkout master
  ```
- Pull the new stuff:
  ```shell
  git pull
  ```
- (If not already, run the `setup_developer_environment_locally` command):
  ```shell
  make setup_developer_environment_locally
  ```
- Update the `ONDEWO_T2S_VERSION` in the `Makefile`
- Add the new Release Notes in `RELEASE.md` in the format:

  ```
  ## Release ONDEWO T2S Python Client X.X.X       <---- Beginning of Notes

     ...<NOTES>...

  *****************                      <---- End of Notes
  ```

- Release:
  ```shell
  make ondewo_release
  ```

---

The release process can be divided into 6 Steps:

1. `build` specified version of the `ondewo-t2s-api`
2. `commit and push` all changes in code resulting from the `build`
3. Create and push the `release branch` e.g. `release/1.3.20`
4. Create and push the `release tag` e.g. `1.3.20`
5. Create a new `Release` on GitHub
6. Publish the built `dist` folder to `pypi.org`

> :warning: The Release Automation checks if the build has created all the proto-code files, but it does not check the code-integrity. Please build and test the generated code prior to starting the release process.
